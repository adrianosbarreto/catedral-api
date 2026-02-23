
import os
from flask import jsonify, request, current_app
from app.api import api
from app.models import Noticia
from app import db
from datetime import datetime
from flask_jwt_extended import jwt_required, get_jwt_identity
from werkzeug.utils import secure_filename
import uuid

UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'static', 'uploads')

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@api.route('/noticias', methods=['GET'])
@jwt_required()
def get_noticias():
    from app.models import User, Ide
    current_user_id = get_jwt_identity()
    user = db.session.get(User, current_user_id)
    
    if not user:
        return jsonify({'error': 'User not found'}), 404

    # Only active news within the date range
    now = datetime.utcnow()
    query = Noticia.query.filter(
        Noticia.ativo == True,
        Noticia.data_inicio <= now,
        Noticia.data_fim >= now
    )
    
    # Filter by user's IDE
    if user.role != 'admin':
        from sqlalchemy import or_
        if user.membro and user.membro.ide_id:
            query = query.filter(
                or_(
                    Noticia.todas_ides == True,
                    Noticia.ides.any(Ide.id == user.membro.ide_id)
                )
            )
        else:
            # If user has no IDE associated, only show "all IDEs" news
            query = query.filter(Noticia.todas_ides == True)
            
    noticias = query.order_by(Noticia.criado_em.desc()).all()
    
    return jsonify([n.to_dict() for n in noticias])

@api.route('/noticias/admin', methods=['GET'])
@jwt_required()
def get_noticias_admin():
    # Admin gets everything
    noticias = Noticia.query.order_by(Noticia.criado_em.desc()).all()
    return jsonify([n.to_dict() for n in noticias])

@api.route('/noticias', methods=['POST'])
@jwt_required()
def create_noticia():
    from app.models import Ide
    data = request.get_json() or {}
    
    required = ['titulo', 'data_inicio', 'data_fim']
    for field in required:
        if field not in data:
            return jsonify({'error': f'{field} is required'}), 400
            
    try:
        noticia = Noticia()
        noticia.titulo = data['titulo']
        noticia.foto_url = data.get('foto_url')
        noticia.data_inicio = datetime.fromisoformat(data['data_inicio'].replace('Z', '+00:00'))
        noticia.data_fim = datetime.fromisoformat(data['data_fim'].replace('Z', '+00:00'))
        noticia.mostrar_ao_iniciar = data.get('mostrar_ao_iniciar', True)
        noticia.todas_ides = data.get('todas_ides', True)
        noticia.ativo = data.get('ativo', True)
        
        if not noticia.todas_ides and 'ides' in data:
            ide_ids = data['ides']
            noticia.ides = Ide.query.filter(Ide.id.in_(ide_ids)).all()
        
        db.session.add(noticia)
        db.session.commit()
        return jsonify(noticia.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@api.route('/noticias/<int:id>', methods=['PUT'])
@jwt_required()
def update_noticia(id):
    from app.models import Ide
    noticia = db.session.get(Noticia, id)
    if not noticia:
        return jsonify({'error': 'Not found'}), 404
        
    data = request.get_json() or {}
    
    try:
        if 'titulo' in data: noticia.titulo = data['titulo']
        if 'foto_url' in data: noticia.foto_url = data['foto_url']
        if 'mostrar_ao_iniciar' in data: noticia.mostrar_ao_iniciar = data['mostrar_ao_iniciar']
        if 'todas_ides' in data: noticia.todas_ides = data['todas_ides']
        if 'ativo' in data: noticia.ativo = data['ativo']
        
        if 'data_inicio' in data:
            noticia.data_inicio = datetime.fromisoformat(data['data_inicio'].replace('Z', '+00:00'))
        if 'data_fim' in data:
            noticia.data_fim = datetime.fromisoformat(data['data_fim'].replace('Z', '+00:00'))
            
        if 'ides' in data:
            if noticia.todas_ides:
                noticia.ides = []
            else:
                ide_ids = data['ides']
                noticia.ides = Ide.query.filter(Ide.id.in_(ide_ids)).all()
            
        db.session.commit()
        return jsonify(noticia.to_dict())
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@api.route('/noticias/<int:id>', methods=['DELETE'])
@jwt_required()
def delete_noticia(id):
    noticia = db.session.get(Noticia, id)
    if not noticia:
        return jsonify({'error': 'Not found'}), 404
        
    # Soft delete
    noticia.ativo = False
    db.session.commit()
    return jsonify({'message': 'Deleted successfully'})

@api.route('/noticias/upload', methods=['POST'])
@jwt_required()
def upload_foto_noticia():
    if 'foto' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    
    file = request.files['foto']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
        
    if file:
        filename = secure_filename(file.filename)
        # Unique filename
        ext = os.path.splitext(filename)[1]
        unique_filename = f"{uuid.uuid4().hex}{ext}"
        
        file_path = os.path.join(UPLOAD_FOLDER, unique_filename)
        file.save(file_path)
        
        # Determine base URL for static files
        # In this setup, we'll assume /app/static/uploads is served as /static/uploads
        # Or even better, just return the relative path and let frontend handle it
        url = f"/static/uploads/{unique_filename}"
        
        return jsonify({'url': url})
    
    return jsonify({'error': 'Unknown error'}), 400
