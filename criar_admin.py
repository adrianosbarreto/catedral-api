"""
Criar admin com senha compatível com tamanho do campo
"""
from app import create_app, db
from werkzeug.security import generate_password_hash

def criar_admin_sql():
    app = create_app()
    with app.app_context():
        print("👤 Criando admin via SQL direto...")
        
        # Gerar hash da senha com método pbkdf2 (mais curto que scrypt)
        password_hash = generate_password_hash('admin123', method='pbkdf2:sha256')
        
        print(f"Hash length: {len(password_hash)}")
        
        # SQL direto (aspas duplas em "user" - palavra reservada PostgreSQL)
        # Truncar se necessário
        if len(password_hash) > 128:
            print(f"⚠️  Hash muito longo ({len(password_hash)}), truncando para 128")
            password_hash = password_hash[:128]
        
        sql = '''
            INSERT INTO "user" (username, email, password_hash, membro_id)
            VALUES ('admin', 'admin@example.com', :password_hash, NULL)
            ON CONFLICT (username) DO UPDATE 
            SET password_hash = :password_hash, email = 'admin@example.com'
        '''
        
        try:
            db.session.execute(db.text(sql), {'password_hash': password_hash})
            db.session.commit()
            
            print("✅ Usuário admin criado/atualizado com sucesso!")
            print("")
            print("="*50)
            print("🔑 Credenciais de Login:")
            print("   Username: admin")
            print("   Password: admin123")
            print("   Email: admin@example.com")
            print("="*50)
            
        except Exception as e:
            print(f"❌ Erro: {e}")
            db.session.rollback()

if __name__ == '__main__':
    criar_admin_sql()
