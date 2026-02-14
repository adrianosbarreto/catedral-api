"""
Testar conexão PostgreSQL diretamente
"""
import psycopg2
from dotenv import load_dotenv
import os

load_dotenv()

def testar_postgres():
    db_url = os.getenv('DATABASE_URL')
    print(f"🔗 DATABASE_URL: {db_url}\n")
    
    try:
        # Parse URL
        # postgresql://user:password@host:port/database
        import re
        match = re.match(r'postgresql://([^:]+):([^@]+)@([^:]+):(\d+)/(.+)', db_url)
        
        if match:
            user, password, host, port, database = match.groups()
            print(f"📊 Testando conexão:")
            print(f"   Host: {host}")
            print(f"   Port: {port}")
            print(f"   Database: {database}")
            print(f"   User: {user}\n")
            
            conn = psycopg2.connect(
                host=host,
                port=port,
                database=database,
                user=user,
                password=password
            )
            
            print("✅ Conexão estabelecida!")
            
            # Testar query simples
            cursor = conn.cursor()
            cursor.execute('SELECT version();')
            version = cursor.fetchone()
            print(f"✅ PostgreSQL version: {version[0]}\n")
            
            # Testar query na tabela user
            cursor.execute('SELECT COUNT(*) FROM "user";')
            count = cursor.fetchone()
            print(f"✅ Registros na tabela user: {count[0]}")
            
            cursor.close()
            conn.close()
            print("\n✅ CONEXÃO OK!")
            
        else:
            print("❌ DATABASE_URL inválida!")
            
    except Exception as e:
        print(f"❌ ERRO: {e}")
        print("\n💡 Possíveis soluções:")
        print("   1. Verificar se PostgreSQL está rodando")
        print("   2. Verificar credenciais no .env")
        print("   3. Verificar se porta 5432 está acessível")
        print("   4. Verificar logs do PostgreSQL")

if __name__ == '__main__':
    testar_postgres()
