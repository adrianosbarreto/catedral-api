from app import create_app, db
from app.models import Convite

app = create_app('production')
with app.app_context():
    token = 'T6iI4NltMMX4NCIrdDfRNw'
    invite = Convite.query.filter_by(token=token).first()
    if invite:
        print(f"Token {token} encontrado!")
        print(f"ID: {invite.id}, IDE: {invite.ide_nome if hasattr(invite, 'ide_nome') else invite.ide_id}, Valido: {invite.esta_valido()}")
    else:
        print(f"Token {token} NAO encontrado.")
