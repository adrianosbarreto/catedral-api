from app import create_app, db
from app.models import Convite
from datetime import datetime

app = create_app('production')
with app.app_context():
    token = '_yEWpphdm2ZNCg_v4OmcVw'
    invite = Convite.query.filter_by(token=token).first()
    if invite:
        print(f"Token encontrado!")
        print(f"ID: {invite.id}")
        print(f"IDE_ID: {invite.ide_id}")
        print(f"Expiracao: {invite.data_expiracao}")
        print(f"Usado: {invite.usado}")
        print(f"Valido agora? {invite.esta_valido()}")
        now = datetime.utcnow()
        print(f"Agora (UTC): {now}")
    else:
        print("Token NAO encontrado no banco de dados.")
