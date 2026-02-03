
from flask import jsonify, request
from app.api import api
from app.models import Evento
from app import db
from datetime import datetime
from flask_jwt_extended import jwt_required

@api.route('/eventos', methods=['GET'])
@jwt_required()
def get_eventos():
    eventos = Evento.query.order_by(Evento.data_inicio).all()
    return jsonify([evento.to_dict() for evento in eventos])

@api.route('/eventos/<int:id>', methods=['GET'])
@jwt_required()
def get_evento(id):
    evento = db.session.get(Evento, id)
    if not evento:
        return jsonify({'error': 'Not found'}), 404
    return jsonify(evento.to_dict())

@api.route('/eventos', methods=['POST'])
@jwt_required()
def create_evento():
    data = request.get_json() or {}
    
    # Basic validation
    required = ['titulo', 'data_inicio', 'data_fim', 'local', 'tipo_evento']
    for field in required:
        if field not in data:
            return jsonify({'error': f'{field} is required'}), 400
            
    try:
        evento = Evento()
        evento.titulo = data['titulo']
        evento.descricao = data.get('descricao')
        evento.local = data['local']
        evento.tipo_evento = data['tipo_evento']
        evento.capacidade_maxima = int(data['capacidade_maxima']) if data.get('capacidade_maxima') else None
        
        # Handle ISO format strings from frontend
        evento.data_inicio = datetime.fromisoformat(data['data_inicio'].replace('Z', '+00:00'))
        evento.data_fim = datetime.fromisoformat(data['data_fim'].replace('Z', '+00:00'))
        
        db.session.add(evento)
        db.session.commit()
        return jsonify(evento.to_dict()), 201
    except ValueError as e:
        return jsonify({'error': f'Invalid date format: {str(e)}'}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@api.route('/eventos/<int:id>', methods=['PUT'])
@jwt_required()
def update_evento(id):
    evento = db.session.get(Evento, id)
    if not evento:
        return jsonify({'error': 'Not found'}), 404
        
    data = request.get_json() or {}
    
    try:
        if 'titulo' in data: evento.titulo = data['titulo']
        if 'descricao' in data: evento.descricao = data['descricao']
        if 'local' in data: evento.local = data['local']
        if 'tipo_evento' in data: evento.tipo_evento = data['tipo_evento']
        if 'capacidade_maxima' in data: 
            evento.capacidade_maxima = int(data['capacidade_maxima']) if data['capacidade_maxima'] else None
            
        if 'data_inicio' in data:
            evento.data_inicio = datetime.fromisoformat(data['data_inicio'].replace('Z', '+00:00'))
        if 'data_fim' in data:
            evento.data_fim = datetime.fromisoformat(data['data_fim'].replace('Z', '+00:00'))
            
        db.session.commit()
        return jsonify(evento.to_dict())
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@api.route('/eventos/<int:id>', methods=['DELETE'])
@jwt_required()
def delete_evento(id):
    evento = db.session.get(Evento, id)
    if not evento:
        return jsonify({'error': 'Not found'}), 404
        
    db.session.delete(evento)
    db.session.commit()
    return jsonify({'message': 'Deleted successfully'})
