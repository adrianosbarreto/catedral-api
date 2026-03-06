
from app import create_app, db
from app.models import Evento, InscricaoEvento, User, Membro
from sqlalchemy import inspect

app = create_app()
with app.app_context():
    print("--- Verificação de Banco de Dados ---")
    inspector = inspect(db.engine)
    
    # Verificar colunas em eventos
    cols_eventos = [c['name'] for c in inspector.get_columns('eventos')]
    print(f"Colunas 'eventos': {cols_eventos}")
    if 'perguntas' in cols_eventos:
        print("✓ Coluna 'perguntas' presente na tabela eventos.")
    else:
        print("✗ Coluna 'perguntas' AUSENTE na tabela eventos.")

    # Verificar colunas em inscricoes_eventos
    cols_inscricoes = [c['name'] for c in inspector.get_columns('inscricoes_eventos')]
    print(f"Colunas 'inscricoes_eventos': {cols_inscricoes}")
    if 'respostas' in cols_inscricoes:
        print("✓ Coluna 'respostas' presente na tabela inscricoes_eventos.")
    else:
        print("✗ Coluna 'respostas' AUSENTE na tabela inscricoes_eventos.")

    print("\n--- Teste de Serialização (to_dict) ---")
    evento = Evento.query.first()
    if evento:
        try:
            d = evento.to_dict()
            print(f"✓ Evento {evento.id} serializado com sucesso. Perguntas: {d.get('perguntas')}")
        except Exception as e:
            print(f"✗ Erro ao serializar evento: {e}")
    else:
        print("Aviso: Nenhum evento para testar serialização.")

    inscricao = InscricaoEvento.query.first()
    if inscricao:
        try:
            d = inscricao.to_dict()
            print(f"✓ Inscrição {inscricao.id} serializada com sucesso. Respostas: {d.get('respostas')}")
        except Exception as e:
            print(f"✗ Erro ao serializar inscrição: {e}")
    else:
        print("Aviso: Nenhuma inscrição para testar serialização.")
