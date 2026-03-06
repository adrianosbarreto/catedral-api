from flask import jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.api import api
from app.models import db, Membro, User, AulaLideranca, FrequenciaAulaLideranca, Ide, Celula
from datetime import datetime, timedelta
import math

def calculate_distance(lat1, lon1, lat2, lon2):
    """Calcula a distância em metros entre dois pontos usando a fórmula de Haversine"""
    if not all([lat1, lon1, lat2, lon2]):
        return float('inf')
    
    R = 6371000  # Raio da Terra em metros
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)

    a = math.sin(delta_phi / 2)**2 + \
        math.cos(phi1) * math.cos(phi2) * \
        math.sin(delta_lambda / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    return R * c

@api.route('/lideranca/aulas', methods=['GET'])
@jwt_required()
def get_aulas_lideranca():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    if not user:
        return jsonify({'error': 'Usuário não encontrado'}), 404

    # Filtra aulas ativas. Se a aula for vinculada a uma IDE específica, 
    # apenas membros daquela IDE (ou admins) vêem.
    query = AulaLideranca.query.filter_by(ativa=True)
    
    if user.role != 'admin' and user.membro and user.membro.ide_id:
        query = query.filter((AulaLideranca.ide_id == user.membro.ide_id) | (AulaLideranca.ide_id == None))
    
    aulas = query.order_by(AulaLideranca.data_hora.desc()).all()
    
    resultado = []
    for a in aulas:
        d = a.to_dict()
        # Verifica se o usuário atual (membro) já tem presença registrada nesta aula
        if user.membro_id:
            frequencia = FrequenciaAulaLideranca.query.filter_by(aula_id=a.id, membro_id=user.membro_id).first()
            d['presente'] = frequencia.presente if frequencia else False
        else:
            d['presente'] = False
        resultado.append(d)

    return jsonify(resultado)

@api.route('/lideranca/aulas/datas', methods=['GET'])
@jwt_required()
def get_aulas_datas():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    
    query = db.session.query(db.func.date(AulaLideranca.data_hora)).filter(AulaLideranca.ativa == True)
    
    if user.role != 'admin' and user.membro and user.membro.ide_id:
        query = query.filter((AulaLideranca.ide_id == user.membro.ide_id) | (AulaLideranca.ide_id == None))
    
    datas = query.distinct().all()
    # Converte de [('2026-03-05',), ...] para ['2026-03-05', ...]
    return jsonify([str(d[0]) for d in datas])

@api.route('/lideranca/aulas', methods=['POST'])
@jwt_required()
def create_aula_lideranca():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    if user.role not in ['admin', 'pastor', 'pastor_de_rede']:
        return jsonify({'error': 'Sem permissão'}), 403

    data = request.json
    try:
        data_hora = datetime.fromisoformat(data['data_hora'].replace('Z', ''))
        data_hora_fim = None
        if data.get('data_hora_fim'):
            data_hora_fim = datetime.fromisoformat(data['data_hora_fim'].replace('Z', ''))
        
        # Automação de IDE: Se for pastor/supervisor e o tipo for IDE, usa a IDE dele
        # apenas Admin pode setar IDE de outros explicitamente
        final_ide_id = data.get('ide_id')
        if not final_ide_id and user.role != 'admin' and user.membro:
            final_ide_id = user.membro.ide_id

        nova_aula = AulaLideranca(
            titulo=data['titulo'],
            descricao=data.get('descricao'),
            data_hora=data_hora,
            data_hora_fim=data_hora_fim,
            local_nome=data.get('local_nome'),
            latitude=data.get('latitude'),
            longitude=data.get('longitude'),
            raio_checkin=data.get('raio_checkin', 100),
            ide_id=final_ide_id
        )
        db.session.add(nova_aula)
        db.session.flush() # Para pegar o id da nova_aula

        # Pré-popular frequências
        query_membros = Membro.query.filter_by(ativo=True)
        if nova_aula.ide_id:
            query_membros = query_membros.filter_by(ide_id=nova_aula.ide_id)
        
        membros = query_membros.all()
        for membro in membros:
            f = FrequenciaAulaLideranca(
                aula_id=nova_aula.id,
                membro_id=membro.id,
                presente=False,
                metodo='manual'
            )
            db.session.add(f)

        db.session.commit()
        return jsonify(nova_aula.to_dict()), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@api.route('/lideranca/subordinados', methods=['GET'])
@jwt_required()
def get_subordinados_lideranca():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    if not user or not user.membro:
        return jsonify({'error': 'Membro não encontrado'}), 404

    role = user.role
    membro_id = user.membro_id
    ide_id = user.membro.ide_id

    subordinados = []

    if role == 'admin':
        subordinados = Membro.query.filter_by(ativo=True).order_by(Membro.nome).all()
    elif role == 'pastor':
        # Pastor vê todos da sua IDE
        subordinados = Membro.query.filter_by(ide_id=ide_id, ativo=True).order_by(Membro.nome).all()
    elif role == 'pastor_de_rede':
        # Pastor de Rede vê todos da sua IDE ou IDEs que lidera
        my_ide_ids = [ide.id for ide in user.membro.ides_lideradas.all()]
        if not my_ide_ids:
            subordinados = Membro.query.filter_by(ide_id=ide_id, ativo=True).all()
        else:
            subordinados = Membro.query.filter(Membro.ide_id.in_(my_ide_ids), Membro.ativo==True).all()
    elif role == 'supervisor':
        # Supervisor vê seus líderes e os membros das células desses líderes
        # Além de pessoas que o tenham diretamente como supervisor
        leaders = Membro.query.filter_by(supervisor_id=membro_id, ativo=True).all()
        leader_ids = [l.id for l in leaders]
        
        # Membros diretamente supervisionados ou em células supervisionadas
        from app.models import MembroNucleo, Nucleo, Celula
        celula_subquery = db.session.query(MembroNucleo.membro_id).join(Nucleo).join(Celula).filter(Celula.supervisor_id == membro_id)
        
        subordinados = Membro.query.filter((Membro.supervisor_id == membro_id) | (Membro.id.in_(celula_subquery))).filter(Membro.ativo==True).all()
                
    elif role in ['lider', 'lider_de_celula', 'vice_lider_de_celula']:
        # Líder vê os membros da sua célula
        subordinados = Membro.query.filter_by(lider_id=membro_id, ativo=True).all()

    return jsonify([{'id': s.id, 'nome': s.nome, 'papel': s.user.role if s.user else 'membro'} for s in subordinados])

@api.route('/lideranca/frequencia/manual', methods=['POST'])
@jwt_required()
def save_frequencia_manual():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    if user.role not in ['admin', 'pastor', 'pastor_de_rede', 'supervisor', 'lider', 'lider_de_celula', 'vice_lider_de_celula']:
        return jsonify({'error': 'Sem permissão'}), 403

    data = request.json
    aula_id = data.get('aula_id')
    membro_id = data.get('membro_id')
    presente = data.get('presente', True)

    if not aula_id or not membro_id:
        return jsonify({'error': 'Dados incompletos'}), 400

    frequencia = FrequenciaAulaLideranca.query.filter_by(aula_id=aula_id, membro_id=membro_id).first()
    
    if frequencia:
        frequencia.presente = presente
        frequencia.metodo = 'manual'
        frequencia.data_registro = datetime.now()
    else:
        frequencia = FrequenciaAulaLideranca(
            aula_id=aula_id,
            membro_id=membro_id,
            presente=presente,
            metodo='manual'
        )
        db.session.add(frequencia)

    db.session.commit()
    return jsonify({'message': 'Frequência salva com sucesso'})

@api.route('/lideranca/frequencia/checkin', methods=['POST'])
@jwt_required()
def checkin_lideranca():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    if not user:
        return jsonify({'error': 'Usuário não encontrado'}), 404

    # Regra: Precisa ser um membro vinculado para registrar presença
    # Exceção: Se for Admin sem membro, vamos permitir o teste vinculando ao primeiro membro Admin encontrado
    # ou lançar erro se realmente não houver perfil.
    if not user.membro:
        if user.role == 'admin':
            from app.models import Membro
            membro_admin = Membro.query.filter_by(nome='Administrador').first()
            if membro_admin:
                user.membro_id = membro_admin.id
                db.session.commit()
            else:
                return jsonify({'error': 'Perfil de membro administrador não encontrado e usuário sem vínculo'}), 404
        else:
            return jsonify({'error': 'Perfil de membro não encontrado'}), 404

    data = request.json
    aula_id = data.get('aula_id')
    lat = data.get('latitude')
    lon = data.get('longitude')

    aula = AulaLideranca.query.get(aula_id)
    if not aula or not aula.ativa:
        return jsonify({'error': 'Aula não encontrada ou inativa'}), 404

    # 1. Validar Janela de Horário
    agora = datetime.now()
    # Início: 1 hora antes do marcado
    inicio_valido = aula.data_hora - timedelta(hours=1)
    
    # Fim: 6 horas de tolerância após o fim da aula (ou 8h após início se não houver fim)
    if aula.data_hora_fim:
        fim_valido = aula.data_hora_fim + timedelta(hours=6)
    else:
        fim_valido = aula.data_hora + timedelta(hours=8)

    if agora < inicio_valido or agora > fim_valido:
        msg = f'Fora do horário permitido. Check-in disponível entre {inicio_valido.strftime("%H:%M")} e {fim_valido.strftime("%H:%M")}'
        return jsonify({'error': msg}), 400

    # 2. Validar Geolocalização se a aula tiver coordenadas
    if aula.latitude and aula.longitude:
        if not lat or not lon:
            return jsonify({'error': 'Localização necessária para esta aula'}), 400
        
        distancia = calculate_distance(lat, lon, aula.latitude, aula.longitude)
        if distancia > aula.raio_checkin:
            return jsonify({'error': f'Você está muito longe do local ({int(distancia)}m)'}), 400

    # 3. Registrar Presença
    frequencia = FrequenciaAulaLideranca.query.filter_by(aula_id=aula_id, membro_id=user.membro_id).first()
    if frequencia and frequencia.presente:
        return jsonify({'message': 'Presença já registrada'}), 200

    if frequencia:
        frequencia.presente = True
        frequencia.metodo = 'checkin'
        frequencia.data_registro = datetime.now()
    else:
        frequencia = FrequenciaAulaLideranca(
            aula_id=aula_id,
            membro_id=user.membro_id,
            presente=True,
            metodo='checkin'
        )
        db.session.add(frequencia)

    db.session.commit()
    return jsonify({'message': 'Check-in realizado com sucesso!'})

@api.route('/lideranca/aulas/<int:aula_id>/frequencias', methods=['GET'])
@jwt_required()
def get_frequencias_aula(aula_id):
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 50, type=int)
    nome = request.args.get('nome', '')
    ide_id = request.args.get('ide_id', type=int)

    query = FrequenciaAulaLideranca.query.filter_by(aula_id=aula_id)

    if nome or ide_id:
        query = query.join(Membro)
        if nome:
            query = query.filter(Membro.nome.ilike(f'%{nome}%'))
        if ide_id:
            query = query.filter(Membro.ide_id == ide_id)
    else:
        # Ordenação padrão por nome do membro se não houver filtro (precisa do join)
        query = query.join(Membro).order_by(Membro.nome)

    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    
    return jsonify({
        'frequencias': [f.to_dict() for f in pagination.items],
        'total': pagination.total,
        'pages': pagination.pages,
        'current_page': page
    })
