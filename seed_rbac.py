from app import create_app, db
from app.models import Role, Permission, PapelMembro

app = create_app()

def seed_rbac():
    # 1. Define Permissions
    permissions_list = [
        # Celulas
        {'name': 'celulas.view_all', 'desc': 'Ver todas as células'},
        {'name': 'celulas.view_rede', 'desc': 'Ver células da rede'},
        {'name': 'celulas.view_supervisor', 'desc': 'Ver células supervisionadas'},
        {'name': 'celulas.view_own', 'desc': 'Ver própria célula (lider)'},
        {'name': 'celulas.create', 'desc': 'Criar nova célula'},
        {'name': 'celulas.edit', 'desc': 'Editar célula'},
        {'name': 'celulas.delete', 'desc': 'Deletar célula'},
        
        # Membros
        {'name': 'membros.view_all', 'desc': 'Ver todos membros'},
        {'name': 'membros.create', 'desc': 'Criar membro'},
        {'name': 'membros.edit', 'desc': 'Editar membro'},
    ]

    perms_db = {}
    for p in permissions_list:
        perm = Permission.query.filter_by(name=p['name']).first()
        if not perm:
            perm = Permission(name=p['name'], description=p['desc'])
            db.session.add(perm)
        perms_db[p['name']] = perm
    
    db.session.commit()
    print("Permissions seeded.")

    # 2. Define Roles and assign Permissions
    roles_config = {
        'admin': {
            'label': 'Administrador',
            'perms': ['celulas.view_all', 'celulas.create', 'celulas.edit', 'celulas.delete', 'membros.view_all', 'membros.create', 'membros.edit']
        },
        'pastor': { # Pastor Geral
            'label': 'Pastor Geral',
            'perms': ['celulas.view_all', 'celulas.create', 'celulas.edit', 'celulas.delete', 'membros.view_all', 'membros.create', 'membros.edit']
        },
        'pastor_de_rede': { # Pastor de Rede
            'label': 'Pastor de Rede',
            'perms': ['celulas.view_rede', 'celulas.create', 'celulas.edit', 'membros.view_all', 'membros.create']
        },
        'supervisor': {
            'label': 'Supervisor',
            'perms': ['celulas.view_supervisor', 'celulas.create', 'membros.create']
        },
        'lider_de_celula': {
            'label': 'Líder de Célula',
            'perms': ['celulas.view_own', 'membros.create'] # Can create members for their cell? Maybe.
        },
        'membro': {
            'label': 'Membro',
            'perms': []
        }
    }

    roles_db = {}
    for role_name, config in roles_config.items():
        role = Role.query.filter_by(name=role_name).first()
        if not role:
            role = Role(name=role_name, label=config['label'])
            db.session.add(role)
        
        # Update permissions
        role.permissions = [] # Reset to re-sync
        for perm_name in config['perms']:
            if perm_name in perms_db:
                role.permissions.append(perms_db[perm_name])
        
        roles_db[role_name] = role
    
    db.session.commit()
    print("Roles seeded.")

    # 3. Migrate Existing Users
    papeis = PapelMembro.query.filter(PapelMembro.role_id == None).all()
    count = 0
    for p in papeis:
        if p.papel in roles_db:
            p.role_rel = roles_db[p.papel]
            count += 1
        elif p.papel == 'admin': # Map 'admin' string to 'admin' role if not in dict key (it is)
             p.role_rel = roles_db['admin']
             count += 1
        else:
            print(f"Warning: Unknown role string '{p.papel}' for PapelMembro ID {p.id}")
            # Map default or ignore

    db.session.commit()
    print(f"Migrated {count} user roles.")

with app.app_context():
    # Ensure tables exist (since I added new models manually)
    db.create_all() 
    seed_rbac()
