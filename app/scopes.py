from app.models import Role

class CellScope:
    @staticmethod
    def apply(query, user):
        """
        Applies hierarchical filtering to the Cell query based on user role.
        """
        if not user:
            return query.filter_by(id=-1)

        role_name = user.role
        if role_name in ['admin', 'pastor']:
            return query

        if not user.membro:
            return query.filter_by(id=-1)

        membro_id = user.membro.id

        # 2. Pastor de Rede: View cells in their IDEs (Network)
        if role_name == 'pastor_de_rede':
            # Get IDs of IDEs led by this pastor
            my_ide_ids = [ide.id for ide in user.membro.ides_lideradas.all()]
            if not my_ide_ids:
                 # Fallback to own IDE if they lead no IDE
                 if user.membro.ide_id:
                     return query.filter_by(ide_id=user.membro.ide_id)
                 return query.filter_by(id=-1)
            
            from app.models import Celula
            return query.filter(Celula.ide_id.in_(my_ide_ids))

        # 3. Supervisor: View cells where they are supervisor
        if role_name == 'supervisor':
            from app.models import Celula
            return query.filter(Celula.supervisor_id == membro_id)

        # 4. Lider: View own cell (lider or vice-lider)
        if role_name == 'lider_de_celula' or role_name == 'vice_lider_de_celula':
            from app.models import Celula
            return query.filter((Celula.lider_id == membro_id) | (Celula.vice_lider_id == membro_id))
        
        # Default: No access
        return query.filter_by(id=-1)

class MembroScope:
    @staticmethod
    def apply(query, user):
        """
        Applies hierarchical filtering to the Membro query based on user role.
        """
        from app.models import Membro
        from app import db
        
        if not user:
            return query.filter_by(id=-1)

        role_name = user.role
        if role_name in ['admin', 'pastor']:
            return query

        if not user.membro:
            return query.filter_by(id=-1)

        membro_id = user.membro.id

        # 2. Pastor de Rede: View members in their IDEs (Network)
        if role_name == 'pastor_de_rede':
            my_ide_ids = [ide.id for ide in user.membro.ides_lideradas.all()]
            if not my_ide_ids:
                 if user.membro.ide_id:
                     return query.filter((Membro.ide_id == user.membro.ide_id) | (Membro.pastor_id == membro_id))
                 return query.filter(Membro.pastor_id == membro_id)
            
            # Include members linked to cells in the network
            from app.models import MembroNucleo, Nucleo, Celula
            celula_subquery = db.session.query(MembroNucleo.membro_id).join(Nucleo).join(Celula).filter(Celula.ide_id.in_(my_ide_ids))
            
            return query.filter((Membro.ide_id.in_(my_ide_ids)) | (Membro.pastor_id == membro_id) | (Membro.id.in_(celula_subquery)))

        # 3. Supervisor: View members directly under their supervision + themselves
        if role_name == 'supervisor':
            # Include members directly supervised or linked to supervised cells
            from app.models import MembroNucleo, Nucleo, Celula
            celula_subquery = db.session.query(MembroNucleo.membro_id).join(Nucleo).join(Celula).filter(Celula.supervisor_id == membro_id)
            
            return query.filter((Membro.supervisor_id == membro_id) | (Membro.id == membro_id) | (Membro.id.in_(celula_subquery)))

            
        # 4. Lider: View own cell members (those who report to them)
        if role_name in ['lider_de_celula', 'vice_lider_de_celula']:
            return query.filter((Membro.lider_id == membro_id) | (Membro.id == membro_id))
        
        # Default: only see self
        return query.filter(Membro.id == membro_id)
