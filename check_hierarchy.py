from app import db, create_app
from app.models import Celula, Membro, Ide
import os

app = create_app()
with app.app_context():
    try:
        # Verificando a célula 12
        c = db.session.get(Celula, 12)
        if not c:
            print("Célula 12 não encontrada")
        else:
            print(f"--- Célula ID: {c.id} ---")
            print(f"Nome: {c.nome}")
            print(f"Lider ID: {c.lider_id}")
            if c.lider:
                print(f"Lider Nome: {c.lider.nome}")
                print(f"Lider -> Pastor_id: {c.lider.pastor_id}")
                if c.lider.pastor_id_rel:
                    print(f"Lider -> Pastor Nome: {c.lider.pastor_id_rel.nome}")
                else:
                    print("Lider -> Pastor_id_rel é None")
            
            print(f"IDE ID: {c.ide_id}")
            if c.ide:
                print(f"IDE Nome: {c.ide.nome}")
                print(f"IDE -> Pastor_id: {c.ide.pastor_id}")
                if c.ide.pastor:
                    print(f"IDE -> Pastor Nome: {c.ide.pastor.nome}")
            
            print("\n--- Resultado do to_dict() ---")
            d = c.to_dict()
            print(f"pastor_id: {d.get('pastor_id')}")
            print(f"pastor_nome: {d.get('pastor_nome')}")
            
            # Verificar Membro 24 especificamente
            m24 = db.session.get(Membro, 24)
            if m24:
                print(f"\n--- Membro ID: 24 ---")
                print(f"Nome: {m24.nome}")
                print(f"Pastor_id: {m24.pastor_id}")
                print(f"Pastor Nome: {m24.pastor_id_rel.nome if m24.pastor_id_rel else 'None'}")
    except Exception as e:
        print(f"Erro ao executar verificação: {e}")
