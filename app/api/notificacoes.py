from flask import request, jsonify, current_app
from app.api import api
from app import db
from app.models import NotificationSubscription, User, PushMessage, Membro
from flask_jwt_extended import jwt_required, get_jwt_identity
import json
import logging
import os
from datetime import datetime, timezone
from pywebpush import webpush, WebPushException
from app import scheduler

logger = logging.getLogger(__name__)

# Helper function to run the actual push dispatch
def dispatch_push_task(message_id):
    from app import scheduler, db
    from app.models import PushMessage, NotificationSubscription, User, Membro

    if not scheduler or not scheduler.app:
        logger.error("Job ran outside of scheduler application context.")
        return

    with scheduler.app.app_context():
        msg = PushMessage.query.get(message_id)
        if not msg or msg.status != 'scheduled':
            return
            
        vapid_private_key = os.environ.get('VAPID_PRIVATE_KEY')
        if not vapid_private_key:
            logger.error('VAPID Base config is missing in server')
            msg.status = 'failed'
            db.session.commit()
            return
            
        vapid_claims = {"sub": "mailto:admin@catedral.com"}
        
        # Build query for subscriptions
        subs_query = NotificationSubscription.query.join(User, NotificationSubscription.user_id == User.id)
        
        if msg.target_ide_id or msg.target_supervisor_id:
            subs_query = subs_query.join(Membro, User.membro_id == Membro.id)
            if msg.target_ide_id:
                subs_query = subs_query.filter(Membro.ide_id == msg.target_ide_id)
            if msg.target_supervisor_id:
                subs_query = subs_query.filter(Membro.supervisor_id == msg.target_supervisor_id)
                
        subs = subs_query.all()
        
        count_success = 0
        count_failed = 0
        
        for sub in subs:
            sub_info = {
                "endpoint": sub.endpoint,
                "keys": {
                    "p256dh": sub.p256dh,
                    "auth": sub.auth
                }
            }
            try:
                webpush(
                    subscription_info=sub_info,
                    data=json.dumps({"title": msg.title, "body": msg.body, "url": msg.url, "icon": '/logo.png'}),
                    vapid_private_key=vapid_private_key,
                    vapid_claims=vapid_claims
                )
                count_success += 1
            except WebPushException as ex:
                logger.error(f"WebPush Error: {ex}")
                count_failed += 1
                if ex.response and ex.response.status_code in [404, 410]:
                    db.session.delete(sub)
                    
        msg.success_count = count_success
        msg.failed_count = count_failed
        msg.status = 'sent'
        db.session.commit()
        logger.info(f"Push Message {msg.id} dispatched: {count_success} success, {count_failed} failed.")

@api.route('/notifications/subscribe', methods=['POST'])
@jwt_required(optional=True)
def subscribe():
    data = request.get_json()
    if not data or 'subscription' not in data:
        return jsonify({'error': 'Subscription data missing'}), 400

    subscription = data['subscription']
    endpoint = subscription.get('endpoint')
    keys = subscription.get('keys', {})
    p256dh = keys.get('p256dh')
    auth = keys.get('auth')

    if not endpoint or not p256dh or not auth:
        return jsonify({'error': 'Invalid subscription object'}), 400

    current_user = get_jwt_identity()
    user_id = current_user if current_user else None

    # Verifica se já existe a mesma subscrição pelo endpoint
    existing_sub = NotificationSubscription.query.filter_by(endpoint=endpoint).first()
    
    if existing_sub:
        # Atualiza usuário se mudou
        if existing_sub.user_id != user_id:
            existing_sub.user_id = user_id
            db.session.commit()
        return jsonify({'message': 'Subscription already exists and updated'}), 200
    
    # Criar nova
    new_sub = NotificationSubscription(
        user_id=user_id,
        endpoint=endpoint,
        p256dh=p256dh,
        auth=auth
    )
    db.session.add(new_sub)
    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        logger.error(f"Erro ao salvar subscription: {e}")
        return jsonify({'error': 'Failed to save subscription'}), 500

    return jsonify({'message': 'Subscription created successfully', 'id': new_sub.id}), 201

@api.route('/notifications/unsubscribe', methods=['POST'])
@jwt_required(optional=True)
def unsubscribe():
    data = request.get_json()
    endpoint = data.get('endpoint') if data else None
    if not endpoint:
        return jsonify({'error': 'Endpoint required'}), 400

    sub = NotificationSubscription.query.filter_by(endpoint=endpoint).first()
    if sub:
        db.session.delete(sub)
        db.session.commit()
    
    return jsonify({'message': 'Unsubscribed'}), 200

@api.route('/notifications/history', methods=['GET'])
@jwt_required()
def notification_history():
    current_user = get_jwt_identity()
    user = User.query.get(current_user)
    if not user or user.role not in ['admin', 'pastor_de_rede', 'pastor']:
        return jsonify({'error': 'Unauthorized'}), 403
        
    messages = PushMessage.query.order_by(PushMessage.created_at.desc()).all()
    return jsonify([m.to_dict() for m in messages]), 200

@api.route('/notifications/send', methods=['POST'])
@jwt_required()
def send_notification():
    current_user = get_jwt_identity()
    user = User.query.get(current_user)
    
    # Validação de admin
    if not user or user.role not in ['admin', 'pastor_de_rede', 'pastor']:
        return jsonify({'error': 'Unauthorized'}), 403

    data = request.get_json()
    title = data.get('title', 'Nova Notificação')
    body = data.get('body', 'Você tem uma nova mensagem')
    url = data.get('url', '/admin')
    icon = data.get('icon', '/logo.png')
    target_ide_id = data.get('target_ide_id')
    target_supervisor_id = data.get('target_supervisor_id')
    scheduled_for_str = data.get('scheduled_for')
    
    now_utc = datetime.now(timezone.utc)
    
    scheduled_for = None
    if scheduled_for_str:
        try:
            # Assumindo formato ISO8601
            scheduled_for = datetime.fromisoformat(scheduled_for_str.replace('Z', '+00:00'))
            if not scheduled_for.tzinfo:
                scheduled_for = scheduled_for.replace(tzinfo=timezone.utc)
        except Exception as e:
            return jsonify({'error': f'Invalid scheduled_for format: {e}'}), 400

    if not scheduled_for or scheduled_for <= now_utc:
        status = 'scheduled'
        scheduled_for = now_utc
        is_immediate = True
    else:
        is_immediate = False

    msg = PushMessage(
        title=title,
        body=body,
        url=url,
        sent_by_id=user.id,
        status=status,
        scheduled_for=scheduled_for.replace(tzinfo=None), # save naive UTC to DB
        target_ide_id=target_ide_id,
        target_supervisor_id=target_supervisor_id
    )
    db.session.add(msg)
    db.session.commit()

    if is_immediate:
        scheduler.add_job(id=f'push_{msg.id}', func=dispatch_push_task, args=[msg.id], trigger='date', run_date=now_utc)
    else:
        scheduler.add_job(id=f'push_{msg.id}', func=dispatch_push_task, args=[msg.id], trigger='date', run_date=scheduled_for)

    return jsonify({
        'message': 'Push message registered successfully',
        'push_message_id': msg.id,
        'status': msg.status,
        'scheduled_for': msg.scheduled_for.isoformat() if msg.scheduled_for else None
    }), 201

@api.route('/notifications/vapid-public-key', methods=['GET'])
def vapid_public_key():
    import os
    public_key = os.environ.get('VAPID_PUBLIC_KEY')
    if not public_key:
        return jsonify({'error': 'Public Key not configured'}), 500
    return jsonify({'publicKey': public_key}), 200
