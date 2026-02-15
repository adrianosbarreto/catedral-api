from flask import jsonify, request
from flask_jwt_extended import jwt_required
from app.api import api
from app.models import db, Ide, Membro
from app.decorators import requires_role

@api.route('/ides', methods=['GET'])
@requires_role(['admin', 'pastor'])
def get_ides():
    ides = Ide.query.all()
    return jsonify([ide.to_dict() for ide in ides])

@api.route('/ides/<int:id>', methods=['GET'])
@requires_role(['admin', 'pastor'])
def get_ide(id):
    ide = db.session.get(Ide, id)
    if not ide:
        return jsonify({'error': 'Not found'}), 404
    return jsonify(ide.to_dict())

@api.route('/ides', methods=['POST'])
@requires_role(['admin', 'pastor'])
def create_ide():
    data = request.get_json() or {}
    
    if not data.get('nome'):
        return jsonify({'error': 'Name is required'}), 400

    ide = Ide()
    ide.nome = data['nome']
    if 'pastor_id' in data:
        ide.pastor_id = data['pastor_id']
    
    db.session.add(ide)
    try:
        db.session.commit()
        return jsonify(ide.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@api.route('/ides/<int:id>', methods=['PUT'])
@requires_role(['admin', 'pastor'])
def update_ide(id):
    ide = db.session.get(Ide, id)
    if not ide:
        return jsonify({'error': 'Not found'}), 404
        
    data = request.get_json() or {}
    
    if 'nome' in data: ide.nome = data['nome']
    if 'pastor_id' in data: ide.pastor_id = data['pastor_id']
    
    try:
        db.session.commit()
        return jsonify(ide.to_dict())
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@api.route('/ides/<int:id>', methods=['DELETE'])
@requires_role(['admin', 'pastor'])
def delete_ide(id):
    ide = db.session.get(Ide, id)
    if not ide:
        return jsonify({'error': 'Not found'}), 404
        
    db.session.delete(ide)
    try:
        db.session.commit()
        return jsonify({'message': 'Deleted successfully'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500
