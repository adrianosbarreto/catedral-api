
from app import create_app, db
from app.models import User, Membro, PapelMembro, Celula, Ide
from werkzeug.security import generate_password_hash
import random

app = create_app()

def create_user_with_role(username, email, role_name, nome, ide=None):
    # Check if user exists
    existing_user = User.query.filter_by(username=username).first()
    if existing_user:
        print(f"User {username} already exists. Skipping.")
        return existing_user.membro

    # Create Member
    membro = Membro(
        nome=nome,
        email=email,
        ide_id=ide.id if ide else None
    )
    db.session.add(membro)
    db.session.commit() # Commit to get ID

    # Assign Role
    papel = PapelMembro(membro_id=membro.id, papel=role_name)
    db.session.add(papel)

    # Create User Login
    user = User(
        username=username,
        email=email,
        membro_id=membro.id
    )
    user.set_password('123456') # Default password
    db.session.add(user)
    db.session.commit()
    
    print(f"Created {role_name}: {nome} ({username})")
    return membro

with app.app_context():
    print("Seeding Hierarchy Users and Data...")

    # 1. Pastor Geral (Admin-like visibility)
    pastor_geral = create_user_with_role('pastor_geral', 'pastor@teste.com', 'pastor', 'Pastor Geraldo')

    # 2. Rede A & Rede B (IDEs)
    rede_a = Ide.query.filter_by(nome="Rede A").first()
    if not rede_a:
        rede_a = Ide(nome="Rede A")
        db.session.add(rede_a)
    
    rede_b = Ide.query.filter_by(nome="Rede B").first()
    if not rede_b:
        rede_b = Ide(nome="Rede B")
        db.session.add(rede_b)
    
    db.session.commit()

    # 3. Pastores de Rede
    pastor_rede_a = create_user_with_role('pastor_rede_a', 'pastor_a@teste.com', 'pastor_de_rede', 'Pastor Area A', ide=rede_a)
    pastor_rede_b = create_user_with_role('pastor_rede_b', 'pastor_b@teste.com', 'pastor_de_rede', 'Pastor Area B', ide=rede_b)

    # Assign pastores to IDEs
    rede_a.pastor_id = pastor_rede_a.id
    rede_b.pastor_id = pastor_rede_b.id
    db.session.commit()

    # 4. Supervisors (2 per Rede)
    sup_a1 = create_user_with_role('sup_a1', 'sup_a1@teste.com', 'supervisor', 'Supervisor A1', ide=rede_a)
    sup_a2 = create_user_with_role('sup_a2', 'sup_a2@teste.com', 'supervisor', 'Supervisor A2', ide=rede_a)
    
    sup_b1 = create_user_with_role('sup_b1', 'sup_b1@teste.com', 'supervisor', 'Supervisor B1', ide=rede_b)

    # 5. Leaders (2 per Supervisor) and Cells
    def create_leader_and_cell(leader_username, leader_name, supervisor, ide, cell_name):
        lider = create_user_with_role(leader_username, f'{leader_username}@teste.com', 'lider_de_celula', leader_name, ide=ide)
        
        # Link leader to supervisor
        lider.lider_id = supervisor.id
        db.session.add(lider)

        # Create Cell
        celula = Celula.query.filter_by(nome=cell_name).first()
        if not celula:
            celula = Celula(
                nome=cell_name,
                ide_id=ide.id,
                supervisor_id=supervisor.id,
                lider_id=lider.id,
                dia_reuniao='segunda',
                horario_reuniao='20:00'
            )
            db.session.add(celula)
            print(f"  Created Cell: {cell_name} (Lider: {leader_name}, Sup: {supervisor.nome}, Rede: {ide.nome})")
        else:
            # Update links just in case
            celula.ide_id = ide.id
            celula.supervisor_id = supervisor.id
            celula.lider_id = lider.id
            db.session.add(celula)
        
        db.session.commit()

    create_leader_and_cell('lider_a1_1', 'Lider A1-1', sup_a1, rede_a, 'Celula A1-Alpha')
    create_leader_and_cell('lider_a1_2', 'Lider A1-2', sup_a1, rede_a, 'Celula A1-Beta')
    
    create_leader_and_cell('lider_a2_1', 'Lider A2-1', sup_a2, rede_a, 'Celula A2-Gama')
    
    create_leader_and_cell('lider_b1_1', 'Lider B1-1', sup_b1, rede_b, 'Celula B1-Delta')

    print("Seeding Complete!")
