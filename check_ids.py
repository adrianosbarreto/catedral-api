import os
import sys

# Desativar túnel SSH para o script de debug
os.environ['SSH_TUNNEL_ENABLED'] = 'false'

from app import create_app, db
from app.models import Membro, Convite

app = create_app('default')
with app.app_context():
    print("--- VERIFICAÇÃO DE IDs CITADOS ---")
    
    ids_to_check = [5, 17, 24]
    for mid in ids_to_check:
        membro = db.session.get(Membro, mid)
        if membro:
            print(f"ID {mid}: {membro.nome}")
        else:
            print(f"ID {mid}: NÃO ENCONTRADO")
            
    print("\n--- DETALHES DO CONVITE 304 ---")
    invite = db.session.get(Convite, 304)
    if invite:
        data = invite.to_dict()
        print(f"ID: {invite.id}")
        print(f"Pastor Destino ID: {invite.pastor_destino_id} -> Nome: {data.get('pastor_nome')}")
        print(f"Supervisor Destino ID: {invite.supervisor_destino_id} -> Nome: {data.get('supervisor_nome')}")
        print(f"Líder Destino ID: {invite.lider_destino_id} -> Nome: {data.get('lider_nome')}")
        print(f"Token: {invite.token}")
    else:
        print("Convite 304 NÃO ENCONTRADO")
