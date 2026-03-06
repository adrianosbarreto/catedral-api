
from app import create_app, db
from sqlalchemy import text
from app.models import User, Membro, Evento, InscricaoEvento

app = create_app('production')

with app.app_context():
    print("--- Verificando Colunas de 'eventos' ---")
    try:
        result = db.session.execute(text("SELECT column_name FROM information_schema.columns WHERE table_name = 'eventos'"))
        columns = [row[0] for row in result]
        print(f"Colunas encontradas: {columns}")
        print(f"tipo_visibilidade presente? {'tipo_visibilidade' in columns}")
    except Exception as e:
        print(f"Erro ao verificar 'eventos': {e}")

    print("\n--- Verificando Colunas de 'inscricoes_eventos' ---")
    try:
        result = db.session.execute(text("SELECT column_name FROM information_schema.columns WHERE table_name = 'inscricoes_eventos'"))
        columns = [row[0] for row in result]
        print(f"Colunas encontradas: {columns}")
        print(f"cpf_externo presente? {'cpf_externo' in columns}")
    except Exception as e:
        print(f"Erro ao verificar 'inscricoes_eventos': {e}")

    print("\n--- Verificando Usuário ---")
    user = User.query.filter_by(username='asb.adrianobarreto@gmail.com').first()
    if user:
        print(f"Usuário encontrado! ID: {user.id}")
        membro = Membro.query.get(user.membro_id)
        if membro:
            print(f"Membro associado: {membro.nome}, CPF: {membro.cpf}")
        else:
            print("Nenhum membro associado.")
    else:
        print("Usuário 'asb.adrianobarreto@gmail.com' não encontrado.")

    print("\n--- Verificando Inscrições do Evento 8 ---")
    inscricoes = InscricaoEvento.query.filter_by(evento_id=8).all()
    print(f"Total de inscrições para o evento 8: {len(inscricoes)}")
