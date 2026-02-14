"""
Script para executar migrações do banco de dados
"""
from app import create_app, db
from flask_migrate import upgrade

app = create_app('development')  # Usar development para carregar config do .env

print("🔄 Conectando ao banco de dados PostgreSQL...")
print(f"📍 DATABASE_URL: {app.config['SQLALCHEMY_DATABASE_URI'][:50]}...")

with app.app_context():
    print("🔨 Executando migrações...")
    try:
        upgrade()
        print("✅ Migrações executadas com sucesso!")
        
        # Verificar tabelas criadas
        from sqlalchemy import inspect
        inspector = inspect(db.engine)
        tables = inspector.get_table_names()
        print(f"\n📊 Tabelas criadas no banco de dados:")
        for table in tables:
            print(f"  - {table}")
            
    except Exception as e:
        print(f"❌ Erro ao executar migrações: {e}")
        raise
