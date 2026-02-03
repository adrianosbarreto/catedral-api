from flask import jsonify, request
from flask_jwt_extended import jwt_required
from app.api import api
from app.models import db, Nucleo, MembroNucleo, Membro, Celula
from datetime import datetime

@api.route('/celulas/<int:celula_id>/nucleos', methods=['GET'])
@jwt_required()
def get_nucleos(celula_id):
    # Ensure at least one nucleus exists for this cell
    nucleo = Nucleo.query.filter_by(celula_id=celula_id).first()
    if not nucleo:
        celula = db.session.get(Celula, celula_id)
        if not celula:
            return jsonify({'error': 'Celula not found'}), 404
        nucleo = Nucleo(nome="Núcleo Principal", celula_id=celula_id)
        db.session.add(nucleo)
        db.session.commit()
    
    return jsonify(nucleo.to_dict())

@api.route('/celulas/<int:celula_id>/nucleos', methods=['POST'])
@jwt_required()
def create_nucleo(celula_id):
    # Just return existing if already exists, logic shifted to GET
    nucleo = Nucleo.query.filter_by(celula_id=celula_id).first()
    if nucleo:
        return jsonify(nucleo.to_dict()), 200
    
    data = request.get_json() or {}
    nome = data.get('nome', 'Núcleo Principal')
    
    nucleo = Nucleo(nome=nome, celula_id=celula_id)
    db.session.add(nucleo)
    db.session.commit()
    return jsonify(nucleo.to_dict()), 201

@api.route('/nucleos/<int:id>', methods=['DELETE'])
@jwt_required()
def delete_nucleo(id):
    nucleo = db.session.get(Nucleo, id)
    if not nucleo:
        return jsonify({'error': 'Not found'}), 404
    # Prevent deleting if it's the last one? Or just allow.
    db.session.delete(nucleo)
    db.session.commit()
    return jsonify({'message': 'Deleted successfully'})

@api.route('/nucleos/<int:id>/membros', methods=['POST'])
@jwt_required()
def add_membro_nucleo(id):
    data = request.get_json() or {}
    
    # Pre-check for duplicates if it's a registered member
    membro_id = data.get('membro_id')
    if membro_id:
        existing = MembroNucleo.query.filter_by(nucleo_id=id, membro_id=membro_id).first()
        if existing:
            return jsonify(existing.to_dict()), 200

    membro_nucleo = MembroNucleo(nucleo_id=id)
    
    if data.get('is_convidado'):
        membro_nucleo.is_convidado = True
        membro_nucleo.nome_convidado = data.get('nome')
        membro_nucleo.telefone_convidado = data.get('telefone')
    else:
        if not membro_id:
            return jsonify({'error': 'membro_id is required if not guest'}), 400
        membro_nucleo.membro_id = membro_id

    db.session.add(membro_nucleo)
    db.session.commit()
    return jsonify(membro_nucleo.to_dict()), 201

@api.route('/membros-nucleo/<int:id>', methods=['DELETE'])
@jwt_required()
def remove_membro_nucleo(id):
    mn = db.session.get(MembroNucleo, id)
    if not mn:
        return jsonify({'error': 'Not found'}), 404
    db.session.delete(mn)
    db.session.commit()
    return jsonify({'message': 'Removed successfully'})
