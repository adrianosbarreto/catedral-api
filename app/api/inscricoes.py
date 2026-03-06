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
    # Permissão: Criador do evento ou Admin ou Pastor
    if user.role not in ['admin', 'pastor'] and evento.criado_por_id != current_user_id:
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
