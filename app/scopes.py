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
            # Assuming Pastor de Rede leads an IDE
            # Filter cells where cell.ide_id IN (ides where pastor_id == membro_id)
            # Or simplified: linked via proper relationship
            # Let's assume user.membro.ides_lideradas gives the IDEs
            
            # If `ides_lideradas` is a relationship on Membro model (we need to check models.py)
            # Yes: pastor = db.relationship('Membro', foreign_keys=[pastor_id], backref='ides_lideradas')
            
            # So we get IDs of IDEs led by this pastor
            my_ide_ids = [ide.id for ide in user.membro.ides_lideradas]
            if not my_ide_ids:
                 # Ensure they see NOTHING if they lead no IDE
                 # Or maybe they are just associated with an IDE?
                 # Fallback to own IDE?
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
            my_ide_ids = [ide.id for ide in user.membro.ides_lideradas]
            if not my_ide_ids:
                 if user.membro.ide_id:
                     return query.filter_by(ide_id=user.membro.ide_id)
                 return query.filter_by(id=-1)
            
            from app.models import Membro
            return query.filter(Membro.ide_id.in_(my_ide_ids))

        # 3. Supervisor: View members in the cells they supervise
        if role_name == 'supervisor':
            from app.models import Celula, Membro
            # Get cells supervised by this person
            supervised_cells = Celula.query.filter_by(supervisor_id=membro_id).all()
            lider_ids = []
            for c in supervised_cells:
                if c.lider_id: lider_ids.append(c.lider_id)
                if c.vice_lider_id: lider_ids.append(c.vice_lider_id)
            
            if not lider_ids:
                return query.filter(Membro.id == membro_id)
            
            return query.filter(Membro.lider_id.in_(lider_ids) | (Membro.id == membro_id))
            
        # 4. Lider: View own cell members (those who report to them)
        if role_name in ['lider_de_celula', 'vice_lider_de_celula']:
            from app.models import Membro
            return query.filter((Membro.lider_id == membro_id) | (Membro.id == membro_id))
        
        # Default: only see self
        from app.models import Membro
        return query.filter(Membro.id == membro_id)
