import sys
import os
sys.path.append(os.getcwd())

from app import create_app, db
from app.models import User, Membro, FrequenciaAulaLideranca, AulaLideranca
from app.scopes import MembroScope

app = create_app()

def verify_hierarchy():
    with app.app_context():
        # Get our seeded supervisor user
        supervisor_user = User.query.filter_by(username='supervisor_test').first()
        
        if not supervisor_user:
             print("No supervisor_test user found.")
             return

        print(f"Testing for user: {supervisor_user.username} (Role: {supervisor_user.role})")
        
        # Get our seeded aula
        aula = AulaLideranca.query.filter_by(titulo="Aula Teste").first()
        if not aula:
            # Fallback to any aula if title changed
            aula = AulaLideranca.query.order_by(AulaLideranca.id.desc()).first()

        if not aula:
            print("No AulaLideranca found to test.")
            return

        print(f"Testing with Aula ID: {aula.id}")

        query = FrequenciaAulaLideranca.query.filter_by(aula_id=aula.id)
        
        # Total before filter (should join with Membro to count correctly if we want to be sure)
        total_before = query.count()
        print(f"Total attendance records for aula {aula.id}: {total_before}")
        
        # Apply scope (MembroScope requires a join with Membro or it will fail because it filters by Membro.xxx)
        query_with_join = query.join(Membro)
        filtered_query = MembroScope.apply(query_with_join, supervisor_user)
        
        results = filtered_query.all()
        total_after = len(results)
        print(f"Total attendance records after hierarchy filter: {total_after}")
        
        # In our seed, supervisor has 3 subordinates + themselves = 4
        # But wait, MembroScope for supervisor: (Membro.supervisor_id == membro_id) | (Membro.id == membro_id) | (Membro.id.in_(celula_subquery))
        # Total should be 4 if no cells are involved.
        
        print("\nMembers visible to supervisor:")
        for r in results:
            print(f"- {r.membro.nome}")

        if total_after < total_before:
            print("\nSUCCESS: Hierarchy filter applied correctly. Supervisor see less than total.")
        else:
            print("\nFAILURE: Supervisor still sees everything or filter not Working.")

        # Admin test
        admin_user = User.query.filter_by(username='admin').first()
        if admin_user:
            admin_query = FrequenciaAulaLideranca.query.filter_by(aula_id=aula.id).join(Membro)
            admin_filtered = MembroScope.apply(admin_query, admin_user)
            admin_count = admin_filtered.count()
            print(f"\nAdmin sees {admin_count} records.")
            if admin_count >= total_before:
                 print("SUCCESS: Admin still sees everything.")

if __name__ == "__main__":
    verify_hierarchy()
