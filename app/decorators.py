from functools import wraps
from flask import jsonify
from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity
from app import db
from app.models import User

def requires_permission(permission_name):
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            try:
                verify_jwt_in_request()
            except Exception as e:
                return jsonify({'error': 'Missing or invalid token'}), 401
            
            user_id = get_jwt_identity()
            user = db.session.get(User, user_id)
            
            if not user:
                 return jsonify({'error': 'User not found'}), 404
            
            if not user.has_permission(permission_name):
                return jsonify({'error': 'Insufficient permissions'}), 403
            
            return fn(*args, **kwargs)
        return wrapper
    return decorator
