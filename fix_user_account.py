
from app import create_app, db
from app.models import User, Membro

app = create_app('production')

with app.app_context():
    email = 'asb.adrianobarreto@gmail.com'
    cpf = '02216656259'
    
    membro = Membro.query.filter_by(email=email).first()
    if membro:
        print(f"Membro {membro.nome} encontrado.")
        if not membro.cpf:
            membro.cpf = cpf
            print("CPF do membro atualizado.")
        
        user = User.query.filter_by(membro_id=membro.id).first()
        if not user:
            user = User(username=email, membro_id=membro.id)
            user.set_password(cpf)
            db.session.add(user)
            print(f"Conta de usuário criada para {email} com senha {cpf}.")
        else:
            user.set_password(cpf)
            print(f"Usuário {email} já existia. Senha resetada para o CPF.")
        
        db.session.commit()
    else:
        print(f"Membro com e-mail {email} não encontrado.")
