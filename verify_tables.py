"""
Verificar tabelas criadas no PostgreSQL
"""
import os
from dotenv import load_dotenv
from app import create_app, db
from sqlalchemy import inspect

load_dotenv()

app = create_app('development')

print("=" * 70)
print("📊 VERIFICANDO TABELAS NO POSTGRESQL")
print("=" * 70)

with app.app_context():
    # Criar todas as tabelas baseado nos models
    print("\n🔨 Criando tabelas a partir dos models...")
    db.create_all()
    print("✅ Tabelas criadas/verificadas!")
    
    # Listar todas as tabelas
    inspector = inspect(db.engine)
    tables = inspector.get_table_names()
    
    print(f"\n📋 Tabelas no banco 'catedral' ({len(tables)}):")
    print("-" * 70)
    
    for table in sorted(tables):
        # Pegar colunas da tabela
        columns = inspector.get_columns(table)
        print(f"\n📄 {table}")
        print(f"   Colunas: {len(columns)}")
        for col in columns[:5]:  # Mostrar primeiras 5 colunas
            print(f"      - {col['name']}: {col['type']}")
        if len(columns) > 5:
            print(f"      ... e mais {len(columns) - 5} colunas")
    
    print("\n" + "=" * 70)
    print("✅ MIGRAÇÃO PARA POSTGRESQL COMPLETA!")
    print("=" * 70)
    print(f"\n🚀 Para iniciar o servidor de produção:")
    print(f"   uv run python server.py")
    print(f"\n🛠️ Para desenvolvimento:")
    print(f"   uv run python run.py")
    print("\n" + "=" * 70)
