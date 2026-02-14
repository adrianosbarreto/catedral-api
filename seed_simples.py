"""
Seed SIMPLIFICADO para PostgreSQL
Ordem estrita: IDEs → Membros → Resto
Sem referências circulares complexas
"""
from app import create_app, db
from app.models import User, Membro, Ide, Celula, Evento, Endereco, PapelMembro, Role
from faker import Faker
import random
from datetime import datetime, timedelta

fake = Faker('pt_BR')

def seed_simplificado():
    app = create_app()
    with app.app_context():
        print("🗑️  Limpando banco...")
        
        # Limpar na ordem reversa (aspas duplas em "user" pois é palavra reservada)
        db.session.execute(db.text('DELETE FROM enderecos'))
        db.session.execute(db.text('DELETE FROM papeis_membros'))
        db.session.execute(db.text('DELETE FROM celulas'))
        db.session.execute(db.text('DELETE FROM eventos'))
        db.session.execute(db.text('DELETE FROM membros'))
        db.session.execute(db.text('DELETE FROM ides'))
        db.session.execute(db.text('DELETE FROM "user"'))  # Aspas duplas - palavra reservada
        db.session.commit()
        print("✅ Limpo!")

        # 1. IDES (sem pastor)
        print("\n📍 Criando IDEs...")
        ides =[]
        for nome in ['IDE Sede', 'IDE Norte', 'IDE Sul']:
            ide = Ide(nome=nome)
            db.session.add(ide)
            ides.append(ide)
        db.session.flush()
        print(f"✅ {len(ides)} IDEs")

        # 2. MEMBROS SIMPLES (sem lider_id, sem pastor ainda)
        print("\n👥 Criando membros...")
        membros = []
        
        # Pastores
        for ide in ides:
            pastor = Membro(
                nome=f"Pastor {ide.nome}",
                email=fake.email(),
                cpf=fake.cpf(),
                ativo=True,
                ide_id=ide.id
            )
            db.session.add(pastor)
            membros.append(pastor)
        
        db.session.flush()
        
        # Atualizar pastor_id das IDEs
        for i, ide in enumerate(ides):
            ide.pastor_id = membros[i].id
            
        # Membros regulares
        for _ in range(20):
            membro = Membro(
                nome=fake.name(),
                email=fake.email(),
                cpf=fake.cpf(),
                ativo=True,
                ide_id=random.choice(ides).id
            )
            db.session.add(membro)
            membros.append(membro)
        
        db.session.commit()
        print(f"✅ {len(membros)} membros")

        # 3. USUÁRIOS
        print("\n👤 Criando usuários...")
        admin = User(username='admin', email='admin@admin.com')
        admin.set_password('admin123')
        db.session.add(admin)
        
        # Usuário para primeiro pastor
        pastor_user = User(
            username='pastor',
            email=membros[0].email,
            membro_id=membros[0].id
        )
        pastor_user.set_password('password123')
        db.session.add(pastor_user)
        
        db.session.commit()
        print("✅ 2 usuários")

        # 4. CÉLULAS
        print("\n🔵 Criando células...")
        celulas = []
        lideres = membros[3:8]  # Alguns membros serão líderes
        
        for i, lider in enumerate(lideres[:3]):
            celula = Celula(
                nome=f'Célula {i+1}',
                ide_id=ides[i % len(ides)].id,
                lider_id=lider.id,
                dia_reuniao='Quarta',
                horario_reuniao='19:00'
            )
            db.session.add(celula)
            celulas.append(celula)
        
        db.session.commit()
        print(f"✅ {len(celulas)} células")

        # 5. EVENTOS
        print("\n📅 Criando eventos...")
        for _ in range(5):
            start = fake.future_datetime(end_date='+30d')
            evento = Evento(
                titulo=fake.catch_phrase(),
                descricao=fake.text(max_nb_chars=100),
                data_inicio=start,
                data_fim=start + timedelta(hours=2),
                local='Sede',
                tipo_evento='Culto',
                capacidade_maxima=100
            )
            db.session.add(evento)
        
        db.session.commit()
        print("✅ 5 eventos")

        # 6. PAPÉIS (se roles existirem)
        print("\n🎭 Criando papéis...")
        role_pastor = Role.query.filter_by(name='pastor').first()
        
        if role_pastor:
            for pastor in membros[:3]:  # Primeiros 3 são pastores
                papel = PapelMembro(
                    membro_id=pastor.id,
                    role_id=role_pastor.id
                )
                db.session.add(papel)
            db.session.commit()
            print("✅ Papéis atribuídos")
        else:
            print("⚠️  Roles não encontradas (execute seed_rbac.py primeiro)")

        print("\n" + "="*60)
        print("✅ SEED CONCLUÍDO!")
        print("="*60)
        print(f"📍 IDEs: {len(ides)}")
        print(f"👥 Membros: {len(membros)}")
        print(f"🔵 Células: {len(celulas)}")
        print(f"📅 Eventos: 5")
        print(f"\n🔑 Login: admin / admin123")
        print(f"🔑 Login: pastor / password123")
        print("="*60)

if __name__ == '__main__':
    seed_simplificado()
