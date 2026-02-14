"""
Script para atualizar o schema do PostgreSQL com novos tamanhos de campos
"""
import psycopg2
import os
from dotenv import load_dotenv

def fix_schema():
    load_dotenv()
    db_url = os.environ.get('DATABASE_URL')
    
    print(f"🚀 Conectando ao banco para ajustar schema...")
    try:
        conn = psycopg2.connect(db_url)
        conn.autocommit = True
        cursor = conn.cursor()
        
        # Ajustar password_hash
        print("🔧 Ajustando tamanho de password_hash para 255...")
        cursor.execute('ALTER TABLE "user" ALTER COLUMN password_hash TYPE VARCHAR(255);')
        
        # Ajustar CPF e Telefone em membros
        print("🔧 Ajustando tamanho de cpf e telefone para 20...")
        cursor.execute('ALTER TABLE membros ALTER COLUMN cpf TYPE VARCHAR(20);')
        cursor.execute('ALTER TABLE membros ALTER COLUMN telefone TYPE VARCHAR(20);')
        
        print("✅ SCHEMA ATUALIZADO COM SUCESSO!")
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"❌ ERRO AO ATUALIZAR SCHEMA: {e}")

if __name__ == '__main__':
    fix_schema()
