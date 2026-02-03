from flask import jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.api import api
from app.models import db, Celula, User
from app import db

@api.route('/celulas', methods=['GET'])
@jwt_required()
def get_celulas():
    current_user_id = get_jwt_identity()
    user = db.session.get(User, current_user_id)
    
    if not user:
        return jsonify({'error': 'User not found'}), 404

    from app.scopes import CellScope
    
    query = Celula.query
    query = CellScope.apply(query, user)
    
    celulas_list = query.all()
    return jsonify([c.to_dict() for c in celulas_list])

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
    
    if not user or user.role not in ['admin', 'pastor', 'pastor_de_rede', 'supervisor']:
        return jsonify({'error': 'Unauthorized. Only pastors or supervisors can create cells.'}), 403

    data = request.get_json() or {}
    
    if not data.get('nome'):
        return jsonify({'error': 'Name is required'}), 400

    celula = Celula()
    update_celula_data(celula, data)
    
    db.session.add(celula)
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
        
    db.session.delete(celula)
    try:
        db.session.commit()
        return jsonify({'message': 'Deleted successfully'})
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
