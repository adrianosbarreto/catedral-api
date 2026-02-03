from flask import Blueprint, request, jsonify
from app import db
from app.models import User, Membro, PapelMembro, Endereco, Ide, Convite
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
import secrets
from datetime import datetime, timedelta

auth = Blueprint('auth', __name__)

@auth.route('/public/ides', methods=['GET'])
def get_public_ides():
    ides = Ide.query.all()
    return jsonify([{'id': ide.id, 'nome': ide.nome} for ide in ides])

@auth.route('/invite/<token>', methods=['GET'])
def validate_invite(token):
    invite = Convite.query.filter_by(token=token).first()
    if not invite or not invite.esta_valido():
        return jsonify({'error': 'Convite inválido ou expirado'}), 400
    return jsonify(invite.to_dict())

@auth.route('/invite', methods=['POST'])
@jwt_required()
def generate_invite():
    current_user_id = get_jwt_identity()
    user = db.session.get(User, current_user_id)
    
    # Check if user can generate invite (Pastor or Supervisor)
    allowed_roles = ['pastor', 'supervisor', 'admin']
    if user.role not in allowed_roles:
        return jsonify({'error': 'Ação não permitida para seu cargo'}), 403

    data = request.get_json()
    ide_id = data.get('ide_id')
    if not ide_id:
        # Default to user's IDE if supervisor
        if user.membro and user.membro.ide_id:
            ide_id = user.membro.ide_id
        elif user.role == 'admin':
            first_ide = Ide.query.first()
            if first_ide:
                ide_id = first_ide.id
    
    if not ide_id:
        return jsonify({'error': 'IDE_ID é obrigatório'}), 400

    now = datetime.utcnow()
    # "expire no proximo dia" -> Tomorrow at 23:59:59
    data_expiracao = (now + timedelta(days=1)).replace(hour=23, minute=59, second=59, microsecond=999999)

    token = secrets.token_urlsafe(16)
    invite = Convite(
        token=token,
        ide_id=ide_id,
        criado_por_id=user.id,
        data_expiracao=data_expiracao
    )
    db.session.add(invite)
    try:
        db.session.commit()
        return jsonify({'token': token, 'invite_url': f'/register?token={token}'}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@auth.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    if not data:
        return jsonify({'error': 'Missing data'}), 400

    required = ['nome', 'email', 'cpf', 'password', 'papel']
    for field in required:
        if field not in data:
            return jsonify({'error': f'Missing {field}'}), 400

    token = data.get('invite_token')
    invite = None
    ide_id = data.get('ide_id')

    if token:
        invite = Convite.query.filter_by(token=token).first()
        if not invite or not invite.esta_valido():
            return jsonify({'error': 'Token de convite inválido ou expirado'}), 400
        
        ide_id = invite.ide_id

    if not ide_id:
        return jsonify({'error': 'IDE_ID é obrigatório (ou use um link de convite)'}), 400

    # Restrict roles for self-registration
    allowed_roles = ['supervisor', 'lider_de_celula', 'vice_lider_de_celula']
    if data['papel'] not in allowed_roles:
        return jsonify({'error': 'Invalid role for self-registration'}), 403

    # Check if user already exists
    if User.query.filter((User.email == data['email']) | (User.username == data['email'])).first():
        return jsonify({'error': 'User already exists'}), 400

    try:
        # Date parsing helper
        def parse_date(date_str):
            if not date_str: return None
            try:
                return datetime.strptime(date_str, '%Y-%m-%d').date()
            except ValueError:
                return None

        # 1. Create Membro
        membro = Membro(
            nome=data['nome'],
            email=data['email'],
            telefone=data.get('telefone'),
            cpf=data['cpf'],
            estado_civil=data.get('estado_civil'),
            data_nascimento=parse_date(data.get('data_nascimento')),
            data_batismo=parse_date(data.get('data_batismo')),
            ide_id=ide_id,
            ativo=True
        )
        db.session.add(membro)
        db.session.flush()

        # 2. Add Role
        papel = PapelMembro(membro_id=membro.id, papel=data['papel'])
        db.session.add(papel)

        # 3. Add Address
        endereco = Endereco(
            membro_id=membro.id,
            logradouro=data.get('logradouro'),
            numero=data.get('numero'),
            bairro=data.get('bairro'),
            cidade=data.get('cidade'),
            estado=data.get('estado'),
            cep=data.get('cep')
        )
        db.session.add(endereco)

        # 4. Create User
        user = User(
            username=data['email'], # Use email as username for simplicity
            email=data['email'],
            membro_id=membro.id
        )
        user.set_password(data['password'])
        db.session.add(user)

        # 5. Mark invite as used
        if invite:
            invite.usado = True

        db.session.commit()
        return jsonify({'message': 'User registered successfully'}), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@auth.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    if not data or 'username' not in data or 'password' not in data:
        return jsonify({'error': 'Missing username or password'}), 400

    username = data.get('username')
    password = data.get('password')

    user = User.query.filter_by(username=username).first()
    if not user and '@' in username: # Check by email if username looks like email
         user = User.query.filter_by(email=username).first()

    if not user or not user.check_password(password):
        return jsonify({'error': 'Invalid credentials'}), 401

    access_token = create_access_token(identity=str(user.id))

    # Fetch permissions
    permissions = []
    from app.models import Role
    role_obj = Role.query.filter_by(name=user.role).first()
    if role_obj:
            permissions = [p.name for p in role_obj.permissions]

    return jsonify({
        'access_token': access_token,
        'user': {
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'role': user.role,
            'ide_id': user.membro.ide_id if user.membro else None,
            'permissions': permissions
        }
    })

@auth.route('/me', methods=['GET'])
@jwt_required()
def me():
    current_user_id = get_jwt_identity()
    user = db.session.get(User, current_user_id)
    
    if user:
        # Fetch permissions
        permissions = []
        from app.models import Role
        # user.role returns string. Need Role object.
        role_obj = Role.query.filter_by(name=user.role).first()
        if role_obj:
             permissions = [p.name for p in role_obj.permissions]

        return jsonify({
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'role': user.role,
                'ide_id': user.membro.ide_id if user.membro else None,
                'permissions': permissions
            }
        })
    return jsonify({'user': None}), 404
