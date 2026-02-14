"""
Teste de conexão PostgreSQL com IP correto
"""
import psycopg2

print("=" * 70)
print("🔧 TESTE DE CONEXÃO - IP CORRETO: 72.60.0.141")
print("=" * 70)

# Dados de conexão CORRETOS
host = "72.60.0.141"  # IP correto!
port = "5432"
username = "kaizendev"
password = "Csabe@senha#12345"

# Teste com banco 'postgres' primeiro
print("\n1️⃣ Testando conexão ao banco 'postgres':")
print("-" * 70)

try:
    conn = psycopg2.connect(
        host=host,
        port=port,
        dbname="postgres",
        user=username,
        password=password,
        connect_timeout=10
    )
    print(f"✅ CONEXÃO ESTABELECIDA COM SUCESSO!")
    
    cursor = conn.cursor()
    cursor.execute('SELECT version();')
    version = cursor.fetchone()[0]
    print(f"📊 {version.split(',')[0]}")
    
    # Verificar se banco catedral existe
    cursor.execute("SELECT 1 FROM pg_database WHERE datname = 'catedral';")
    exists = cursor.fetchone()
    
    if not exists:
        print(f"\n📋 Banco 'catedral' não existe. Criando...")
        conn.autocommit = True
        cursor.execute("CREATE DATABASE catedral;")
        print(f"✅ Banco 'catedral' criado!")
    else:
        print(f"\n📋 Banco 'catedral' já existe!")
    
    cursor.close()
    conn.close()
    
    # Testar conexão ao banco catedral
    print(f"\n2️⃣ Testando conexão ao banco 'catedral':")
    print("-" * 70)
    
    conn = psycopg2.connect(
        host=host,
        port=port,
        dbname="catedral",
        user=username,
        password=password,
        connect_timeout=10
    )
    print(f"✅ CONEXÃO ao banco 'catedral' OK!")
    
    cursor = conn.cursor()
    cursor.execute("""
        SELECT table_name FROM information_schema.tables 
        WHERE table_schema = 'public';
    """)
    tables = cursor.fetchall()
    
    print(f"\n📋 Tabelas: {len(tables)}")
    for table in tables:
        print(f"   - {table[0]}")
    
    cursor.close()
    conn.close()
    
    print("\n" + "=" * 70)
    print("✅ TUDO PRONTO PARA AS MIGRAÇÕES!")
    print("=" * 70)
    
except Exception as e:
    print(f"❌ ERRO: {e}")
    print("\n" + "=" * 70)
