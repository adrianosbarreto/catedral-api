
from app import create_app, db
from app.models import User, Membro

app = create_app('production')

with app.app_context():
    email = 'asb.adrianobarreto@gmail.com'
    print(f"--- Pesquisando Membro por Email: {email} ---")
    membro = Membro.query.filter_by(email=email).first()
    if membro:
        print(f"Membro encontrado! ID: {membro.id}, Nome: {membro.nome}, CPF: {membro.cpf}")
        user = User.query.filter_by(membro_id=membro.id).first()
        if user:
            print(f"Usuário associado encontrado: {user.username}")
        else:
            print("Membro existe, mas NÃO tem conta de usuário (User).")
            # Vamos verificar se existe um user com este username (mesmo que sem membro_id correto)
            user_by_name = User.query.filter_by(username=email).first()
            if user_by_name:
                print(f"Existe um usuário com este e-mail ({email}), mas o membro_id é {user_by_name.membro_id}")
            else:
                print(f"Nenhum usuário com username {email} foi encontrado.")
    else:
        print(f"Nenhum Membro encontrado com o e-mail {email}.")

    print("\n--- Pesquisando Membro por CPF (se houver) ---")
    # Tentando achar algum membro com CPF 02216656259
    membro_cpf = Membro.query.filter_by(cpf='02216656259').first()
    if membro_cpf:
        print(f"Membro encontrado pelo CPF! ID: {membro_cpf.id}, Nome: {membro_cpf.nome}, Email: {membro_cpf.email}")
    else:
        print("Nenhum Membro encontrado com este CPF.")
