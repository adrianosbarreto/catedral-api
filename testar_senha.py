"""
Testar codificação de senha para URL PostgreSQL
"""
from urllib.parse import quote_plus

senha_original = "Csabe@senha#12345"
senha_encoded = quote_plus(senha_original)

print(f"Senha original: {senha_original}")
print(f"Senha encoded:  {senha_encoded}")
print(f"\nDATABASE_URL correto:")
print(f"postgresql://kaizendev:{senha_encoded}@72.60.0.141:5432/catedral")

# Testar conexão com senha encodada
import psycopg2

try:
    conn = psycopg2.connect(
        host="72.60.0.141",
        port=5432,
        database="catedral",
        user="kaizendev",
        password=senha_original  # Usar senha original, não encoded
    )
    print("\n✅ CONEXÃO ESTABELECIDA!")
    
    cursor = conn.cursor()
    cursor.execute('SELECT COUNT(*) FROM "user";')
    count = cursor.fetchone()
    print(f"✅ Registros na tabela user: {count[0]}")
    
    cursor.close()
    conn.close()
    
except Exception as e:
    print(f"\n❌ ERRO: {e}")
