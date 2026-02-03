from app import create_app, db
from app.models import User, Membro, Ide, Celula, PapelMembro

def seed():
    app = create_app()
    with app.app_context():
        # User
        admin = User(username='admin', email='contato@adriano.pro.br')
        admin.set_password('admin123')
        db.session.add(admin)
        
        # IDE
        pastor = Membro(nome='Pastor Geral', email='pastor@test.com', ativo=True)
        db.session.add(pastor)
        db.session.flush()
        db.session.add(PapelMembro(membro_id=pastor.id, papel='pastor'))
        
        ide = Ide(nome='IDE Sede', pastor_id=pastor.id)
        db.session.add(ide)
        db.session.flush()
        pastor.ide_id = ide.id
        
        # Leaders
        sup = Membro(nome='Supervisor Teste', ide_id=ide.id, ativo=True)
        lider = Membro(nome='Lider Teste', ide_id=ide.id, ativo=True)
        db.session.add(sup)
        db.session.add(lider)
        db.session.flush()
        db.session.add(PapelMembro(membro_id=sup.id, papel='supervisor'))
        db.session.add(PapelMembro(membro_id=lider.id, papel='lider_de_celula'))
        
        # Cell
        celula = Celula(
            nome='Célula Alpha',
            ide_id=ide.id,
            supervisor_id=sup.id,
            lider_id=lider.id,
            dia_reuniao='quarta',
            horario_reuniao='20:00',
            logradouro='Rua Principal',
            numero='123',
            bairro='Centro',
            cidade='Exemplo',
            estado='SP',
            cep='12345-678'
        )
        db.session.add(celula)
        
        db.session.commit()
        print("Minimal seed successful!")

if __name__ == '__main__':
    seed()
