from flask import jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.api import api
from app.models import db, Celula, User
from app import db

from app.models import Celula, Nucleo, MembroNucleo

def sync_lideranca_nucleo(celula):
    # 1. Garantir que exista um Núcleo Principal
    nucleo = Nucleo.query.filter_by(celula_id=celula.id).first()
    if not nucleo:
        nucleo = Nucleo(nome="Núcleo Principal", celula_id=celula.id)
        db.session.add(nucleo)
        db.session.flush() # Para pegar o id do núcleo
    
    # 2. Identificar IDs que devem estar no núcleo (Líder e Vice)
    liderança_ids = [id for id in [celula.lider_id, celula.vice_lider_id] if id]
    
    # 3. Adicionar se não existirem
    for m_id in liderança_ids:
        exists = MembroNucleo.query.filter_by(nucleo_id=nucleo.id, membro_id=m_id).first()
        if not exists:
            mn = MembroNucleo(nucleo_id=nucleo.id, membro_id=m_id, is_convidado=False)
            db.session.add(mn)

@api.route('/celulas', methods=['GET'])
@jwt_required()
def get_celulas():
    current_user_id = get_jwt_identity()
    user = db.session.get(User, current_user_id)
    
    if not user:
        return jsonify({'error': 'User not found'}), 404

    # Paginação
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)

    # Filtros
    nome = request.args.get('nome')
    ide_id = request.args.get('ide_id', type=int)
    lider_id = request.args.get('lider_id', type=int)
    supervisor_id = request.args.get('supervisor_id', type=int)
    all_records = request.args.get('all', 'false').lower() == 'true'

    from app.scopes import CellScope
    
    query = Celula.query.filter_by(ativo=True)
    query = CellScope.apply(query, user)

    if nome:
        query = query.filter(Celula.nome.ilike(f'%{nome}%'))
    if ide_id:
        query = query.filter(Celula.ide_id == ide_id)
    if lider_id:
        query = query.filter(Celula.lider_id == lider_id)
    if supervisor_id:
        query = query.filter(Celula.supervisor_id == supervisor_id)

    if all_records:
        celulas = query.all()
        return jsonify({
            'celulas': [c.to_dict() for c in celulas],
            'total': len(celulas),
            'pages': 1,
            'current_page': 1
        })

    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    
    return jsonify({
        'celulas': [c.to_dict() for c in pagination.items],
        'total': pagination.total,
        'pages': pagination.pages,
        'current_page': page
    })

@api.route('/celulas/public', methods=['GET'])
def get_celulas_public():
    celulas = Celula.query.filter_by(ativo=True).order_by(Celula.nome).all()
    return jsonify([{'id': c.id, 'nome': c.nome, 'bairro': c.bairro, 'lider_nome': c.lider.nome if c.lider else None} for c in celulas])

@api.route('/hello-test')
def hello_test():
    return jsonify({"message": "hello"})

@api.route('/celulas/public/nearby', methods=['GET'])
def get_nearby_cells_public():
    lat = request.args.get('lat', type=float)
    lng = request.args.get('lng', type=float)
    radius = request.args.get('radius', 10.0, type=float) # Default 10km

    if lat is None or lng is None:
        return jsonify({'error': 'Latitude and Longitude are required'}), 400

    from sqlalchemy import func
    
    distance_expr = func.acos(
        func.cos(func.radians(lat)) * func.cos(func.radians(Celula.latitude)) * 
        func.cos(func.radians(Celula.longitude) - func.radians(lng)) + 
        func.sin(func.radians(lat)) * func.sin(func.radians(Celula.latitude))
    ) * 6371

    nearby_cells_query = db.session.query(Celula, distance_expr.label('distance')).filter(
        Celula.ativo == True,
        Celula.latitude.isnot(None),
        Celula.longitude.isnot(None)
    ).filter(distance_expr <= radius).order_by('distance').limit(5)

    results_raw = nearby_cells_query.all()

    results = []
    for cell, distance in results_raw:
        results.append({
            'id': cell.id,
            'nome': cell.nome,
            'bairro': cell.bairro,
            'lider_nome': cell.lider.nome if cell.lider else None,
            'distance': round(float(distance), 2)
        })

    return jsonify(results)

@api.route('/celulas/nearby', methods=['GET'])
@jwt_required()
def get_nearby_cells():
    current_user_id = get_jwt_identity()
    user = db.session.get(User, current_user_id)
    
    if not user:
        return jsonify({'error': 'User not found'}), 404

    # Permissão básica: admin, pastor, pastor_de_rede, supervisor
    if user.role not in ['admin', 'pastor', 'pastor_de_rede', 'supervisor']:
        return jsonify({'error': 'Unauthorized'}), 403

    lat = request.args.get('lat', type=float)
    lng = request.args.get('lng', type=float)
    radius = request.args.get('radius', 10.0, type=float) # Default 10km

    if lat is None or lng is None:
        return jsonify({'error': 'Latitude and Longitude are required'}), 400

    from sqlalchemy import func
    from app.scopes import CellScope
    
    distance_expr = func.acos(
        func.cos(func.radians(lat)) * func.cos(func.radians(Celula.latitude)) * 
        func.cos(func.radians(Celula.longitude) - func.radians(lng)) + 
        func.sin(func.radians(lat)) * func.sin(func.radians(Celula.latitude))
    ) * 6371

    # Inicia a query base
    query = db.session.query(Celula, distance_expr.label('distance')).filter(
        Celula.ativo == True,
        Celula.latitude.isnot(None),
        Celula.longitude.isnot(None)
    )

    # Aplica o escopo do usuário (Filtra por IDE/Rede se for pastor de rede, etc)
    # Ajuste: O CellScope.apply adiciona filtros à query. query.filter age no modelo principal da query.
    query = CellScope.apply(query, user)

    limit = 100 if user.role in ['admin', 'pastor'] else 20
    nearby_cells_query = query.filter(distance_expr <= radius).order_by('distance').limit(limit)

    results_raw = nearby_cells_query.all()

    results = []
    for cell, distance in results_raw:
        cell_dict = cell.to_dict()
        cell_dict['distance'] = round(float(distance), 2)
        results.append(cell_dict)

    return jsonify(results)

