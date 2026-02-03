from flask import jsonify, request
from flask_jwt_extended import jwt_required
from app.api import api
from app.models import Membro, Endereco, PapelMembro, Ide
from app import db
from datetime import datetime

@api.route('/membros', methods=['GET'])
@jwt_required()
def get_membros():
    from flask_jwt_extended import get_jwt_identity
    from app.models import User
    from app.scopes import MembroScope
    
    current_user_id = get_jwt_identity()
    user = db.session.get(User, current_user_id)
    
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    role = request.args.get('role')
    
    ide_id = request.args.get('ide_id', type=int)
    nome = request.args.get('nome')
    estado_civil = request.args.get('estado_civil')
    lider_id = request.args.get('lider_id', type=int)
    
    query = Membro.query
    if user:
        query = MembroScope.apply(query, user)
    
    if role:
        # Split by comma to support multiple roles filter
        roles = [r.strip() for r in role.split(',')]
        # Join with PapelMembro and filter using in_
        query = query.join(Membro.papeis).filter(PapelMembro.papel.in_(roles))

    if ide_id:
        query = query.filter(Membro.ide_id == ide_id)
        
    if nome:
        query = query.filter(Membro.nome.ilike(f'%{nome}%'))
        
    if estado_civil:
        # Check if the DB value contains the filter string (e.g. 'solteiro' in 'Solteiro(a)')
        query = query.filter(Membro.estado_civil.ilike(f'%{estado_civil}%'))

    if lider_id:
        query = query.filter(Membro.lider_id == lider_id)

    # Use distinct to ensure no duplicate members due to joins
    query = query.distinct()

    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    membros = pagination.items
    
    return jsonify({
        'membros': [membro.to_dict() for membro in membros],
        'total': pagination.total,
        'pages': pagination.pages,
        'current_page': page
    })



def parse_id(val):
    if val is None or val == "" or val == "none" or val == 0:
        return None
    try:
        return int(val)
    except (ValueError, TypeError):
        return None

@api.route('/membros', methods=['POST'])
@jwt_required()
def create_membro():
    data = request.get_json() or {}
    if 'nome' not in data:
        return jsonify({'error': 'Nome is required'}), 400

    membro = Membro()
    membro.nome = data.get('nome')
    membro.email = data.get('email')
    membro.telefone = data.get('telefone')
    membro.cpf = data.get('cpf')
    membro.estado_civil = data.get('estado_civil')
    membro.sexo = data.get('sexo')
    membro.ide_id = parse_id(data.get('ide_id'))
    membro.lider_id = parse_id(data.get('lider_id'))
    membro.tipo = data.get('tipo', 'membro')
    membro.batizado = data.get('batizado', False)
    
    if data.get('data_nascimento'):
        try:
            membro.data_nascimento = datetime.fromisoformat(data.get('data_nascimento')).date()
        except ValueError:
             membro.data_nascimento = datetime.strptime(data.get('data_nascimento'), '%Y-%m-%d').date()

    if data.get('data_batismo'):
        try:
            membro.data_batismo = datetime.fromisoformat(data.get('data_batismo')).date()
        except ValueError:
            membro.data_batismo = datetime.strptime(data.get('data_batismo'), '%Y-%m-%d').date()

    db.session.add(membro)
    db.session.flush()

    if 'endereco' in data:
        end_data = data['endereco']
        endereco = Endereco(membro_id=membro.id)
        endereco.cep = end_data.get('cep')
        endereco.logradouro = end_data.get('logradouro')
        endereco.numero = end_data.get('numero')
        endereco.complemento = end_data.get('complemento')
        endereco.bairro = end_data.get('bairro')
        endereco.cidade = end_data.get('cidade')
        endereco.estado = end_data.get('estado')
        db.session.add(endereco)

    if 'papel' in data:
        papel = PapelMembro(membro_id=membro.id, papel=data['papel'])
        db.session.add(papel)

    db.session.commit()
    return jsonify(membro.to_dict()), 201

