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
    allowed_roles = ['pastor', 'pastor_de_rede', 'supervisor', 'admin']
    if user.role not in allowed_roles:
        return jsonify({'error': 'Ação não permitida para seu cargo'}), 403

    data = request.get_json()
    ide_id = data.get('ide_id')
    papel_destino = data.get('papel_destino')
    supervisor_id = data.get('supervisor_id') # Opcional: só para Pastor convidando Líder

    # Validação de Hierarquia
    hierarchy = {
        'admin': ['pastor_de_rede', 'supervisor', 'lider_de_celula', 'vice_lider_de_celula'],
        'pastor_de_rede': ['supervisor', 'lider_de_celula'],
        'pastor': ['supervisor', 'lider_de_celula'],
        'supervisor': ['lider_de_celula'],
        'lider_de_celula': ['vice_lider_de_celula']
    }

    user_role = user.role
    if user_role not in hierarchy:
        return jsonify({'error': f'Seu cargo ({user_role}) não tem permissão para gerar convites'}), 403

    if papel_destino not in hierarchy.get(user_role, []):
        return jsonify({'error': f'Você não tem permissão para convidar um {papel_destino}'}), 403

    if not ide_id:
        # Default to user's IDE if supervisor/pastor
        if user.membro and user.membro.ide_id:
            ide_id = user.membro.ide_id
        elif user.role == 'admin':
            first_ide = Ide.query.first()
            if first_ide:
                ide_id = first_ide.id
    
    if not ide_id:
        return jsonify({'error': 'IDE_ID é obrigatório'}), 400

    now = datetime.utcnow()
    data_expiracao = (now + timedelta(days=1)).replace(hour=23, minute=59, second=59, microsecond=999999)

    token = secrets.token_urlsafe(16)
    invite = Convite(
        token=token,
        ide_id=ide_id,
        criado_por_id=user.id,
        data_expiracao=data_expiracao,
        papel_destino=papel_destino,
        supervisor_destino_id=supervisor_id
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

    # Validação de Token e IDE
    token = data.get('invite_token')
    invite = None
    ide_id = data.get('ide_id')
    papel = data.get('papel')

    if token:
        invite = Convite.query.filter_by(token=token).first()
        if not invite or not invite.esta_valido():
            return jsonify({'error': 'Link de convite inválido ou expirado'}), 400
        
        ide_id = invite.ide_id
        if invite.papel_destino:
            papel = invite.papel_destino

    if not ide_id:
        return jsonify({'error': 'A identificação da IDE é obrigatória'}), 400

    # Restringir papéis para auto-cadastro sem token
    if not token:
        allowed_roles = ['supervisor', 'lider_de_celula', 'vice_lider_de_celula']
        if papel not in allowed_roles:
            return jsonify({'error': 'Cargo inválido para cadastro sem convite'}), 403

    # Verificação detalhada de duplicidade
    if User.query.filter((User.email == data['email']) | (User.username == data['email'])).first():
        return jsonify({'error': f"Já existe um usuário cadastrado com o e-mail {data['email']}"}), 400
    
    if Membro.query.filter_by(cpf=data['cpf']).first():
        return jsonify({'error': f"Já existe um membro cadastrado com o CPF {data['cpf']}"}), 400

    try:
        # Auxiliar de data
        def parse_date(date_str):
            if not date_str: return None
            try:
                return datetime.strptime(date_str, '%Y-%m-%d').date()
            except ValueError:
                return None

        # 1. Criar Membro
        lider_id = invite.criador.membro_id if invite and invite.criador else None
        if invite and invite.supervisor_destino_id:
            lider_id = invite.supervisor_destino_id

        membro = Membro(
            nome=data['nome'],
            email=data['email'],
            telefone=data.get('telefone'),
            cpf=data['cpf'],
            estado_civil=data.get('estado_civil'),
            sexo=data.get('sexo'),
            data_nascimento=parse_date(data.get('data_nascimento')),
            data_batismo=parse_date(data.get('data_batismo')),
            ide_id=ide_id,
            lider_id=lider_id,
            ativo=True
        )
        db.session.add(membro)
        db.session.flush()

        # 2. Adicionar Papel
        papel_obj = PapelMembro(membro_id=membro.id, papel=papel)
        db.session.add(papel_obj)

        # 3. Adicionar Endereço
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

        # 4. Criar Usuário
        user = User(
            username=data['email'],
            email=data['email'],
            membro_id=membro.id
        )
        user.set_password(data['password'])
        db.session.add(user)

        # 5. Marcar convite como usado
        if invite:
            invite.usado = True

        db.session.commit()
        return jsonify({'message': 'Usuário registrado com sucesso'}), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f"Erro interno: {str(e)}"}), 500

