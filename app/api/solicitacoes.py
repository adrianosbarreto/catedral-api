from flask import jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.api import api
from app.models import db, SolicitacaoTransferencia, Membro, User, MembroNucleo, Nucleo
from datetime import datetime

@api.route('/transferencias/solicitar', methods=['POST'])
@jwt_required()
def solicitar_transferencia():
    data = request.get_json() or {}
    membro_id = data.get('membro_id')
    para_nucleo_id = data.get('para_nucleo_id')
    
    if not membro_id or not para_nucleo_id:
        return jsonify({'error': 'membro_id and para_nucleo_id are required'}), 400
        
    current_user_id = get_jwt_identity()
    
    # Verificar se o membro já está em algum núcleo
    # Buscamos o núcleo atual do membro
    membro_nucleo_atual = MembroNucleo.query.filter_by(membro_id=membro_id).first()
    de_nucleo_id = membro_nucleo_atual.nucleo_id if membro_nucleo_atual else None
    
    # Se já estiver no núcleo de destino, não faz sentido solicitar
    if de_nucleo_id == para_nucleo_id:
        return jsonify({'error': 'Member already in this nucleus'}), 400

    # Criar solicitação
    solicitacao = SolicitacaoTransferencia(
        membro_id=membro_id,
        de_nucleo_id=de_nucleo_id,
        para_nucleo_id=para_nucleo_id,
        solicitante_id=current_user_id,
        status='pendente'
    )
    
    db.session.add(solicitacao)
    db.session.commit()
    
    return jsonify(solicitacao.to_dict()), 201

@api.route('/transferencias/pendentes', methods=['GET'])
@jwt_required()
def get_transferencias_pendentes():
    current_user_id = get_jwt_identity()
    user = db.session.get(User, current_user_id)
    
    if not user or not user.membro:
        return jsonify([])

    # Um líder deve ver solicitações de membros que estão saindo da sua célula
    # 1. Buscar células onde o usuário é líder ou supervisor
    from app.models import Celula
    celulas_ids = []
    
    if user.role == 'admin' or user.role == 'pastor':
        # Admin vê tudo? Talvez não precise. Vamos focar nos líderes.
        solicitacoes = SolicitacaoTransferencia.query.filter_by(status='pendente').all()
        return jsonify([s.to_dict() for s in solicitacoes])

    # Supervisor vê das suas células
    celulas_supervisionadas = Celula.query.filter_by(supervisor_id=user.membro_id).all()
    celulas_ids.extend([c.id for c in celulas_supervisionadas])
    
    # Líder vê da sua própria célula
    celulas_lideradas = Celula.query.filter((Celula.lider_id == user.membro_id) | (Celula.vice_lider_id == user.membro_id)).all()
    celulas_ids.extend([c.id for c in celulas_lideradas])
    
    if not celulas_ids:
        return jsonify([])

    # Agora buscamos os núcleos dessas células
    nucleos_ids = [n.id for n in Nucleo.query.filter(Nucleo.celula_id.in_(celulas_ids)).all()]
    
    # E finalmente as solicitações onde o 'de_nucleo_id' é um desses núcleos
    solicitacoes = SolicitacaoTransferencia.query.filter(
        SolicitacaoTransferencia.de_nucleo_id.in_(nucleos_ids),
        SolicitacaoTransferencia.status == 'pendente'
    ).all()
    
    return jsonify([s.to_dict() for s in solicitacoes])

@api.route('/transferencias/<int:id>/responder', methods=['POST'])
@jwt_required()
def responder_transferencia(id):
    data = request.get_json() or {}
    acao = data.get('acao') # 'aceitar' ou 'recusar'
    motivo = data.get('motivo')
    
    solicitacao = db.session.get(SolicitacaoTransferencia, id)
    if not solicitacao or solicitacao.status != 'pendente':
        return jsonify({'error': 'Valid pendidng solicitation not found'}), 404
        
    if acao == 'aceitar':
        solicitacao.status = 'aceito'
        solicitacao.data_resposta = datetime.utcnow()
        
        # Efetivar a transferência
        # 1. Remover vínculo anterior
        MembroNucleo.query.filter_by(membro_id=solicitacao.membro_id).delete()
        
        # 2. Criar novo vínculo
        novo_vinculo = MembroNucleo(
            nucleo_id=solicitacao.para_nucleo_id,
            membro_id=solicitacao.membro_id
        )
        db.session.add(novo_vinculo)
        
        # 3. Atualizar ide_id e lider_id do membro para os novos valores
        membro = db.session.get(Membro, solicitacao.membro_id)
        para_celula = solicitacao.para_nucleo.celula
        membro.ide_id = para_celula.ide_id
        membro.lider_id = para_celula.lider_id
        
    elif acao == 'recusar':
        solicitacao.status = 'recusado'
        solicitacao.data_resposta = datetime.utcnow()
        solicitacao.motivo_recusa = motivo
    else:
        return jsonify({'error': 'Invalid action'}), 400
        
    db.session.commit()
    return jsonify(solicitacao.to_dict())
