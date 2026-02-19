from app import create_app, db
from app.models import Membro, MembroNucleo, Nucleo, Celula

def check_visitor_data():
    app = create_app()
    with app.app_context():
        print("Checking visitors and their cell links...")
        visitors = Membro.query.filter_by(tipo='visitante', ativo=True).all()
        
        for v in visitors:
            print(f"\nVisitor: {v.nome} (ID: {v.id})")
            print(f"  Membro table -> IDE: {v.ide_id}, Supervisor: {v.supervisor_id}, Lider: {v.lider_id}")
            
            # Check cell links
            links = MembroNucleo.query.filter_by(membro_id=v.id).all()
            if not links:
                print("  ⚠️ Not linked to any cell.")
            for link in links:
                celula = link.nucleo.celula
                print(f"  🔗 Linked to Cell: {celula.nome} (ID: {celula.id})")
                print(f"    Cell -> IDE: {celula.ide_id}, Supervisor: {celula.supervisor_id}")
                
                # Check if hierarchy matches
                match = (v.ide_id == celula.ide_id and v.supervisor_id == celula.supervisor_id)
                if not match:
                    print("    ❌ Hierarchy MISMATCH or MISSING in Membro table.")

if __name__ == '__main__':
    check_visitor_data()
