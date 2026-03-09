
from flask import jsonify, request
from app.api import api
from app.models import Projeto, User
from app import db
from datetime import datetime
from flask_jwt_extended import jwt_required, get_jwt_identity
import re
import unicodedata

def slugify(text):
    text = unicodedata.normalize('NFKD', text).encode('ascii', 'ignore').decode('ascii')
    text = re.sub(r'[^\w\s-]', '', text).strip().lower()
    return re.sub(r'[-\s]+', '-', text)

@api.route('/public/projetos', methods=['GET'])
def get_public_projetos():
    projetos = Projeto.query.filter_by(ativo=True).order_by(Projeto.ordem.asc(), Projeto.data_criacao.desc()).all()
    return jsonify([p.to_dict() for p in projetos]), 200

@api.route('/public/projetos/<slug>', methods=['GET'])
def get_public_projeto_by_slug(slug):
    projeto = Projeto.query.filter_by(slug=slug, ativo=True).first()
    if not projeto:
        return jsonify({'error': 'Projeto não encontrado'}), 404
    return jsonify(projeto.to_dict()), 200

@api.route('/admin/projetos', methods=['GET'])
@jwt_required()
def admin_get_projetos():
    current_user_id = get_jwt_identity()
    user = db.session.get(User, current_user_id)
    if not user or user.role != 'admin':
        return jsonify({'error': 'Acesso negado'}), 403
        
    projetos = Projeto.query.order_by(Projeto.ordem.asc(), Projeto.data_criacao.desc()).all()
    return jsonify([p.to_dict() for p in projetos]), 200

@api.route('/admin/projetos', methods=['POST'])
@jwt_required()
def admin_create_projeto():
    current_user_id = get_jwt_identity()
    user = db.session.get(User, current_user_id)
    if not user or user.role != 'admin':
        return jsonify({'error': 'Acesso negado'}), 403
        
    data = request.json
    if not data or not data.get('titulo'):
        return jsonify({'error': 'Título é obrigatório'}), 400
        
    titulo = data.get('titulo')
    slug = data.get('slug') or slugify(titulo)
    
    # Verificar se slug já existe
    if Projeto.query.filter_by(slug=slug).first():
        slug = f"{slug}-{int(datetime.utcnow().timestamp())}"

    novo_projeto = Projeto(
        titulo=titulo,
        subtitulo=data.get('subtitulo'),
        slug=slug,
        descricao_home=data.get('descricao_home'),
        imagem_capa=data.get('imagem_capa'),
        ativo=data.get('ativo', True),
        destaque=data.get('destaque', False),
        ordem=data.get('ordem', 0),
        paginas=data.get('paginas', []),
        galeria=data.get('galeria', []),
        custom_css=data.get('custom_css')
    )

    
    db.session.add(novo_projeto)
    db.session.commit()
    
    return jsonify(novo_projeto.to_dict()), 201

@api.route('/admin/projetos/<int:id>', methods=['PUT'])
@jwt_required()
def admin_update_projeto(id):
    current_user_id = get_jwt_identity()
    user = db.session.get(User, current_user_id)
    if not user or user.role != 'admin':
        return jsonify({'error': 'Acesso negado'}), 403
        
    projeto = db.session.get(Projeto, id)
    if not projeto:
        return jsonify({'error': 'Projeto não encontrado'}), 404
        
    data = request.json
    projeto.titulo = data.get('titulo', projeto.titulo)
    projeto.subtitulo = data.get('subtitulo', projeto.subtitulo)
    if data.get('slug'):
        projeto.slug = data.get('slug')
    projeto.descricao_home = data.get('descricao_home', projeto.descricao_home)
    projeto.imagem_capa = data.get('imagem_capa', projeto.imagem_capa)
    projeto.ativo = data.get('ativo', projeto.ativo)
    projeto.destaque = data.get('destaque', projeto.destaque)
    projeto.ordem = data.get('ordem', projeto.ordem)
    projeto.paginas = data.get('paginas', projeto.paginas)
    projeto.galeria = data.get('galeria', projeto.galeria)
    projeto.custom_css = data.get('custom_css', projeto.custom_css)

    
    db.session.commit()
    return jsonify(projeto.to_dict()), 200

@api.route('/admin/projetos/<int:id>', methods=['DELETE'])
@jwt_required()
def admin_delete_projeto(id):
    current_user_id = get_jwt_identity()
    user = db.session.get(User, current_user_id)
    if not user or user.role != 'admin':
        return jsonify({'error': 'Acesso negado'}), 403
        
    projeto = db.session.get(Projeto, id)
    if not projeto:
        return jsonify({'error': 'Projeto não encontrado'}), 404
        
    db.session.delete(projeto)
    db.session.commit()
    return jsonify({'message': 'Projeto excluído com sucesso'}), 200
