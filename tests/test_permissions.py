import unittest
from app import create_app, db
from app.models import User, Role, Permission, PapelMembro, Membro, Celula, Ide
from app.scopes import CellScope

class TestPermissions(unittest.TestCase):
    def setUp(self):
        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        
        # Seed Permissions/Roles (Assuming seed_rbac logic, but simplified here)
        self.setup_rbac()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def setup_rbac(self):
        # Permissions
        p1 = Permission(name='celulas.view_all')
        p2 = Permission(name='celulas.view_own')
        p3 = Permission(name='celulas.create')
        db.session.add_all([p1, p2, p3])
        
        # Roles
        r_admin = Role(name='admin', label='Admin')
        r_admin.permissions.append(p1)
        r_admin.permissions.append(p3)
        
        r_lider = Role(name='lider_de_celula', label='Lider')
        r_lider.permissions.append(p2)
        
        db.session.add_all([r_admin, r_lider])
        db.session.commit()

    def test_user_has_permission(self):
        u = User(username='test_admin', email='a@a.com')
        m = Membro(nome='Admin')
        db.session.add(m)
        pm = PapelMembro(membro=m, role_rel=Role.query.filter_by(name='admin').first())
        db.session.add(pm)
        u.membro = m
        db.session.add(u)
        db.session.commit()
        
        self.assertTrue(u.has_permission('celulas.create'))
        self.assertFalse(u.has_permission('celulas.view_own')) # Admin doesn't have it explicitly in this setup
        # But Admin username bypass?
        # User.has_permission: "if self.username == 'admin': return True"
        
        u2 = User(username='regular_admin', email='b@b.com', membro=m)
        # Bypassing username check
        self.assertTrue(u2.has_permission('celulas.create'))

    def test_cell_scope_lider(self):
        # Create Lider
        r_lider = Role.query.filter_by(name='lider_de_celula').first()
        m = Membro(nome='Lader')
        db.session.add(m)
        db.session.flush() # Ensure ID is generated
        
        pm = PapelMembro(membro=m, role_rel=r_lider)
        db.session.add(pm)
        u = User(username='lider', email='l@l.com', membro=m)
        db.session.add(u)
        
        # Create Cells
        c1 = Celula(nome='Cell Own', lider_id=m.id)
        c2 = Celula(nome='Cell Other', lider_id=999)
        db.session.add_all([c1, c2])
        db.session.commit()
        
        # Apply Scope
        query = Celula.query
        query = CellScope.apply(query, u)
        results = query.all()
        
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].nome, 'Cell Own')

if __name__ == '__main__':
    unittest.main()