@auth.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    if not data or 'username' not in data or 'password' not in data:
        return jsonify({'error': 'Usuário e senha são obrigatórios'}), 400

    username = data.get('username')
    password = data.get('password')

    user = User.query.filter_by(username=username).first()
    if not user and '@' in username:
         user = User.query.filter_by(email=username).first()

    if not user or not user.check_password(password):
        return jsonify({'error': 'Usuário ou senha inválidos'}), 401

    access_token = create_access_token(identity=str(user.id))

    # Fetch permissions
    permissions = []
    from app.models import Role
    role_obj = Role.query.filter_by(name=user.role).first()
    if role_obj:
            permissions = [p.name for p in role_obj.permissions]

    user_data = {
        'id': user.id,
        'username': user.username,
        'nome': user.membro.nome if user.membro else user.username,
        'email': user.email,
        'role': user.role,
        'ide_id': user.membro.ide_id if user.membro else None,
        'membro_id': user.membro.id if user.membro else None,
        'supervisor_id': user.membro.supervisor_id if user.membro else None,
        'permissions': permissions,
        'requer_troca_senha': user.requer_troca_senha
    }
    print(f"DEBUG LOGIN - User: {user.username}, Nome: {user_data['nome']}")
    return jsonify({
        'access_token': access_token,
        'user': user_data
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

        user_data = {
            'id': user.id,
            'username': user.username,
            'nome': user.membro.nome if user.membro else user.username,
            'email': user.email,
            'role': user.role,
            'ide_id': user.membro.ide_id if user.membro else None,
            'membro_id': user.membro.id if user.membro else None,
            'supervisor_id': user.membro.supervisor_id if user.membro else None,
            'permissions': permissions,
            'requer_troca_senha': user.requer_troca_senha
        }
        print(f"DEBUG ME - User: {user.username}, Nome: {user_data['nome']}")
        return jsonify({
            'user': user_data
        })
    return jsonify({'user': None}), 404

@auth.route('/reset-password/<int:membro_id>', methods=['POST'])
@jwt_required()
def reset_password(membro_id):
    current_user_id = get_jwt_identity()
    current_user = db.session.get(User, current_user_id)
    
    # Check permissions (admin, pastor, supervisor)
    allowed_roles = ['admin', 'pastor', 'pastor_de_rede', 'supervisor']
    if current_user.role not in allowed_roles:
        return jsonify({'error': 'Ação não permitida para seu cargo'}), 403

    target_user = User.query.filter_by(membro_id=membro_id).first()
    
    if not target_user:
        target_membro = db.session.get(Membro, membro_id)
        if not target_membro:
            return jsonify({'error': 'Membro não encontrado'}), 404
            
        # Verificar se o membro tem papel de liderança
        leadership_roles = ['admin', 'pastor', 'pastor_de_rede', 'supervisor', 'lider_de_celula', 'vice_lider_de_celula']
        membro_papel = target_membro.papeis.first().papel if target_membro.papeis.first() else 'membro'
        
        if membro_papel not in leadership_roles:
            return jsonify({'error': f'O membro {target_membro.nome} possui o cargo de "{membro_papel}" e não necessita de acesso ao sistema.'}), 400

        if not target_membro.email:
            return jsonify({'error': f'O membro {target_membro.nome} não possui e-mail cadastrado para criar a conta.'}), 400

        # Criar Usuário automaticamente para liderança
        target_user = User(
            username=target_membro.email,
            email=target_membro.email,
            membro_id=target_membro.id
        )
        db.session.add(target_user)
        message_suffix = " (Conta criada agora para este líder)"
    else:
        message_suffix = ""

    # Gerar senha aleatória de 8 caracteres
    import string
    alphabet = string.ascii_letters + string.digits
    new_password = ''.join(secrets.choice(alphabet) for _ in range(8))
    
    target_user.set_password(new_password)
    target_user.requer_troca_senha = True
    
    try:
        db.session.commit()
        return jsonify({
            'message': f'Senha resetada com sucesso{message_suffix}',
            'new_password': new_password
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Erro ao processar reset: {str(e)}'}), 500

@auth.route('/change-password', methods=['POST'])
@jwt_required()
def change_password():
    current_user_id = get_jwt_identity()
    user = db.session.get(User, current_user_id)
    
    data = request.get_json()
    new_password = data.get('password')
    
    if not new_password or len(new_password) < 6:
        return jsonify({'error': 'A senha deve ter pelo menos 6 caracteres'}), 400
        
    user.set_password(new_password)
    user.requer_troca_senha = False
    
    try:
        db.session.commit()
        return jsonify({'message': 'Senha alterada com sucesso'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Erro ao alterar senha: {str(e)}'}), 500