@api.route('/membros/<int:id>', methods=['GET'])
@jwt_required()
def get_membro(id):
    membro = db.session.get(Membro, id)
    if not membro:
        return jsonify({'error': 'Not found'}), 404
    return jsonify(membro.to_dict())

@api.route('/membros/<int:id>', methods=['PUT'])
@jwt_required()
def update_membro(id):
    membro = db.session.get(Membro, id)
    if not membro:
        return jsonify({'error': 'Not found'}), 404
        
    data = request.get_json() or {}
    
    if 'nome' in data: membro.nome = data['nome']
    if 'email' in data: membro.email = data['email']
    if 'telefone' in data: membro.telefone = data['telefone']
    if 'cpf' in data: membro.cpf = data['cpf']
    if 'estado_civil' in data: membro.estado_civil = data['estado_civil']
    if 'sexo' in data: membro.sexo = data['sexo']
    if 'ide_id' in data: membro.ide_id = parse_id(data['ide_id'])
    if 'lider_id' in data: membro.lider_id = parse_id(data['lider_id'])
    if 'ativo' in data: membro.ativo = data['ativo']
    if 'tipo' in data: membro.tipo = data['tipo']
    if 'batizado' in data: membro.batizado = data['batizado']

    if 'data_nascimento' in data:
        if data['data_nascimento']:
             try:
                membro.data_nascimento = datetime.fromisoformat(data['data_nascimento']).date()
             except ValueError:
                membro.data_nascimento = datetime.strptime(data['data_nascimento'], '%Y-%m-%d').date()
        else:
            membro.data_nascimento = None

    if 'endereco' in data:
        end_data = data['endereco']
        endereco = membro.enderecos.first()
        if not endereco:
            endereco = Endereco(membro_id=membro.id)
            db.session.add(endereco)
        
        if 'cep' in end_data: endereco.cep = end_data['cep']
        if 'logradouro' in end_data: endereco.logradouro = end_data['logradouro']
        if 'numero' in end_data: endereco.numero = end_data['numero']
        if 'complemento' in end_data: endereco.complemento = end_data['complemento']
        if 'bairro' in end_data: endereco.bairro = end_data['bairro']
        if 'cidade' in end_data: endereco.cidade = end_data['cidade']
        if 'estado' in end_data: endereco.estado = end_data['estado']

    if 'papel' in data:
        papel_obj = membro.papeis.first()
        if not papel_obj:
            papel_obj = PapelMembro(membro_id=membro.id)
            db.session.add(papel_obj)
        papel_obj.papel = data['papel']

    db.session.commit()
    return jsonify(membro.to_dict())

@api.route('/membros/<int:id>', methods=['DELETE'])
@jwt_required()
def delete_membro(id):
    membro = db.session.get(Membro, id)
    if not membro:
        return jsonify({'error': 'Not found'}), 404
        
    db.session.delete(membro)
    db.session.commit()
    return jsonify({'message': 'Deleted successfully'})

@api.route('/stats/dashboard', methods=['GET'])
@jwt_required()
def get_dashboard_stats():
    from flask_jwt_extended import get_jwt_identity
    from app.models import User
    from app.scopes import MembroScope, CellScope
    from sqlalchemy import func
    
    current_user_id = get_jwt_identity()
    user = db.session.get(User, current_user_id)

    # Total members (filtered)
    membro_query = Membro.query
    if user:
        membro_query = MembroScope.apply(membro_query, user)
    total_membros = membro_query.count()
    
    # Role distribution (filtered)
    roles_dist = db.session.query(
        PapelMembro.papel, 
        func.count(PapelMembro.id)
    ).join(Membro).filter(Membro.id.in_(membro_query.with_entities(Membro.id))).group_by(PapelMembro.papel).all()
    
    role_counts = {role: count for role, count in roles_dist}
    
    return jsonify({
        'total_membros': total_membros,
        'roles_distribution': [
            {'papel': role, 'quantidade': count} 
            for role, count in roles_dist
        ]
    })
