from flask import Blueprint, jsonify
from flask_login import login_required, current_user

main = Blueprint('main', __name__)

@main.route('/')
def index():
    return jsonify({'message': 'Welcome to Igreja em Foco API', 'user': current_user.username if current_user.is_authenticated else 'Guest'})

@main.route('/api/data')
@login_required
def data():
    return jsonify({'data': 'Secure data access'})
