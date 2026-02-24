
import os
from app import create_app, db
from sqlalchemy import text, inspect

def fix_db():
    # Use config 'production' to get the real DATABASE_URL
    app = create_app('production')
    
    with app.app_context():
        print(f"🔍 Verificando banco de dados: {app.config['SQLALCHEMY_DATABASE_URI']}")
        
        inspector = inspect(db.engine)
        
        # 1. Verificar tabela 'noticias'
        if 'noticias' in inspector.get_table_names():
            columns = [c['name'] for c in inspector.get_columns('noticias')]
            
            # Adicionar 'todas_ides' se não existir
            if 'todas_ides' not in columns:
                print("➕ Adicionando coluna 'todas_ides' à tabela 'noticias'...")
                try:
                    db.session.execute(text("ALTER TABLE noticias ADD COLUMN todas_ides BOOLEAN DEFAULT TRUE"))
                    db.session.commit()
                    print("✅ Coluna 'todas_ides' adicionada.")
                except Exception as e:
                    print(f"❌ Erro ao adicionar coluna 'todas_ides': {e}")
                    db.session.rollback()
            else:
                print("✔ Coluna 'todas_ides' já existe.")
        else:
            print("⚠ Tabela 'noticias' não encontrada. create_all() deve criá-la.")

        # 2. Criar tabelas que não existem (incluindo noticia_ides)
        print("🛠 Executando db.create_all() para garantir que novas tabelas existam...")
        try:
            db.create_all()
            print("✅ db.create_all() concluído com sucesso.")
        except Exception as e:
            print(f"❌ Erro ao executar db.create_all(): {e}")

        # 3. Finalizar
        print("\n✨ Processo de correção concluído!")

if __name__ == '__main__':
    fix_db()
