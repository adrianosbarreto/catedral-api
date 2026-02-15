from app import create_app, db
from app.models import User

app = create_app('development')
with app.app_context():
    # Atualizar nulos para False
    User.query.filter(User.requer_troca_senha == None).update({User.requer_troca_senha: False})
    db.session.commit()
    print("✅ Registros antigos atualizados para False")
