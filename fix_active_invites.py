
import os
import sys
from datetime import datetime
from app import create_app, db
from app.models import Convite, Celula, Membro, User

def fix_invites():
    app = create_app()
    with app.app_context():
        now = datetime.utcnow()
        # Buscar convites ativos (não usados e não expirados)
        active_invites = Convite.query.filter(
            Convite.data_expiracao > now
        ).all()

        print(f"Encontrados {len(active_invites)} convites ativos para verificar.")
        updated_count = 0

        for invite in active_invites:
            changed = False
            
            # 1. Tentar preencher a partir da Célula
            if invite.celula_id:
                celula = db.session.get(Celula, invite.celula_id)
                if celula:
                    if not invite.lider_destino_id and celula.lider_id:
                        invite.lider_destino_id = celula.lider_id
                        changed = True
                    if not invite.supervisor_destino_id and celula.supervisor_id:
                        invite.supervisor_destino_id = celula.supervisor_id
                        changed = True
                    if not invite.pastor_destino_id and celula.ide and celula.ide.pastor_id:
                        invite.pastor_destino_id = celula.ide.pastor_id
                        changed = True

            # 2. Tentar preencher a partir do Criador
            if invite.criado_por_id:
                criador_user = db.session.get(User, invite.criado_por_id)
                if criador_user and criador_user.membro:
                    membro = criador_user.membro
                    role = criador_user.role
                    
                    if role == 'supervisor':
                        if not invite.supervisor_destino_id:
                            invite.supervisor_destino_id = membro.id
                            changed = True
                        if not invite.pastor_destino_id and membro.pastor_id:
                            invite.pastor_destino_id = membro.pastor_id
                            changed = True
                    
                    elif role == 'pastor_de_rede':
                        if not invite.pastor_destino_id:
                            invite.pastor_destino_id = membro.id
                            changed = True
                            
                    elif role == 'lider_de_celula':
                        if not invite.lider_destino_id:
                            invite.lider_destino_id = membro.id
                            changed = True
                        if not invite.supervisor_destino_id and membro.supervisor_id:
                            invite.supervisor_destino_id = membro.supervisor_id
                            changed = True
                        if not invite.pastor_destino_id and membro.pastor_id:
                            invite.pastor_destino_id = membro.pastor_id
                            changed = True

            if changed:
                print(f"Update no convite {invite.token[:8]}... para {invite.papel_destino}")
                updated_count += 1

        if updated_count > 0:
            try:
                db.session.commit()
                print(f"Sucesso: {updated_count} convites foram corrigidos.")
            except Exception as e:
                db.session.rollback()
                print(f"Erro ao salvar alterações: {e}")
        else:
            print("Nenhum convite precisou de correção.")

if __name__ == "__main__":
    fix_invites()
