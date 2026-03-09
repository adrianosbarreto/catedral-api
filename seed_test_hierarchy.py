import sys
import os
sys.path.append(os.getcwd())

from app import create_app, db
from app.models import User, Membro, AulaLideranca, FrequenciaAulaLideranca, Ide, PapelMembro, Role
from datetime import datetime, timedelta

app = create_app()

def seed_test_data():
    with app.app_context():
        # 1. Ensure IDE exists
        ide = Ide.query.first()
        if not ide:
            ide = Ide(nome="IDE Teste", cor="#ff0000")
            db.session.add(ide)
            db.session.flush()

        # 2. Ensure Roles exist
        roles = {r.name: r for r in Role.query.all()}
        for rname in ['admin', 'pastor', 'supervisor', 'lider_de_celula', 'membro']:
            if rname not in roles:
                roles[rname] = Role(name=rname, label=rname.capitalize())
                db.session.add(roles[rname])
        db.session.flush()

        # 3. Create Supervisor
        supervisor_membro = Membro.query.filter_by(nome="Supervisor Teste").first()
        if not supervisor_membro:
            supervisor_membro = Membro(nome="Supervisor Teste", ide_id=ide.id, ativo=True)
            db.session.add(supervisor_membro)
            db.session.flush()
        
        supervisor_user = User.query.filter_by(username="supervisor_test").first()
        if not supervisor_user:
            supervisor_user = User(username="supervisor_test", membro_id=supervisor_membro.id)
            supervisor_user.set_password("teste123")
            db.session.add(supervisor_user)
            db.session.flush()
            
            papel = PapelMembro(membro_id=supervisor_membro.id, role_id=roles['supervisor'].id)
            db.session.add(papel)

        # 4. Create Subordinate Members
        for i in range(3):
            nome = f"Subordinado {i}"
            m = Membro.query.filter_by(nome=nome).first()
            if not m:
                m = Membro(nome=nome, ide_id=ide.id, supervisor_id=supervisor_membro.id, ativo=True)
                db.session.add(m)
        
        # 5. Create Non-Subordinate Members
        for i in range(3):
            nome = f"Outro Membro {i}"
            m = Membro.query.filter_by(nome=nome).first()
            if not m:
                m = Membro(nome=nome, ide_id=ide.id, ativo=True)
                db.session.add(m)
        
        db.session.flush()

        # 6. Create Aula
        aula = AulaLideranca.query.filter_by(titulo="Aula Teste").first()
        if not aula:
            aula = AulaLideranca(titulo="Aula Teste", data_hora=datetime.utcnow() + timedelta(days=1), ativa=True)
            db.session.add(aula)
            db.session.flush()

        # 7. Create Frequencias for ALL members
        total_membros = Membro.query.filter_by(ativo=True).all()
        for m in total_membros:
            freq = FrequenciaAulaLideranca.query.filter_by(aula_id=aula.id, membro_id=m.id).first()
            if not freq:
                freq = FrequenciaAulaLideranca(aula_id=aula.id, membro_id=m.id, presente=False)
                db.session.add(freq)

        db.session.commit()
        print("Test data seeded successfully.")
        print(f"Total members: {len(total_membros)}")
        print(f"Supervisor: {supervisor_user.username}")
        print(f"Aula ID: {aula.id}")

if __name__ == "__main__":
    seed_test_data()
