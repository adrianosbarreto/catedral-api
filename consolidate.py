from app import create_app, db
from app.models import Membro, User, PapelMembro, Endereco

def consolidate_data():
    app = create_app('development')
    with app.app_context():
        # 1. Clean up old duplicates in IDE 1
        # Thaynara Silva (3)
        m3 = db.session.get(Membro, 3)
        if m3:
            print(f"Limpando Thaynara Silva (3)")
            PapelMembro.query.filter_by(membro_id=3).delete()
            Endereco.query.filter_by(membro_id=3).delete()
            User.query.filter_by(membro_id=3).delete()
            db.session.delete(m3)
        
        # Adriano Silva Barreto (4)
        m4 = db.session.get(Membro, 4)
        if m4:
            print(f"Limpando Adriano Silva Barreto (4)")
            PapelMembro.query.filter_by(membro_id=4).delete()
            Endereco.query.filter_by(membro_id=4).delete()
            User.query.filter_by(membro_id=4).delete()
            db.session.delete(m4)

        # 2. Create User for Thaynara (7) if not exists
        m7 = db.session.get(Membro, 7)
        if m7:
            u7 = User.query.filter_by(membro_id=7).first()
            if not u7:
                print(f"Criando usuario para Thaynara (7)")
                new_u = User(
                    username="thaynara",
                    email="thaynara@email.com", # Placeholder, ideally user provides
                    membro_id=7
                )
                new_u.set_password("123456") # Password temporaria
                db.session.add(new_u)
            else:
                print("Usuario para Thaynara ja existe.")
        
        db.session.commit()
        print("Consolidacao concluida!")

if __name__ == "__main__":
    consolidate_data()
