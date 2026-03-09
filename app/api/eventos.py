
from flask import jsonify, request
from app.api import api
from app.models import Evento, User
from app import db
import os
from werkzeug.utils import secure_filename
from datetime import datetime
from flask_jwt_extended import jwt_required, get_jwt_identity

@api.route('/eventos', methods=['GET'])
@jwt_required()
def get_eventos():
    current_user_id = get_jwt_identity()
    user = db.session.get(User, current_user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404
        
    mostrar_finalizados = request.args.get('finalizados', 'false').lower() == 'true'
    
    query = Evento.query
    
    # Filtro de Finalizados
    agora = datetime.utcnow()
    if mostrar_finalizados:
        query = query.filter(Evento.data_fim < agora)
    else:
        # Mostra todos os eventos futuros (ativos e inativos) para os gestores
        query = query.filter(Evento.data_fim >= agora)
    
    # Filtro de Visibilidade (IDE vs Igreja)
    # Admin e Pastor (geral/rede) vêem tudo. Supervisores e abaixo vêem apenas da sua IDE ou Igreja.
    if user.role not in ['admin', 'pastor', 'pastor_de_rede']:

        from sqlalchemy import or_
        # Regra: Se não tem IDEs associadas, é da Igreja (todos veem). 
        # Se tem IDEs, só vê quem pertence a uma delas.
        # Também mantemos o ide_id legado para compatibilidade.
        user_ide_id = user.membro.ide_id if user.membro else None
        
        if user_ide_id:
            query = query.filter(or_(
                Evento.ide_id == None, # Legado
                Evento.ide_id == user_ide_id, # Legado
                ~Evento.ides.any(), # Sem IDEs (Igreja)
                Evento.ides.any(id=user_ide_id) # Pertence à IDE do usuário
            ))
        else:
            # Se o usuário não tem IDE, vê apenas os da Igreja
            query = query.filter(or_(
                Evento.ide_id == None,
                ~Evento.ides.any()
            ))
            
    eventos = query.order_by(Evento.data_inicio).all()
    return jsonify([evento.to_dict() for evento in eventos])

@api.route('/public/eventos', methods=['GET'])
def get_eventos_publico():
    agora = datetime.utcnow()
    # Retorna apenas eventos ativos e que não finalizaram
    query = Evento.query.filter(Evento.ativo == True, Evento.data_fim >= agora)
    eventos = query.order_by(Evento.data_inicio).all()
    return jsonify([evento.to_dict() for evento in eventos])

@api.route('/eventos/<int:id>', methods=['GET'])
@jwt_required()
def get_evento(id):
    evento = db.session.get(Evento, id)
    if not evento:
        return jsonify({'error': 'Not found'}), 404
    return jsonify(evento.to_dict())

@api.route('/eventos/upload-banner', methods=['POST'])
@jwt_required()
def upload_evento_banner():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    
    if file:
        import base64
        import mimetypes
        file_content = file.read()
        mime_type, _ = mimetypes.guess_type(file.filename)
        if not mime_type:
            mime_type = 'image/jpeg'
            
        encoded = base64.b64encode(file_content).decode('utf-8')
        file_url = f"data:{mime_type};base64,{encoded}"
        
        return jsonify({'url': file_url}), 200

@api.route('/eventos', methods=['POST'])
@jwt_required()
def create_evento():
    current_user_id = get_jwt_identity()
    user = db.session.get(User, current_user_id)
    if not user or user.role not in ['admin', 'pastor', 'pastor_de_rede']:
        return jsonify({'error': 'Você não tem permissão para criar eventos.'}), 403

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
        
        # Campos de gestão e visibilidade
        evento.imagem_banner = data.get('imagem_banner')
        evento.cta_texto = data.get('cta_texto')
        evento.cta_link = data.get('cta_link')
        evento.config_mensagem_antecedencia = int(data.get('config_mensagem_antecedencia', 0))
        evento.tipo_visibilidade = data.get('tipo_visibilidade', 'igreja')
        evento.ativo = data.get('ativo', True)
        evento.is_batismo = data.get('is_batismo', False)
        evento.criado_por_id = current_user_id
        
        # Gestão de participantes
        evento.gerenciar_participantes = data.get('gerenciar_participantes', False)
        evento.instrucoes_inscricao = data.get('instrucoes_inscricao')
        evento.valor_inscricao = float(data['valor_inscricao']) if data.get('valor_inscricao') else None
        evento.exibir_vagas_restantes = data.get('exibir_vagas_restantes', False)
        
        # Múltiplas IDEs
        if 'ides' in data and isinstance(data['ides'], list):
            from app.models import Ide
            ide_list = Ide.query.filter(Ide.id.in_(data['ides'])).all()
            evento.ides = ide_list
            # Preencher ide_id legado se houver apenas uma IDE para retrocompatibilidade
            if len(data['ides']) == 1:
                evento.ide_id = data['ides'][0]
        
        if 'perguntas' in data:
            evento.perguntas = data['perguntas']
        
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
    current_user_id = get_jwt_identity()
    user = db.session.get(User, current_user_id)
    
    evento = db.session.get(Evento, id)
    if not evento:
        return jsonify({'error': 'Not found'}), 404
        
    # Permissão: Admin e Pastor podem tudo. Outros apenas se forem o criador ou se for legado e tiverem cargo de gestão.
    is_owner = evento.criado_por_id == current_user_id
    is_admin_or_pastor = user.role in ['admin', 'pastor', 'pastor_de_rede']
    is_legacy = evento.criado_por_id is None
    is_manager = user.role in ['supervisor']

    if not (is_admin_or_pastor or is_owner or (is_legacy and is_manager)):
        return jsonify({'error': 'Você não tem permissão para alterar este evento. Apenas o criador ou administradores podem editá-lo.'}), 403

    data = request.get_json() or {}
    
    try:
        if 'titulo' in data: evento.titulo = data['titulo']
        if 'descricao' in data: evento.descricao = data['descricao']
        if 'local' in data: evento.local = data['local']
        if 'tipo_evento' in data: evento.tipo_evento = data['tipo_evento']
        if 'capacidade_maxima' in data: 
            evento.capacidade_maxima = int(data['capacidade_maxima']) if data['capacidade_maxima'] else None
            
        # Novos campos
        if 'is_batismo' in data: evento.is_batismo = data['is_batismo']
        if 'imagem_banner' in data: evento.imagem_banner = data['imagem_banner']
        if 'cta_texto' in data: evento.cta_texto = data['cta_texto']
        if 'cta_link' in data: evento.cta_link = data['cta_link']
        # Múltiplas IDEs
        if 'ides' in data and isinstance(data['ides'], list):
            from app.models import Ide
            ide_list = Ide.query.filter(Ide.id.in_(data['ides'])).all()
            evento.ides = ide_list
            # Atualizar ide_id legado se houver apenas uma IDE
            if len(data['ides']) == 1:
                evento.ide_id = data['ides'][0]
            elif len(data['ides']) == 0:
                evento.ide_id = None

        if 'gerenciar_participantes' in data: evento.gerenciar_participantes = data['gerenciar_participantes']
        if 'instrucoes_inscricao' in data: evento.instrucoes_inscricao = data['instrucoes_inscricao']
        if 'valor_inscricao' in data: 
            evento.valor_inscricao = float(data['valor_inscricao']) if data['valor_inscricao'] else None
        if 'exibir_vagas_restantes' in data: evento.exibir_vagas_restantes = data['exibir_vagas_restantes']
        if 'perguntas' in data: evento.perguntas = data['perguntas']
        if 'ativo' in data: evento.ativo = data['ativo']
            
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
    current_user_id = get_jwt_identity()
    user = db.session.get(User, current_user_id)
    
    evento = db.session.get(Evento, id)
    if not evento:
        return jsonify({'error': 'Not found'}), 404
        
    # Permissão: Admin e Pastor podem tudo. Outros apenas se forem o criador.
    is_owner = evento.criado_por_id == current_user_id
    is_admin_or_pastor = user.role in ['admin', 'pastor', 'pastor_de_rede']
    
    if not (is_admin_or_pastor or is_owner):
        return jsonify({'error': 'Você não tem permissão para excluir este evento.'}), 403
        
    db.session.delete(evento)
    db.session.commit()
    return jsonify({'message': 'Deleted successfully'})

@api.route('/eventos/proximo-batismo', methods=['GET'])
@jwt_required()
def get_proximo_batismo():
    agora = datetime.utcnow()
    from sqlalchemy import or_
    evento = Evento.query.filter(
        Evento.ativo == True,
        Evento.data_fim >= agora,
        or_(
            Evento.is_batismo == True,
            Evento.tipo_evento.ilike('%batismo%'),
            Evento.titulo.ilike('%batismo%')
        )
    ).order_by(Evento.data_inicio).first()

    if not evento:
        return jsonify({'error': 'Nenhum evento de batismo encontrado'}), 404
        
    return jsonify(evento.to_dict())
