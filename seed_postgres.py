"""
Seed otimizado para PostgreSQL
Respeita ordem de foreign keys e constraints
"""
from app import create_app, db
from app.models import User, Membro, Ide, Celula, Evento, Endereco, PapelMembro, Role
from faker import Faker
import random
from datetime import datetime, timedelta

fake = Faker('pt_BR')

def seed_postgres():
    app = create_app()
    with app.app_context():
        print("🗑️  Limpando banco de dados...")
        
        # Ordem de deleção (reversa das foreign keys)
        db.session.query(Endereco).delete()
        db.session.query(PapelMembro).delete()
        db.session.query(Celula).delete()
        db.session.query(Membro).delete()
        db.session.query(Ide).delete()
        db.session.query(Evento).delete()
        db.session.query(User).delete()
        db.session.commit()
        print("✅ Banco limpo!")

        # ============================================================
        # 1. CRIAR IDEs PRIMEIRO (sem pastor ainda)
        # ============================================================
        print("\n📍 Criando IDEs...")
        ides_data = ['IDE Sede', 'IDE Norte', 'IDE Sul', 'IDE Leste', 'IDE Oeste']
        ides = []
        
        for nome_ide in ides_data:
            ide = Ide(nome=nome_ide, pastor_id=None)  # Sem pastor ainda
            db.session.add(ide)
            ides.append(ide)
        
        db.session.commit()
        print(f"✅ {len(ides)} IDEs criadas")

        # ============================================================
        # 2. CRIAR MEMBROS (agora que IDEs existem)
        # ============================================================
        print("\n👥 Criando membros...")
        membros = []
        
        # Criar pastores para IDEs
        for ide in ides:
            pastor = Membro(
                nome=f"Pastor {ide.nome}",
                email=fake.email(),
                telefone=fake.phone_number(),
                cpf=fake.cpf(),
                estado_civil='Casado(a)',
                sexo='Masculino',
                data_nascimento=fake.date_of_birth(minimum_age=30, maximum_age=60),
                data_batismo=fake.date_between(start_date='-20y', end_date='-5y'),
                ativo=True,
                ide_id=ide.id,
                lider_id=None  # Sem líder (é pastor)
            )
            db.session.add(pastor)
            db.session.flush()  # Obter ID
            
            # Atualizar IDE com pastor
            ide.pastor_id = pastor.id
            membros.append(pastor)
        
        # Criar membros regulares (sem lider_id por enquanto)
        for i in range(40):
            membro = Membro(
                nome=fake.name(),
                email=fake.email(),
                telefone=fake.phone_number(),
                cpf=fake.cpf(),
                estado_civil=random.choice(['Solteiro(a)', 'Casado(a)', 'Divorciado(a)', 'Viúvo(a)']),
                sexo=random.choice(['Masculino', 'Feminino']),
                data_nascimento=fake.date_of_birth(minimum_age=18, maximum_age=80),
                data_batismo=fake.date_between(start_date='-10y', end_date='today') if random.random() > 0.3 else None,
                ativo=True,
                ide_id=random.choice(ides).id,
                lider_id=None  # Definir depois
            )
            db.session.add(membro)
            membros.append(membro)
        
        db.session.commit()
        
        # Atribuir alguns líderes aos membros
        lideres = membros[len(ides):len(ides) + 10]  # Índices 5-15 serão líderes
        membros_sem_lider = membros[len(ides) + 10:]  # Resto
        
        for membro in membros_sem_lider:
            if random.random() > 0.3:  # 70% terão líder
                membro.lider_id = random.choice(lideres).id
        
        db.session.commit()
        print(f"✅ {len(membros)} membros criados")

        # ============================================================
        # 3. CRIAR ENDEREÇOS (agora que membros existem)
        # ============================================================
        print("\n🏠 Criando endereços...")
        enderecos_count = 0
        for membro in membros[:25]:  # Apenas alguns têm endereço
            endereco = Endereco(
                membro_id=membro.id,
                logradouro=fake.street_name(),
                numero=fake.building_number(),
                bairro=fake.bairro(),
                cidade=fake.city(),
                estado=fake.state_abbr(),
                cep=fake.postcode()
            )
            db.session.add(endereco)
            enderecos_count += 1
        
        db.session.commit()
        print(f"✅ {enderecos_count} endereços criados")

        # ============================================================
        # 4. CRIAR PAPÉIS (agora que membros existem e roles foram criadas)
        # ============================================================
        print("\n🎭 Atribuindo papéis...")
        papeis_count = 0
        
        # Obter roles do seed_rbac
        role_admin = Role.query.filter_by(name='admin').first()
        role_pastor = Role.query.filter_by(name='pastor').first()
        role_lider = Role.query.filter_by(name='lider').first()
        role_membro = Role.query.filter_by(name='membro').first()
        
        # Pastores
        for i in range(len(ides)):
            pastor = membros[i]
            papel = PapelMembro(
                membro_id=pastor.id,
                role_id=role_pastor.id if role_pastor else None,
                papel='Pastor'
            )
            db.session.add(papel)
            papeis_count += 1
        
        # Líderes
        for i in range(len(ides), len(ides) + 10):
            if i < len(membros):
                lider = membros[i]
                papel = PapelMembro(
                    membro_id=lider.id,
                    role_id=role_lider.id if role_lider else None,
                    papel='Líder'
                )
                db.session.add(papel)
                papeis_count += 1
        
        db.session.commit()
        print(f"✅ {papeis_count} papéis atribuídos")

        # ============================================================
        # 5. CRIAR CÉLULAS (agora que membros e IDEs existem)
        # ============================================================
        print("\n🔵 Criando células...")
        celulas = []
        lideres_disponiveis = membros[len(ides):len(ides) + 10]  # Usar membros que são líderes
        
        for i in range(8):
            if i < len(lideres_disponiveis) and i < len(ides):
                lider = lideres_disponiveis[i]
                ide = ides[i % len(ides)]
                
                celula = Celula(
                    nome=f'Célula {fake.first_name()}',
                    ide_id=ide.id,
                    lider_id=lider.id,
                    supervisor_id=ide.pastor_id,  # Pastor é supervisor
                    dia_reuniao=random.choice(['Segunda', 'Terça', 'Quarta', 'Quinta', 'Sexta', 'Sábado']),
                    horario_reuniao=f"{random.randint(18, 20)}:00",
                    logradouro=fake.street_name(),
                    numero=fake.building_number(),
                    bairro=fake.bairro(),
                    cidade=fake.city(),
                    estado=fake.state_abbr(),
                    cep=fake.postcode()
                )
                db.session.add(celula)
                celulas.append(celula)
        
        db.session.commit()
        print(f"✅ {len(celulas)} células criadas")

        # ============================================================
        # 6. CRIAR EVENTOS
        # ============================================================
        print("\n📅 Criando eventos...")
        tipos_evento = ['Culto', 'Reunião', 'Conferência', 'Workshop', 'Retiro']
        eventos = []
        
        for _ in range(8):
            start_date = fake.future_datetime(end_date='+60d')
            end_date = start_date + timedelta(hours=random.randint(2, 8))
            
            evento = Evento(
                titulo=fake.catch_phrase(),
                descricao=fake.text(max_nb_chars=200),
                data_inicio=start_date,
                data_fim=end_date,
                local=random.choice(['Sede Principal', 'IDE Norte', 'IDE Sul', 'Auditório Central']),
                tipo_evento=random.choice(tipos_evento),
                capacidade_maxima=random.randint(50, 500)
            )
            db.session.add(evento)
            eventos.append(evento)
        
        db.session.commit()
        print(f"✅ {len(eventos)} eventos criados")

        # ============================================================
        # 7. CRIAR USUÁRIOS (por último, com membro_id)
        # ============================================================
        print("\n👤 Criando usuários...")
        
        # Admin
        admin = User(
            username='admin',
            email='admin@example.com',
            membro_id=None  # Admin não precisa ser membro
        )
        admin.set_password('admin123')
        db.session.add(admin)
        
        # Usuários para pastores
        for i in range(min(3, len(ides))):
            pastor = membros[i]
            user = User(
                username=f'pastor{i+1}',
                email=pastor.email,
                membro_id=pastor.id
            )
            user.set_password('password123')
            db.session.add(user)
        
        # Usuários para alguns líderes
        for i in range(len(ides), min(len(ides) + 5, len(membros))):
            lider = membros[i]
            user = User(
                username=f'lider{i-len(ides)+1}',
                email=lider.email,
                membro_id=lider.id
            )
            user.set_password('password123')
            db.session.add(user)
        
        db.session.commit()
        print(f"✅ Usuários criados")

        # ============================================================
        # RESUMO
        # ============================================================
        print("\n" + "="*60)
        print("✅ SEED CONCLUÍDO COM SUCESSO!")
        print("="*60)
        print(f"📍 IDEs: {len(ides)}")
        print(f"👥 Membros: {len(membros)}")
        print(f"🏠 Endereços: {enderecos_count}")
        print(f"🎭 Papéis: {papeis_count}")
        print(f"🔵 Células: {len(celulas)}")
        print(f"📅 Eventos: {len(eventos)}")
        print(f"👤 Usuários: {4 + min(3, len(ides)) + min(5, len(membros) - len(ides))}")
        print("\n🔑 Credenciais:")
        print("   Admin: admin / admin123")
        print("   Pastores: pastor1, pastor2, pastor3 / password123")
        print("   Líderes: lider1, lider2, ... / password123")
        print("="*60)

if __name__ == '__main__':
    seed_postgres()