@api.route('/celulas/<int:id>', methods=['GET'])
@jwt_required()
def get_celula(id):
    celula = db.session.get(Celula, id)
    if not celula:
        return jsonify({'error': 'Not found'}), 404
    return jsonify(celula.to_dict())

@api.route('/celulas', methods=['POST'])
@jwt_required()
def create_celula():
    current_user_id = get_jwt_identity()


    user = db.session.get(User, current_user_id)
    
    print(f"DEBUG CREATE CELL - User ID: {current_user_id}, User: {user.username if user else 'None'}, Role: {user.role if user else 'N/A'}, MembroID: {user.membro_id if user else 'N/A'}")

    data = request.get_json() or {}
    
    # Helper to parse ID from payload
    def parse_id(val):
        if val is None or val == "" or val == "none" or val == 0: return None
        try: return int(val)
        except: return None
    
    req_lider_id = parse_id(data.get('lider_id'))

    # Permission check
    is_management = user and user.role in ['admin', 'pastor', 'pastor_de_rede', 'supervisor']
    is_self_leader = user and user.role == 'lider_de_celula' and user.membro_id == req_lider_id

    if not (is_management or is_self_leader):
        error_msg = f'Unauthorized. Role ({user.role if user else "None"}) cannot create cells'
        if user and user.role == 'lider_de_celula':
            error_msg += ' for other leaders (only for yourself).'
        return jsonify({'error': error_msg}), 403

    # Extra check for leaders: Limit of ONE active cell
    if user and user.role == 'lider_de_celula':
        existing_cell = Celula.query.filter_by(lider_id=user.membro_id, ativo=True).first()
        if existing_cell:
            return jsonify({'error': 'Você já possui uma célula ativa vinculada ao seu nome. Não é permitido criar mais de uma.'}), 400




    
    if not data.get('nome'):
        return jsonify({'error': 'Name is required'}), 400

    celula = Celula()
    update_celula_data(celula, data)
    db.session.add(celula)
    db.session.flush()
    sync_lideranca_nucleo(celula)
    
    try:
        db.session.commit()
        return jsonify(celula.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@api.route('/celulas/<int:id>', methods=['PUT'])
@jwt_required()
def update_celula(id):
    celula = db.session.get(Celula, id)
    if not celula:
        return jsonify({'error': 'Not found'}), 404
        
    data = request.get_json() or {}
    update_celula_data(celula, data)
    sync_lideranca_nucleo(celula)
    
    try:
        db.session.commit()
        return jsonify(celula.to_dict())
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@api.route('/celulas/<int:id>', methods=['DELETE'])
@jwt_required()
def delete_celula(id):
    celula = db.session.get(Celula, id)
    if not celula:
        return jsonify({'error': 'Not found'}), 404
        
    # Soft delete instead of hard delete
    celula.ativo = False
    try:
        db.session.commit()
        return jsonify({'message': 'Inactivated successfully'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

def update_celula_data(celula, data):
    def parse_id(val):
        if val is None or val == "" or val == "none" or val == 0:
            return None
        try:
            return int(val)
        except (ValueError, TypeError):
            return None

    if 'nome' in data: celula.nome = data['nome']
    if 'ide_id' in data: celula.ide_id = parse_id(data['ide_id'])
    if 'supervisor_id' in data: celula.supervisor_id = parse_id(data['supervisor_id'])
    if 'lider_id' in data: celula.lider_id = parse_id(data['lider_id'])
    if 'vice_lider_id' in data: celula.vice_lider_id = parse_id(data['vice_lider_id'])
    if 'dia_reuniao' in data: celula.dia_reuniao = data['dia_reuniao']
    if 'horario_reuniao' in data: celula.horario_reuniao = data['horario_reuniao']
    if 'logradouro' in data: celula.logradouro = data['logradouro']
    if 'numero' in data: celula.numero = data['numero']
    if 'complemento' in data: celula.complemento = data['complemento']
    if 'bairro' in data: celula.bairro = data['bairro']
    if 'cidade' in data: celula.cidade = data['cidade']
    if 'estado' in data: celula.estado = data['estado']
    if 'cep' in data: celula.cep = data['cep']
    if 'latitude' in data: 
        try: celula.latitude = float(data['latitude'])
        except: pass
    if 'longitude' in data: 
        try: celula.longitude = float(data['longitude'])
        except: pass
