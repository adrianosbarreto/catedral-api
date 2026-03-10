import os
import sys

# Desativar túnel SSH para o script de debug
os.environ['SSH_TUNNEL_ENABLED'] = 'false'

from app import create_app, db
from app.models import Convite, Ide, Membro, Celula

app = create_app('default')
with app.app_context():
    print("--- DEBUG CONVITES ---")
    latest_invites = Convite.query.order_by(Convite.id.desc()).limit(3).all()
    
    for invite in latest_invites:
        data = invite.to_dict()
        print(f"\nID: {invite.id} | Token: {invite.token}")
        print(f"Role Destino: {data.get('role_nome')} ({data.get('papel_destino')})")
        print(f"Pastor: {data.get('pastor_nome')}")
        print(f"Supervisor: {data.get('supervisor_nome')}")
        print(f"Líder: {data.get('lider_nome')}")
        print(f"IDE: {data.get('ide_nome')}")
        print(f"Célula: {data.get('celula_nome')}")
        
        # Inspecionar relacionamentos crus
        ide = invite.ide
        print(f"DEBUG IDE: {ide.nome if ide else 'None'} | Pastor ID: {ide.pastor_id if ide else 'None'}")
        if ide and ide.pastor:
            print(f"DEBUG IDE PASTOR: {ide.pastor.nome}")
            
        print(f"DEBUG CONVITE RAW: Pastor Dest ID: {invite.pastor_destino_id} | Sup Dest ID: {invite.supervisor_destino_id} | Lider Dest ID: {invite.lider_destino_id}")
    
    print("\n--- DEBUG MEMBROS PLACEHOLDERS ---")
    distrito = Membro.query.filter(Membro.nome.ilike('%Distrito%')).first()
    area = Membro.query.filter(Membro.nome.ilike('%Área%')).first()
    print(f"Membro 'Distrito': {'Encontrado' if distrito else 'Não encontrado'}")
    print(f"Membro 'Área': {'Encontrado' if area else 'Não encontrado'}")
