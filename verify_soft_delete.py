from app import create_app, db
from app.models import Celula, Membro, Ide
import traceback

app = create_app()

def test_soft_delete():
    with app.app_context():
        try:
            print("--- Iniciando Verificação de Soft Delete ---")
            
            # Garantir Dependências
            print("Verificando dependências...")
            ide = Ide.query.first()
            if not ide:
                print("Criando IDE de teste...")
                ide = Ide(nome="IDE Teste", tipo="MACRO-CELULA")
                db.session.add(ide)
                db.session.commit()
            
            lider = Membro.query.first()
            if not lider:
                print("Criando Líder de teste...")
                lider = Membro(nome="Líder Teste", ide_id=ide.id)
                db.session.add(lider)
                db.session.commit()

            # 1. Testar Celula
            print("\n[1] Testando Célula...")
            celula = Celula(nome="Célula Teste Soft Delete", ide_id=ide.id, lider_id=lider.id, ativo=True)
            db.session.add(celula)
            db.session.commit()
            celula_id = celula.id
            print(f"Célula criada com ID: {celula_id}, Ativo: {celula.ativo}")

            # Simular Delete (API Logic)
            celula = db.session.get(Celula, celula_id)
            celula.ativo = False
            db.session.commit()
            print(f"Célula inativada. Ativo: {celula.ativo}")

            # Verificar Query
            found = Celula.query.filter_by(ativo=True).filter_by(id=celula_id).first()
            print(f"Busca via API Query (ativo=True): {'ENCONTRADO (ERRO)' if found else 'NÃO ENCONTRADO (OK)'}")
            
            db_celula = db.session.get(Celula, celula_id)
            print(f"Busca Direta no DB: {'ENCONTRADO (OK)' if db_celula else 'NÃO ENCONTRADO (ERRO)'}, Status Ativo: {db_celula.ativo}")

            # Limpar Celula
            db.session.delete(db_celula)
            db.session.commit()

            # 2. Testar Membro
            print("\n[2] Testando Membro...")
            membro = Membro(nome="Membro Teste Soft Delete", ide_id=ide.id, ativo=True)
            db.session.add(membro)
            db.session.commit()
            membro_id = membro.id
            print(f"Membro criado com ID: {membro_id}, Ativo: {membro.ativo}")

            # Simular Delete (API Logic)
            membro = db.session.get(Membro, membro_id)
            membro.ativo = False
            db.session.commit()
            print(f"Membro inativado. Ativo: {membro.ativo}")

            # Verificar Query
            found = Membro.query.filter_by(ativo=True).filter_by(id=membro_id).first()
            print(f"Busca via API Query (ativo=True): {'ENCONTRADO (ERRO)' if found else 'NÃO ENCONTRADO (OK)'}")

            db_membro = db.session.get(Membro, membro_id)
            print(f"Busca Direta no DB: {'ENCONTRADO (OK)' if db_membro else 'NÃO ENCONTRADO (ERRO)'}, Status Ativo: {db_membro.ativo}")

            # Limpar Membro
            db.session.delete(db_membro)
            db.session.commit()
            
            print("\n--- Verificação Concluída com Sucesso ---")

        except Exception:
            traceback.print_exc()

if __name__ == '__main__':
    test_soft_delete()
