
from app import db
from app.models import Membro, Endereco, PapelMembro, Ide
import datetime

def test_create_membro(client, app):
    with app.app_context():
        membro = Membro(nome="Teste Membro", email="teste@example.com", cpf="12345678901")
        db.session.add(membro)
        db.session.commit()
        
        saved_membro = db.session.get(Membro, membro.id)
        assert saved_membro is not None
        assert saved_membro.nome == "Teste Membro"
        assert saved_membro.ativo is True

def test_membro_relationships(client, app):
    with app.app_context():
        # Ide
        ide = Ide(nome="IDE Teste")
        db.session.add(ide)
        db.session.commit()

        # Membro
        membro = Membro(nome="Membro Relacionado", ide_id=ide.id)
        db.session.add(membro)
        db.session.commit()

        # Endereco
        endereco = Endereco(membro_id=membro.id, logradouro="Rua Teste", cidade="Cidade Teste")
        db.session.add(endereco)
        
        # Papel
        papel = PapelMembro(membro_id=membro.id, papel="membro")
        db.session.add(papel)
        db.session.commit()

        # Check relationships
        saved_membro = db.session.get(Membro, membro.id)
        assert saved_membro.ide.nome == "IDE Teste"
        assert saved_membro.enderecos[0].logradouro == "Rua Teste"
        assert saved_membro.papeis[0].papel == "membro"

def test_membro_to_dict(client, app):
    with app.app_context():
        membro = Membro(nome="Dict Membro", data_nascimento=datetime.date(1990, 1, 1))
        db.session.add(membro)
        db.session.commit()
        
        data = membro.to_dict()
        assert data['nome'] == "Dict Membro"
        assert data['data_nascimento'] == "1990-01-01"
