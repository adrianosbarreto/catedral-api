from app import create_app, db
from app.models import Membro, User, Role, Ide, Celula, PapelMembro
from app.scopes import MembroScope, CellScope

def check_db():
    app = create_app()
    with app.app_context():
        print("Checking Pastores de Rede...")
        role_obj = Role.query.filter_by(name='pastor_de_rede').first()
        role_id = role_obj.id if role_obj else None
        
        pastores = Membro.query.join(PapelMembro).filter(
            (PapelMembro.papel == 'pastor_de_rede') | (PapelMembro.role_id == role_id)
        ).all()
        
        print(f"Found {len(pastores)} pastores de rede.")
        for p in pastores:
            ides = p.ides_lideradas.all()
            print(f"Pastor: {p.nome} (ID: {p.id})")
            print(f"  IDEs: {[ide.nome for ide in ides]}")
            
            if p.user:
                m_count = MembroScope.apply(Membro.query.filter_by(ativo=True), p.user).count()
                c_count = CellScope.apply(Celula.query.filter_by(ativo=True), p.user).count()
                print(f"  Visible Members: {m_count}")
                print(f"  Visible Cells: {c_count}")
            else:
                print("  No user record.")

if __name__ == '__main__':
    check_db()
