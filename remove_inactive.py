from app import create_app, db
from app.models import User, Membro, Celula, Convite, SolicitacaoTransferencia

def cleanup_inactive():
    app = create_app()
    with app.app_context():
        print("--- DATABASE CLEANUP - INACTIVE RECORDS (AUTO-COMMIT) ---")
        
        # 1. Inactive Cells
        inactive_cells = Celula.query.filter_by(ativo=False).all()
        print(f"Deleting {len(inactive_cells)} inactive cells...")
        for c in inactive_cells:
            db.session.delete(c)
            
        # 2. Identify Users to delete (Linked to inactive members or orphans)
        users_to_purge = []
        
        # Inactive Members
        inactive_members = Membro.query.filter_by(ativo=False).all()
        for m in inactive_members:
            user = User.query.filter_by(membro_id=m.id).first()
            if user and user not in users_to_purge:
                users_to_purge.append(user)
        
        # Orphan Users (non-admin)
        orphan_users = User.query.filter(User.username != 'admin', (~User.membro.has())).all()
        for u in orphan_users:
            if u not in users_to_purge:
                users_to_purge.append(u)

        print(f"Identified {len(users_to_purge)} users to purge.")

        # 3. Handle Dependencies for these Users
        for user in users_to_purge:
            print(f"  - Cleaning up dependencies for user: {user.username}")
            
            # Convites created by this user
            convites = Convite.query.filter_by(criado_por_id=user.id).all()
            for con in convites:
                db.session.delete(con)
            
            # Solicitacoes created by this user
            solicitacoes = SolicitacaoTransferencia.query.filter_by(solicitante_id=user.id).all()
            for sol in solicitacoes:
                db.session.delete(sol)
            
            # Finally delete the user
            db.session.delete(user)

        # 4. Finally delete the Inactive Members
        print(f"Deleting {len(inactive_members)} inactive members...")
        for m in inactive_members:
            db.session.delete(m)

        try:
            db.session.commit()
            print("\nCleanup completed successfully.")
        except Exception as e:
            db.session.rollback()
            print(f"\nCRITICAL ERROR during commit: {e}")

if __name__ == '__main__':
    cleanup_inactive()
