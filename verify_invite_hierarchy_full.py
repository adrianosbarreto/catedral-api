# Configuração de ambiente para testes ANTES do import do app se possível
import os
import unittest
import json
from datetime import datetime, timedelta
os.environ['SSH_TUNNEL_ENABLED'] = 'false'
os.environ['APPLICATION_SUBPATH'] = '/catedral' # Mantém subpath para ser idêntico à produção

import config
# Patching the config BEFORE create_app is called to avoid engine initialization errors
config.TestingConfig.SQLALCHEMY_ENGINE_OPTIONS = {}

from app import create_app, db
from app.models import User, Membro, Ide, Convite, Role, PapelMembro, Celula
from flask_jwt_extended import create_access_token

class TestHierarchyLogic(unittest.TestCase):
    def setUp(self):
        # Usar um arquivo local para o banco de teste (isolado)
        self.test_db_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'test_hierarchy.db')
        
        # Forçar configuração de teste
        self.app = create_app('testing')
        self.app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{self.test_db_path}'
        self.app.config['JWT_SECRET_KEY'] = 'test-secret'
        self.app.config['TESTING'] = True
        self.app.config['PROPAGATE_EXCEPTIONS'] = True
        
        self.app_context = self.app.app_context()
        self.app_context.push()
        
        # Garantir que o db use a nova config (o init_app do create_app já rodou, 
        # mas o motor é criado preguiçosamente. Se der erro, precisamos recriar o engine)
        from sqlalchemy import create_engine
        db.engine.dispose() # Descarta o anterior
        
        self.client = self.app.test_client()
        
        db.create_all()
        self.setup_seeds()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()
        if os.path.exists(self.test_db_path):
            try:
                os.remove(self.test_db_path)
            except:
                pass

    def setup_seeds(self):
        # 1. Criar Roles padrão
        roles = ['admin', 'pastor', 'pastor_de_rede', 'supervisor', 'lider_de_celula', 'vice_lider_de_celula', 'membro']
        self.role_objs = {}
        for r in roles:
            obj = Role(name=r)
            db.session.add(obj)
            self.role_objs[r] = obj
        
        # 2. Criar IDE
        self.ide = Ide(nome="IDE Teste")
        db.session.add(self.ide)
        db.session.flush()

        # 3. Criar Usuários para teste
        
        # Admin
        self.user_admin = User(username='admin', email='admin@test.com')
        self.user_admin.set_password('test')
        db.session.add(self.user_admin)
        
        # Pastor de Rede
        self.pastor_membro = Membro(nome="Pastor de Rede", ide_id=self.ide.id, ativo=True)
        db.session.add(self.pastor_membro)
        db.session.flush()
        self.ide.pastor_id = self.pastor_membro.id # Pastor da IDE
        
        self.user_pastor = User(username='pastor_test', email='pastor@test.com', membro_id=self.pastor_membro.id)
        self.user_pastor.set_password('test')
        db.session.add(self.user_pastor)
        db.session.add(PapelMembro(membro_id=self.pastor_membro.id, role_id=self.role_objs['pastor_de_rede'].id))
        
        # Supervisor (vinculado ao Pastor de Rede)
        self.supervisor_membro = Membro(nome="Supervisor Teste", ide_id=self.ide.id, pastor_id=self.pastor_membro.id, ativo=True)
        db.session.add(self.supervisor_membro)
        db.session.flush()
        self.user_supervisor = User(username='supervisor_test', email='sup@test.com', membro_id=self.supervisor_membro.id)
        self.user_supervisor.set_password('test')
        db.session.add(self.user_supervisor)
        db.session.add(PapelMembro(membro_id=self.supervisor_membro.id, role_id=self.role_objs['supervisor'].id))

        # Líder (vinculado ao Supervisor)
        self.lider_membro = Membro(nome="Líder Teste", ide_id=self.ide.id, pastor_id=self.pastor_membro.id, supervisor_id=self.supervisor_membro.id, ativo=True)
        db.session.add(self.lider_membro)
        db.session.flush()
        self.user_lider = User(username='lider_test', email='lider@test.com', membro_id=self.lider_membro.id)
        self.user_lider.set_password('test')
        db.session.add(self.user_lider)
        db.session.add(PapelMembro(membro_id=self.lider_membro.id, role_id=self.role_objs['lider_de_celula'].id))
        
        db.session.commit()
        
        # VERIFICAÇÃO DE ROLES PARA DEBUG SE FALHAR
        # print(f"DEBUG: Admin role: {self.user_admin.role}")
        # print(f"DEBUG: Pastor role: {self.user_pastor.role}")
        # print(f"DEBUG: Lider role: {self.user_lider.role}")
        
        # 4. Criar Célula
        self.celula = Celula(nome="Célula Alpha", ide_id=self.ide.id, supervisor_id=self.supervisor_membro.id, lider_id=self.lider_membro.id)
        db.session.add(self.celula)
        
        db.session.commit()

    def get_token(self, user):
        with self.app.test_request_context():
            return create_access_token(identity=str(user.id))

    def generate_invite(self, user, payload):
        token = self.get_token(user)
        headers = {'Authorization': f'Bearer {token}'}
        res = self.client.post('/catedral/auth/invite', json=payload, headers=headers)
        if res.status_code not in [200, 201]:
            print(f"DEBUG: generate_invite failed with {res.status_code}: {res.get_data(as_text=True)}")
        else:
            # Check if saved in DB
            token_str = res.get_json()['invite_url'].split('=')[-1]
            invite = Convite.query.filter_by(token=token_str).first()
            if not invite:
                print(f"DEBUG: Invite {token_str} NOT found in DB after generation!")
        return res

    def register_user(self, invite_token, email, nome="Novo", papel="membro"):
        import random
        # Gerar um CPF fake simples para teste
        cpf = f"{random.randint(100,999)}.{random.randint(100,999)}.{random.randint(100,999)}-{random.randint(10,99)}"
        
        payload = {
            'nome': nome,
            'email': email,
            'password': 'password123',
            'invite_token': invite_token,
            'papel': papel,
            'cpf': cpf,
            'sexo': 'Masculino',
            'estado_civil': 'Solteiro',
            'data_nascimento': '1990-01-01'
        }
        res = self.client.post('/catedral/auth/register', json=payload)
        if res.status_code != 201:
            print(f"DEBUG: register_user failed with {res.status_code}: {res.get_data(as_text=True)}")
        return res

    # --- TEST CASES ---

    def test_pastor_invites_supervisor_inheritance(self):
        """Teste: Pastor de Rede convida um Supervisor. Deve herdar o pastor_id do criador."""
        res = self.generate_invite(self.user_pastor, {
            'ide_id': self.ide.id,
            'papel_destino': 'supervisor'
        })
        self.assertIn(res.status_code, [200, 201])
        token = res.get_json()['invite_url'].split('=')[-1]
        
        reg_res = self.register_user(token, 'new_sup@test.com', papel='supervisor')
        self.assertEqual(reg_res.status_code, 201)
        
        membro = Membro.query.filter_by(email='new_sup@test.com').first()
        self.assertEqual(membro.pastor_id, self.pastor_membro.id)
        self.assertIsNone(membro.supervisor_id)

    def test_supervisor_invites_lider_inheritance(self):
        """Teste: Supervisor convida um Líder. Deve herdar Pastor do supervisor e colocar supervisor_id = criador."""
        res = self.generate_invite(self.user_supervisor, {
            'ide_id': self.ide.id,
            'papel_destino': 'lider_de_celula'
        })
        token = res.get_json()['invite_url'].split('=')[-1]
        
        self.register_user(token, 'new_lider@test.com', papel='lider_de_celula')
        
        membro = Membro.query.filter_by(email='new_lider@test.com').first()
        self.assertEqual(membro.supervisor_id, self.supervisor_membro.id)
        self.assertEqual(membro.pastor_id, self.pastor_membro.id)

    def test_admin_invites_membro_with_cell(self):
        """Teste: Admin convida Membro para uma Célula específica. Deve herdar TUDO da célula."""
        res = self.generate_invite(self.user_admin, {
            'ide_id': self.ide.id,
            'papel_destino': 'membro',
            'celula_id': self.celula.id
        })
        token = res.get_json()['invite_url'].split('=')[-1]
        
        self.register_user(token, 'cel_membro@test.com', papel='membro')
        
        membro = Membro.query.filter_by(email='cel_membro@test.com').first()
        self.assertEqual(membro.lider_id, self.lider_membro.id)
        self.assertEqual(membro.supervisor_id, self.supervisor_membro.id)
        self.assertEqual(membro.pastor_id, self.pastor_membro.id)

    def test_explicit_override_by_admin(self):
        """Teste: Admin cria Líder mas define manualmente um Supervisor diferente do dele."""
        # Criar outro supervisor
        sup_b = Membro(nome="Supervisor B", ide_id=self.ide.id, pastor_id=self.pastor_membro.id, ativo=True)
        db.session.add(sup_b)
        db.session.commit()
        
        res = self.generate_invite(self.user_admin, {
            'ide_id': self.ide.id,
            'papel_destino': 'lider_de_celula',
            'pastor_id': self.pastor_membro.id,
            'supervisor_id': sup_b.id
        })
        token = res.get_json()['invite_url'].split('=')[-1]
        
        self.register_user(token, 'explicit_lider@test.com', papel='lider_de_celula')
        
        membro = Membro.query.filter_by(email='explicit_lider@test.com').first()
        self.assertEqual(membro.supervisor_id, sup_b.id)
        # Agora deve herdar do Pastor da IDE como fallback final (antes era None)
        self.assertEqual(membro.pastor_id, self.pastor_membro.id)

    def test_unauthorized_invite_role(self):
        """Teste: Líder tentando convidar um Pastor (Não permitido)."""
        res = self.generate_invite(self.user_lider, {
            'ide_id': self.ide.id,
            'papel_destino': 'pastor_de_rede'
        })
        self.assertEqual(res.status_code, 403)
        self.assertIn('não tem permissão', res.get_json()['error'])

    def test_hierarchy_levels_preservation(self):
        """Teste: Garantir que não existem fallbacks perigosos (ex: pastor_id virar lider_id)."""
        # Se um Líder convida um Membro sem passar célula
        res = self.generate_invite(self.user_lider, {
            'ide_id': self.ide.id,
            'papel_destino': 'membro'
        })
        token = res.get_json()['invite_url'].split('=')[-1]
        self.register_user(token, 'membro_lider@test.com', papel='membro')
        
        membro = Membro.query.filter_by(email='membro_lider@test.com').first()
        # Deve herdar a hierarquia completa do líder
        self.assertEqual(membro.lider_id, self.lider_membro.id)
        self.assertEqual(membro.supervisor_id, self.supervisor_membro.id)
        self.assertEqual(membro.pastor_id, self.pastor_membro.id)

    # --- NOVOS TESTES DE VALIDAÇÃO RIGOROSA NO ENDPOINT /INVITE ---

    def test_admin_invite_supervisor_missing_pastor(self):
        """Erro: Admin tentando convidar Supervisor sem informar pastor_id."""
        res = self.generate_invite(self.user_admin, {
            'ide_id': self.ide.id,
            'papel_destino': 'supervisor'
            # Faltando pastor_id
        })
        self.assertEqual(res.status_code, 400)
        self.assertIn('Pastor de Rede é obrigatória', res.get_json()['error'])

    def test_admin_invite_lider_missing_hierarchy(self):
        """Erro: Admin tentando convidar Líder sem informar toda a hierarquia intermediária."""
        # Tenta com pastor mas sem supervisor
        res = self.generate_invite(self.user_admin, {
            'ide_id': self.ide.id,
            'papel_destino': 'lider_de_celula',
            'pastor_id': self.pastor_membro.id
            # Faltando supervisor_id
        })
        self.assertEqual(res.status_code, 400)
        self.assertIn('Supervisor é obrigatória', res.get_json()['error'])

    def test_pastor_rede_invite_membro_missing_lider(self):
        """Erro: Pastor de Rede tentando convidar Membro sem informar Líder."""
        res = self.generate_invite(self.user_pastor, {
            'ide_id': self.ide.id,
            'papel_destino': 'membro',
            'supervisor_id': self.supervisor_membro.id
            # Faltando lider_id
        })
        self.assertEqual(res.status_code, 400)
        self.assertIn('você precisa definir o Líder', res.get_json()['error'])

    def test_supervisor_invite_membro_missing_lider(self):
        """Erro: Supervisor tentando convidar Membro sem informar Líder."""
        res = self.generate_invite(self.user_supervisor, {
            'ide_id': self.ide.id,
            'papel_destino': 'membro'
            # Faltando lider_id
        })
        self.assertEqual(res.status_code, 400)
        self.assertIn('você precisa definir o Líder', res.get_json()['error'])

    def test_admin_invite_membro_success_with_full_hierarchy(self):
        """Sucesso: Admin fornece toda a hierarquia manualmente para um Membro."""
        res = self.generate_invite(self.user_admin, {
            'ide_id': self.ide.id,
            'papel_destino': 'membro',
            'pastor_id': self.pastor_membro.id,
            'supervisor_id': self.supervisor_membro.id,
            'lider_id': self.lider_membro.id
        })
        self.assertEqual(res.status_code, 201)
        token = res.get_json()['invite_url'].split('=')[-1]
        
        # Registrar e validar se gravou certo
        self.register_user(token, 'full_h_admin@test.com', papel='membro')
        membro = Membro.query.filter_by(email='full_h_admin@test.com').first()
        self.assertEqual(membro.pastor_id, self.pastor_membro.id)
        self.assertEqual(membro.supervisor_id, self.supervisor_membro.id)
        self.assertEqual(membro.lider_id, self.lider_membro.id)

    def test_invite_with_cell_bypass_validation(self):
        """Sucesso: Quando célula é fornecida, o backend não exige os IDs intermediários."""
        res = self.generate_invite(self.user_admin, {
            'ide_id': self.ide.id,
            'papel_destino': 'membro',
            'celula_id': self.celula.id
            # pastor_id, supervisor_id e lider_id omitidos mas deve passar por causa da celula
        })
        self.assertEqual(res.status_code, 201)

if __name__ == '__main__':
    unittest.main()
