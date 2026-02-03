from app import create_app, db
from app.models import User, Membro, Ide, Celula, Evento, Endereco, PapelMembro
from faker import Faker
import random
from datetime import datetime, timedelta, date

fake = Faker('pt_BR')

def seed_data():
    app = create_app()
    with app.app_context():
        # Clear existing data
        print("Clearing database...")
        db.session.query(PapelMembro).delete()
        db.session.query(Endereco).delete()
        db.session.query(Celula).delete()
        db.session.query(Membro).delete()
        db.session.query(Ide).delete()
        db.session.query(Evento).delete()
        db.session.query(User).delete()
        db.session.commit()

        print("Creating Admin User...")
        admin = User(username='admin', email='admin@example.com')
        admin.set_password('admin123')
        db.session.add(admin)
        db.session.commit()

        print("Creating Members...")
        membros = []
        for _ in range(30):
            membro = Membro(
                nome=fake.name(),
                email=fake.email(),
                telefone=fake.phone_number(),
                cpf=fake.cpf(),
                estado_civil=random.choice(['Solteiro(a)', 'Casado(a)', 'Viúvo(a)']),
                sexo=random.choice(['Masculino', 'Feminino']),
                data_nascimento=fake.date_of_birth(minimum_age=18, maximum_age=80),
                data_batismo=fake.date_between(start_date='-10y', end_date='today'),
                ativo=True
            )
            db.session.add(membro)
            membros.append(membro)
        
        db.session.commit()

        # Add addresses to some members
        print("Adding addresses...")
        for membro in membros[:20]:
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
        
        db.session.commit()

        print("Creating IDEs...")
        ides_data = ['IDE Sede', 'IDE Norte', 'IDE Sul']
        ides = []
        
        # Create dedicated pastors for IDEs
        # We need at least one responsible pastor per IDE, plus maybe others.
        for i, nome_ide in enumerate(ides_data):
            # Create Responsible Pastor
            resp_pastor = Membro(
                nome=f"Pastor Resp {nome_ide}",
                email=fake.email(), 
                cpf=fake.cpf(),
                ativo=True
            )
            db.session.add(resp_pastor)
            db.session.flush() # get ID
            
            # Create IDE with responsible pastor
            ide = Ide(nome=nome_ide, pastor_id=resp_pastor.id)
            db.session.add(ide)
            db.session.flush() # get ID
            ides.append(ide)

            # Assign responsible pastor to this IDE
            resp_pastor.ide_id = ide.id
            db.session.add(resp_pastor)
            
            # Add Role
            db.session.add(PapelMembro(membro_id=resp_pastor.id, papel='Pastor Responsável'))

            # Add another pastor (not responsible)
            aux_pastor = Membro(
                nome=f"Pastor Aux {nome_ide}",
                email=fake.email(),
                cpf=fake.cpf(),
                ativo=True,
                ide_id=ide.id
            )
            db.session.add(aux_pastor)
            db.session.flush()
            db.session.add(PapelMembro(membro_id=aux_pastor.id, papel='Pastor'))

        db.session.commit()

        print("Assigning members to IDEs...")
        # Assign generated members to random IDEs
        for membro in membros:
            if not membro.ide_id: # if not already assigned
                membro.ide_id = random.choice(ides).id
                db.session.add(membro)
        
        db.session.commit()

        print("Creating Cells...")
        celulas = []
        # Leaders are distinct from pastors
        lideres = membros[3:10]
        
        for i in range(6):
            lider = lideres[i]
            celula = Celula(
                nome=f'Célula {fake.first_name()}',
                lider_id=admin.id, # Using Admin User as leader for login purposes mostly, or use Membro ID if we change model
                # Wait, Celula.lider_id FK is to User.id. 
                # Ideally it should be Membro, but for now let's stick to User or link a Membro to User.
                # Let's create Users for leaders
            )
            
            # Update: Create a User for this leader so they can login?
            # For simplicity, assign all cells to the single admin user or create users for leaders.
            # Let's assign to admin for now or create another user.
            
            celula.dia_reuniao = random.choice(['segunda', 'terca', 'quarta', 'quinta', 'sexta', 'sabado'])
            celula.horario = f"{random.randint(18, 20)}:00"
            celula.endereco = fake.street_name()
            celula.numero = fake.building_number()
            celula.bairro = fake.bairro()
            celula.cidade = fake.city()
            celula.estado = fake.state_abbr()
            celula.cep = fake.postcode()
            
            db.session.add(celula)
            celulas.append(celula)
        
        db.session.commit()

        print("Creating Events...")
        tipos_evento = ['Culto', 'Reunião', 'Conferência', 'Workshop']
        for _ in range(5):
            start_date = fake.future_datetime(end_date='+30d')
            end_date = start_date + timedelta(hours=2)
            evento = Evento(
                titulo=fake.catch_phrase(),
                descricao=fake.text(),
                data_inicio=start_date,
                data_fim=end_date,
                local='Sede',
                tipo_evento=random.choice(tipos_evento),
                capacidade_maxima=random.randint(50, 500)
            )
            db.session.add(evento)
        
        db.session.commit()
        print("Seeding completed successfully!")

if __name__ == '__main__':
    seed_data()
