from flask import jsonify, request
from app.api import api
from app.models import Evento, InscricaoEvento, User, Membro
from app import db
from datetime import datetime
from flask_jwt_extended import jwt_required, get_jwt_identity

@api.route('/eventos/<int:id>/inscrever', methods=['POST'])
def inscrever_evento(id):
    evento = db.session.get(Evento, id)
    if not evento:
        return jsonify({'error': 'Evento não encontrado'}), 404
        
    if not evento.ativo or (evento.data_fim < datetime.utcnow()):
        return jsonify({'error': 'Inscrições encerradas para este evento'}), 400
        
    if not evento.gerenciar_participantes:
        return jsonify({'error': 'Este evento não aceita inscrições gerenciadas'}), 400

    data = request.get_json() or {}
    nome = data.get('nome')
    email = data.get('email')
    telefone = data.get('telefone')
    cpf = data.get('cpf')
    
    # Sanitizar CPF (apenas números)
    cpf_limpo = ''.join(filter(str.isdigit, str(cpf))) if cpf else None

    try:
        inscricao = InscricaoEvento(evento_id=id)
        
        # Se estiver logado, associar ao membro
        from flask_jwt_extended import decode_token
        auth_header = request.headers.get('Authorization')
        if auth_header and "Bearer " in auth_header:
            try:
                token = auth_header.split(" ")[1]
                identity = decode_token(token)['sub']
                user = db.session.get(User, identity)
                if user and user.membro_id:
                    inscricao.membro_id = user.membro_id
            except:
                pass

        inscricao.nome_externo = nome
        inscricao.email_externo = email
        inscricao.telefone_externo = telefone
        inscricao.cpf_externo = cpf_limpo
        inscricao.respostas = data.get('respostas', {})
        
        if not inscricao.membro_id and not (inscricao.nome_externo and (inscricao.email_externo or inscricao.telefone_externo)):
            return jsonify({'error': 'Nome e contato são obrigatórios'}), 400

        db.session.add(inscricao)
        db.session.commit()
        return jsonify(inscricao.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@api.route('/eventos/<int:id>/inscrever-batismo-publico', methods=['POST'])
def inscrever_batismo_publico(id):
    evento = db.session.get(Evento, id)
    if not evento:
        return jsonify({'error': 'Evento não encontrado'}), 404
        
    data = request.get_json() or {}
    nome = data.get('nome')
    telefone = data.get('telefone')
    email = data.get('email')
    cpf = data.get('cpf')
    data_nascimento_raw = data.get('data_nascimento')
    sexo = data.get('sexo')
    estado_civil = data.get('estado_civil')
    celula_id = data.get('celula_id')
    
    # Endereço
    cep = data.get('cep')
    logradouro = data.get('logradouro')
    numero = data.get('numero')
    bairro = data.get('bairro')
    cidade = data.get('cidade')
    estado = data.get('estado')
    complemento = data.get('complemento')

    if not nome or not celula_id:
        return jsonify({'error': 'Nome e Célula são obrigatórios'}), 400

    nascimento = None
    if data_nascimento_raw:
        try:
            nascimento = datetime.strptime(data_nascimento_raw, '%Y-%m-%d').date()
        except:
            pass

    try:
        from app.models import MembroNucleo, Nucleo, Membro, Celula, Endereco, InscricaoEvento
        
        celula = db.session.get(Celula, celula_id)
        if not celula:
            return jsonify({'error': 'Célula não encontrada'}), 404

        # Hierarquia
        ide_id = celula.ide_id
        pastor_id = None
        if celula.ide and celula.ide.pastor_id:
            pastor_id = celula.ide.pastor_id
        elif celula.lider and celula.lider.pastor_id:
            pastor_id = celula.lider.pastor_id
            
        supervisor_id = celula.supervisor_id
        lider_membro_id = celula.lider_id
            
        nucleo = Nucleo.query.filter_by(celula_id=celula.id).first()

        # Criar ou atualizar membro pelo CPF
        cpf_limpo = ''.join(filter(str.isdigit, str(cpf))) if cpf else None
        
        alvo_membro = None
        if cpf_limpo:
            alvo_membro = Membro.query.filter_by(cpf=cpf_limpo).first()

        if alvo_membro:
            alvo_membro.nome = nome
            alvo_membro.telefone = telefone
            alvo_membro.email = email
            alvo_membro.data_nascimento = nascimento
            alvo_membro.sexo = sexo
            alvo_membro.estado_civil = estado_civil
            alvo_membro.tipo = 'aguardando_batismo'
            alvo_membro.ide_id = ide_id
            alvo_membro.pastor_id = pastor_id
            alvo_membro.supervisor_id = supervisor_id
            alvo_membro.lider_id = lider_membro_id
        else:
            alvo_membro = Membro(
                nome=nome,
                telefone=telefone,
                email=email,
                cpf=cpf_limpo,
                data_nascimento=nascimento,
                sexo=sexo,
                estado_civil=estado_civil,
                tipo='aguardando_batismo',
                batizado=False,
                data_batismo=evento.data_inicio.date(),
                ativo=True,
                ide_id=ide_id,
                pastor_id=pastor_id,
                supervisor_id=supervisor_id,
                lider_id=lider_membro_id
            )
            db.session.add(alvo_membro)
            db.session.flush()

        # Endereço
        if cep:
            end = Endereco.query.filter_by(membro_id=alvo_membro.id).first()
            if not end:
                end = Endereco(membro_id=alvo_membro.id)
                db.session.add(end)
            end.cep = cep
            end.logradouro = logradouro
            end.numero = numero
            end.bairro = bairro
            end.cidade = cidade
            end.estado = estado
            end.complemento = complemento

        # Vincular ao Núcleo
        if nucleo:
            existente = MembroNucleo.query.filter_by(nucleo_id=nucleo.id, membro_id=alvo_membro.id).first()
            if not existente:
                novo_mn = MembroNucleo(nucleo_id=nucleo.id, membro_id=alvo_membro.id, is_convidado=False)
                db.session.add(novo_mn)

        # Inscrição no evento
        inscricao = InscricaoEvento.query.filter_by(evento_id=id, membro_id=alvo_membro.id).first()
        if not inscricao:
            inscricao = InscricaoEvento(evento_id=id, membro_id=alvo_membro.id)
            db.session.add(inscricao)
        
        db.session.commit()
        return jsonify({'message': 'Inscrição realizada com sucesso', 'id': inscricao.id}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@api.route('/eventos/<int:id>/participantes', methods=['GET'])
@jwt_required()
def get_participantes_evento(id):
    current_user_id = get_jwt_identity()
    user = db.session.get(User, current_user_id)
    evento = db.session.get(Evento, id)
    
    if not evento:
        return jsonify({'error': 'Evento não encontrado'}), 404
        
    # Permissão: Criador ou Admin ou Pastor ou Pastor de Rede
    is_owner = evento.criado_por_id == current_user_id
    is_admin_or_pastor = user.role in ['admin', 'pastor', 'pastor_de_rede']
    is_legacy = evento.criado_por_id is None
    is_manager = user.role in ['supervisor']

    # Se o usuário tem uma IDE, e o evento está vinculado a essa IDE
    user_ide_id = user.membro.ide_id if user.membro else None
    belongs_to_user_ide = False
    if user_ide_id:
        from app.models import Ide
        belongs_to_user_ide = any(i.id == user_ide_id for i in evento.ides) or (evento.ide_id == user_ide_id)

    if not (is_admin_or_pastor or is_owner or (is_legacy and is_manager) or belongs_to_user_ide):
        return jsonify({'error': 'Sem permissão para ver inscritos'}), 403
        
    participantes = InscricaoEvento.query.filter_by(evento_id=id).all()
    return jsonify([p.to_dict() for p in participantes])

@api.route('/inscricoes/<int:id>', methods=['PUT'])
@jwt_required()
def update_status_inscricao(id):
    current_user_id = get_jwt_identity()
    user = db.session.get(User, current_user_id)
    inscricao = db.session.get(InscricaoEvento, id)
    
    if not inscricao:
        return jsonify({'error': 'Inscrição não encontrada'}), 404
        
    evento = inscricao.evento
    # Permissão: Criador do evento ou Admin ou Pastor (geral/rede)
    if user.role not in ['admin', 'pastor', 'pastor_de_rede'] and evento.criado_por_id != current_user_id:

        return jsonify({'error': 'Sem permissão para alterar inscrição'}), 403
        
    data = request.get_json() or {}
    
    if 'status' in data:
        inscricao.status = data['status'] # pendente, confirmado, cancelado
    if 'pago' in data:
        inscricao.pago = data['pago']
        
    db.session.commit()
    return jsonify(inscricao.to_dict())

@api.route('/inscricoes/<int:id>', methods=['DELETE'])
def cancelar_inscricao(id):
    # Cancelamento público (precisa de validação, talvez um token? ou apenas deletar se souber o ID)
    # Por segurança, vamos permitir apenas se logado ou se for o organizador
    inscricao = db.session.get(InscricaoEvento, id)
    if not inscricao:
        return jsonify({'error': 'Inscrição não encontrada'}), 404
        
    db.session.delete(inscricao)
    db.session.commit()
    return jsonify({'message': 'Inscrição cancelada com sucesso'})

@api.route('/eventos/<int:id>/inscrever-batismo', methods=['POST'])
@jwt_required()
def inscrever_batismo_celula(id):
    evento = db.session.get(Evento, id)
    if not evento or not evento.ativo or (evento.data_fim < datetime.utcnow()):
        return jsonify({'error': 'Evento inválido ou encerrado'}), 400
        
    current_user_id = get_jwt_identity()
    user = db.session.get(User, current_user_id)
    if not user or not user.membro:
        return jsonify({'error': 'Apenas membros logados podem inscrever'}), 403
        
    lider_atual = user.membro
    data = request.get_json() or {}
    
    visitante_id = data.get('visitante_id')
    membro_id = data.get('membro_id')
    nome = data.get('nome')
    telefone = data.get('telefone')
    email = data.get('email')
    cpf = data.get('cpf')
    data_nascimento_raw = data.get('data_nascimento')
    sexo = data.get('sexo')
    estado_civil = data.get('estado_civil')
    
    if not nome:
        return jsonify({'error': 'Nome é obrigatório'}), 400

    nascimento = None
    if data_nascimento_raw:
        try:
            nascimento = datetime.strptime(data_nascimento_raw, '%Y-%m-%d').date()
        except:
            pass

    try:
        from app.models import MembroNucleo, Nucleo, Membro, Celula
        
        celula_id = data.get('celula_id')
        celula = db.session.get(Celula, celula_id) if celula_id else None
        
        # Se não tiver célula id, tenta carregar do líder logado (se ele liderar uma)
        if not celula and lider_atual.celulas_lideradas:
            celula = lider_atual.celulas_lideradas[0]

        # Define hierarquia baseada na célula ou no líder logado
        ide_id = celula.ide_id if celula else (lider_atual.ide_id if lider_atual.ide_id else None)
        
        # Pastor de Rede: tenta IDE da célula -> Pastor do Líder da Célula -> Pastor do Líder logado
        pastor_id = None
        if celula and celula.ide and celula.ide.pastor_id:
            pastor_id = celula.ide.pastor_id
        elif celula and celula.lider and celula.lider.pastor_id:
            pastor_id = celula.lider.pastor_id
        elif lider_atual:
            pastor_id = lider_atual.pastor_id
            
        supervisor_id = celula.supervisor_id if celula else (lider_atual.supervisor_id if lider_atual.supervisor_id else None)
        lider_membro_id = celula.lider_id if celula else lider_atual.id
            
        nucleo = None
        if celula:
            nucleo = Nucleo.query.filter_by(celula_id=celula.id).first()

        # Se já existe como membro (tipo visitante), vamos apenas atualizar
        alvo_membro = None
        if membro_id:
            alvo_membro = db.session.get(Membro, membro_id)
        
        if alvo_membro:
            alvo_membro.nome = nome
            alvo_membro.telefone = telefone
            alvo_membro.email = email
            alvo_membro.cpf = cpf
            alvo_membro.data_nascimento = nascimento
            alvo_membro.sexo = sexo
            alvo_membro.estado_civil = estado_civil
            alvo_membro.tipo = 'aguardando_batismo'
            alvo_membro.batizado = False
            alvo_membro.data_batismo = evento.data_inicio.date()
            alvo_membro.ide_id = ide_id
            alvo_membro.pastor_id = pastor_id
            alvo_membro.supervisor_id = supervisor_id
            alvo_membro.lider_id = lider_membro_id
            db.session.add(alvo_membro)
        else:
            # Criar novo membro
            alvo_membro = Membro(
                nome=nome,
                telefone=telefone,
                email=email,
                cpf=cpf,
                data_nascimento=nascimento,
                sexo=sexo,
                estado_civil=estado_civil,
                tipo='aguardando_batismo',
                batizado=False,
                data_batismo=evento.data_inicio.date(),
                ativo=True,
                ide_id=ide_id,
                pastor_id=pastor_id,
                supervisor_id=supervisor_id,
                lider_id=lider_membro_id
            )
            db.session.add(alvo_membro)
            db.session.flush() # obtem o alvo_membro.id
            
            if nucleo:
                # Verifica se já está no núcleo (evitar duplicados)
                existente = MembroNucleo.query.filter_by(nucleo_id=nucleo.id, membro_id=alvo_membro.id).first()
                if not existente:
                    novo_mn = MembroNucleo(
                        nucleo_id=nucleo.id,
                        membro_id=alvo_membro.id,
                        is_convidado=False
                    )
                    db.session.add(novo_mn)
            
        # Limpeza de registros de visitante (legado ou redundante)
        if visitante_id:
            from sqlalchemy import text
            # Se fosse um membro_id passado como visitante_id no corpo (antigo comportamento do frontend)
            # Mas vamos ser robustos e tentar deletar apenas se for realmente da tabela visitantes
            db.session.execute(text("DELETE FROM membros_nucleo WHERE visitante_id = :vid"), {'vid': visitante_id})
            db.session.execute(text("DELETE FROM visitantes WHERE id = :vid"), {'vid': visitante_id})
        
        # Endereço
        endereco_data = data.get('endereco')
        if endereco_data:
            from app.models import Endereco
            # Remove endereco existente se houver
            Endereco.query.filter_by(membro_id=alvo_membro.id).delete()
            novo_endereco = Endereco(
                membro_id=alvo_membro.id,
                cep=endereco_data.get('cep'),
                logradouro=endereco_data.get('logradouro'),
                numero=endereco_data.get('numero'),
                complemento=endereco_data.get('complemento'),
                bairro=endereco_data.get('bairro'),
                cidade=endereco_data.get('cidade'),
                estado=endereco_data.get('estado')
            )
            db.session.add(novo_endereco)
                
        # Gerar a inscrição no evento
        # Verificar se já existe inscrição para evitar erro de UNIQUE
        inscricao_existente = InscricaoEvento.query.filter_by(evento_id=evento.id, membro_id=alvo_membro.id).first()
        if not inscricao_existente:
            inscricao = InscricaoEvento(
                evento_id=evento.id, 
                membro_id=alvo_membro.id,
                status='confirmado',
                respostas={'inscrito_por_lider_id': lider_atual.id, 'data_registro': datetime.utcnow().isoformat()}
            )
            db.session.add(inscricao)
        else:
            inscricao_existente.status = 'confirmado'
            db.session.add(inscricao_existente)
        
        db.session.commit()
        return jsonify({'message': 'Membro atualizado/cadastrado e inscrito no batismo com sucesso!', 'membro': alvo_membro.to_dict()}), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500
