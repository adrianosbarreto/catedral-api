
import pytest
from app import db
from app.models import Membro, Ide, PapelMembro, Endereco
from datetime import date

def test_get_membros_empty(client, app):
    response = client.get('/api/membros')
    assert response.status_code == 200
    data = response.get_json()
    assert data['membros'] == []
    assert data['total'] == 0

def test_create_membro_api(client, app):
    membro_data = {
        'nome': 'Novo Membro API',
        'email': 'api@test.com',
        'telefone': '11999999999',
        'data_nascimento': '1995-05-15',
        'sexo': 'masculino',
        'endereco': {
            'logradouro': 'Rua API',
            'cidade': 'Cidade API',
            'estado': 'SP'
        },
        'papel': 'membro'
    }
    
    response = client.post('/api/membros', json=membro_data)
    assert response.status_code == 201
    data = response.get_json()
    assert data['nome'] == 'Novo Membro API'
    assert data['email'] == 'api@test.com'
    assert data['enderecos'][0]['logradouro'] == 'Rua API'
    assert data['papeis_membros'][0]['papel'] == 'membro'

def test_get_membro_detail(client, app):
    # Setup
    with app.app_context():
        membro = Membro(nome="Detalhe Membro")
        db.session.add(membro)
        db.session.commit()
        membro_id = membro.id

    response = client.get(f'/api/membros/{membro_id}')
    assert response.status_code == 200
    data = response.get_json()
    assert data['nome'] == "Detalhe Membro"

def test_update_membro_api(client, app):
    # Setup
    with app.app_context():
        membro = Membro(nome="Antigo Nome")
        db.session.add(membro)
        db.session.commit()
        
        # Add address
        endereco = Endereco(membro_id=membro.id, logradouro="Antiga Rua")
        db.session.add(endereco)
        db.session.commit()
        
        membro_id = membro.id

    update_data = {
        'nome': 'Novo Nome',
        'endereco': {
            'logradouro': 'Nova Rua'
        }
    }
    response = client.put(f'/api/membros/{membro_id}', json=update_data)
    assert response.status_code == 200
    data = response.get_json()
    assert data['nome'] == 'Novo Nome'
    assert data['enderecos'][0]['logradouro'] == 'Nova Rua'

def test_delete_membro_api(client, app):
    # Setup
    with app.app_context():
        membro = Membro(nome="Para Deletar")
        db.session.add(membro)
        db.session.commit()
        membro_id = membro.id

    response = client.delete(f'/api/membros/{membro_id}')
    assert response.status_code == 200
    
    # Verify deletion
    with app.app_context():
        deleted = db.session.get(Membro, membro_id)
        assert deleted is None

def test_get_ides(client, app):
    with app.app_context():
        ide = Ide(nome="IDE Teste API")
        db.session.add(ide)
        db.session.commit()
    
    response = client.get('/api/ides')
    assert response.status_code == 200
    data = response.get_json()
    assert len(data) >= 1
    assert any(i['nome'] == "IDE Teste API" for i in data)

def test_get_membros_filter_role(client, app):
    with app.app_context():
        # Create member with role
        m = Membro(nome="Pastor Teste")
        db.session.add(m)
        db.session.commit()
        
        pm = PapelMembro(membro_id=m.id, papel="pastor")
        db.session.add(pm)
        db.session.commit()
        
    response = client.get('/api/membros?role=pastor')
    assert response.status_code == 200
    data = response.get_json()
    assert any(m['nome'] == "Pastor Teste" for m in data['membros'])
    
    response = client.get('/api/membros?role=naoexiste')
    data = response.get_json()
    assert len(data['membros']) == 0
