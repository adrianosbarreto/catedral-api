from app import db
from flask_login import UserMixin
from datetime import datetime, timedelta
import secrets

class Convite(db.Model):
    __tablename__ = 'convites'
    id = db.Column(db.Integer, primary_key=True)
    token = db.Column(db.String(100), unique=True, nullable=False)
    ide_id = db.Column(db.Integer, db.ForeignKey('ides.id'), nullable=False)
    criado_por_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    data_criacao = db.Column(db.DateTime, default=datetime.utcnow)
    data_expiracao = db.Column(db.DateTime, nullable=False)
    papel_destino = db.Column(db.String(50), nullable=True) # Papel que o convidado terá
    supervisor_destino_id = db.Column(db.Integer, db.ForeignKey('membros.id'), nullable=True) # Supervisor imediato
    usado = db.Column(db.Boolean, default=False)

    ide = db.relationship('Ide', backref='convites')
    criador = db.relationship('User', backref='convites_criados')
    supervisor_destino = db.relationship('Membro', foreign_keys=[supervisor_destino_id])

    def esta_valido(self):
        agora = datetime.utcnow()
        return agora < self.data_expiracao

    def to_dict(self):
        try:
            # Pegar dados básicos com segurança
            token = getattr(self, 'token', None)
            ide_id = getattr(self, 'ide_id', None)
            
            # Tentar pegar IDE
            ide = getattr(self, 'ide', None)
            ide_nome = getattr(ide, 'nome', None) if ide else None
            
            # Tentar pegar Supervisor
            supervisor = getattr(self, 'supervisor_destino', None)
            supervisor_nome = getattr(supervisor, 'nome', None) if supervisor else None
            
            # Tentar pegar Criador
            criador = getattr(self, 'criador', None)
            criador_membro = getattr(criador, 'membro', None) if criador else None
            criador_nome = getattr(criador_membro, 'nome', None) if criador_membro else getattr(criador, 'username', 'N/A')
            criador_role = getattr(criador, 'role', 'membro')
            
            data = {
                'id': self.id,
                'token': token,
                'ide_id': ide_id,
                'ide_nome': ide_nome,
                'data_criacao': self.data_criacao.isoformat() if self.data_criacao else None,
                'data_expiracao': self.data_expiracao.isoformat() if self.data_expiracao else None,
                'papel_destino': getattr(self, 'papel_destino', None),
                'supervisor_destino_id': getattr(self, 'supervisor_destino_id', None),
                'supervisor_destino_nome': supervisor_nome,
                'criado_por_nome': criador_nome,
                'criado_por_papel': criador_role,
                'valido': self.esta_valido()
            }
            
            # Tentar pegar Pastor da Unidade (IDE)
            try:
                pastor = getattr(ide, 'pastor', None) if ide else None
                data['ide_pastor_nome'] = getattr(pastor, 'nome', None) if pastor else None
            except Exception:
                data['ide_pastor_nome'] = None
                
            return data
        except Exception as e:
            print(f"ERROR: Exception in Convite.to_dict: {e}")
            return {
                'id': getattr(self, 'id', None),
                'error': 'Falha interna ao carregar convite'
            }



class User(UserMixin, db.Model):
    __tablename__ = 'user' # Explicitly set table name to match default or ensuring consistency
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(255))
    membro_id = db.Column(db.Integer, db.ForeignKey('membros.id'), nullable=True)
    requer_troca_senha = db.Column(db.Boolean, default=False)

    membro = db.relationship('Membro', backref=db.backref('user', uselist=False))

    def __repr__(self):
        return '<User {}>'.format(self.username)

    def set_password(self, password):
        from werkzeug.security import generate_password_hash
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        from werkzeug.security import check_password_hash
        return check_password_hash(self.password_hash, password)

    @property
    def role(self):
        if self.username == 'admin': return 'admin'
        if self.membro and self.membro.papeis.first():
            papel = self.membro.papeis.first()
            if papel.role_rel:
                return papel.role_rel.name
            return papel.papel
        return 'membro'

    def has_permission(self, permission_name):
        role_name = self.role
        if role_name == 'admin': return True
        
        from app.models import Role
        role_obj = Role.query.filter_by(name=role_name).first()
        if not role_obj: return False
        
        for p in role_obj.permissions:
            if p.name == permission_name:
                return True
        return False




class Membro(db.Model):
    __tablename__ = 'membros'
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120))
    telefone = db.Column(db.String(20))
    cpf = db.Column(db.String(20))
    estado_civil = db.Column(db.String(20))
    data_batismo = db.Column(db.Date)
    data_nascimento = db.Column(db.Date)
    sexo = db.Column(db.String(20))
    ativo = db.Column(db.Boolean, default=True)
    
    tipo = db.Column(db.String(20), default='membro') # 'membro' or 'visitante'
    batizado = db.Column(db.Boolean, default=False)
    
    ide_id = db.Column(db.Integer, db.ForeignKey('ides.id'))
    lider_id = db.Column(db.Integer, db.ForeignKey('membros.id'))
    supervisor_id = db.Column(db.Integer, db.ForeignKey('membros.id'))
    pastor_id = db.Column(db.Integer, db.ForeignKey('membros.id'))
    
    ide = db.relationship('Ide', foreign_keys=[ide_id], backref='membros')
    lider = db.relationship('Membro', foreign_keys=[lider_id], remote_side=[id], backref='liderados')
    supervisor = db.relationship('Membro', foreign_keys=[supervisor_id], remote_side=[id], backref='supervisionados')
    pastor_id_rel = db.relationship('Membro', foreign_keys=[pastor_id], remote_side=[id], backref='pastoreados')
    enderecos = db.relationship('Endereco', backref='membro', lazy='dynamic', cascade='all, delete-orphan')
    papeis = db.relationship('PapelMembro', backref='membro', lazy='dynamic', cascade='all, delete-orphan')

    def to_dict(self):
        return {
            'id': self.id,
            'nome': self.nome,
            'email': self.email,
            'telefone': self.telefone,
            'cpf': self.cpf,
            'estado_civil': self.estado_civil,
            'data_batismo': self.data_batismo.isoformat() if self.data_batismo else None,
            'data_nascimento': self.data_nascimento.isoformat() if self.data_nascimento else None,
            'sexo': self.sexo,
            'ativo': self.ativo,
            'ide_id': self.ide_id,
            'lider_id': self.lider_id,
            'supervisor_id': self.supervisor_id,
            'pastor_id': self.pastor_id,
            'pastor_nome': self.pastor_id_rel.nome if self.pastor_id_rel else None,
            'ide': {'id': self.ide.id, 'nome': self.ide.nome} if self.ide else None,
            'lider': {'id': self.lider.id, 'nome': self.lider.nome} if self.lider else None,
            'supervisor': {'id': self.supervisor.id, 'nome': self.supervisor.nome} if self.supervisor else None,
            'pastor': {'id': self.pastor_id_rel.id, 'nome': self.pastor_id_rel.nome} if self.pastor_id_rel else None,
            'enderecos': [e.to_dict() for e in self.enderecos],
            'papeis_membros': [p.to_dict() for p in self.papeis],
            'tipo': self.tipo,
            'batizado': self.batizado,
            'celulas_lideradas': [{'id': c.id, 'nome': c.nome} for c in self.celulas_lideradas if c.ativo],
            'celulas_supervisionadas': [{'id': c.id, 'nome': c.nome} for c in self.celulas_supervisionadas if c.ativo]
        }


class Ide(db.Model):
    __tablename__ = 'ides'
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    pastor_id = db.Column(db.Integer, db.ForeignKey('membros.id'), nullable=True)

    pastor = db.relationship('Membro', foreign_keys=[pastor_id], backref=db.backref('ides_lideradas', lazy='dynamic'))

    def to_dict(self):
        try:
            return {
                'id': self.id, 
                'nome': self.nome,
                'pastor_id': getattr(self, 'pastor_id', None),
                'pastor_nome': getattr(self.pastor, 'nome', None) if getattr(self, 'pastor', None) else None
            }
        except Exception:
            return {
                'id': self.id,
                'nome': self.nome
            }


class Endereco(db.Model):
    __tablename__ = 'enderecos'
    id = db.Column(db.Integer, primary_key=True)
    membro_id = db.Column(db.Integer, db.ForeignKey('membros.id'), nullable=False)
    cep = db.Column(db.String(10))
    logradouro = db.Column(db.String(100))
    numero = db.Column(db.String(20))
    complemento = db.Column(db.String(100))
    bairro = db.Column(db.String(50))
    cidade = db.Column(db.String(50))
    estado = db.Column(db.String(2))

    def to_dict(self):
        return {
            'id': self.id,
            'cep': self.cep,
            'logradouro': self.logradouro,
            'numero': self.numero,
            'complemento': self.complemento,
            'bairro': self.bairro,
            'cidade': self.cidade,
            'estado': self.estado
        }

# RBAC Models
role_permissions = db.Table('role_permissions',
    db.Column('role_id', db.Integer, db.ForeignKey('roles.id'), primary_key=True),
    db.Column('permission_id', db.Integer, db.ForeignKey('permissions.id'), primary_key=True)
)

class Permission(db.Model):
    __tablename__ = 'permissions'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    description = db.Column(db.String(255))

    def __repr__(self):
        return f'<Permission {self.name}>'

class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False) # e.g. 'admin'
    label = db.Column(db.String(100)) # e.g. 'Administrador'
    
    permissions = db.relationship('Permission', secondary=role_permissions, lazy='subquery',
        backref=db.backref('roles', lazy=True))

    def __repr__(self):
        return f'<Role {self.name}>'

class PapelMembro(db.Model):
    __tablename__ = 'papeis_membros'
    id = db.Column(db.Integer, primary_key=True)
    membro_id = db.Column(db.Integer, db.ForeignKey('membros.id'), nullable=False)
    papel = db.Column(db.String(50), nullable=True) # Deprecated in favor of role_id
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'), nullable=True)

    role_rel = db.relationship('Role') # Renamed to avoid conflict if I used 'role'

    def to_dict(self):
        return {
            'id': self.id,
            'papel': self.role_rel.name if self.role_rel else self.papel,
            'role_id': self.role_id,
            'role_label': self.role_rel.label if self.role_rel else None
        }

class Evento(db.Model):
    __tablename__ = 'eventos'
    id = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String(100), nullable=False)
    descricao = db.Column(db.Text)
    data_inicio = db.Column(db.DateTime, nullable=False)
    data_fim = db.Column(db.DateTime, nullable=False)
    local = db.Column(db.String(100), nullable=False)
    tipo_evento = db.Column(db.String(50), nullable=False)
    capacidade_maxima = db.Column(db.Integer)

    def to_dict(self):
        return {
            'id': self.id,
            'titulo': self.titulo,
            'descricao': self.descricao,
            'data_inicio': self.data_inicio.isoformat() if self.data_inicio else None,
            'data_fim': self.data_fim.isoformat() if self.data_fim else None,
            'local': self.local,
            'tipo_evento': self.tipo_evento,
            'capacidade_maxima': self.capacidade_maxima
        }

class Celula(db.Model):
    __tablename__ = 'celulas'

    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    ide_id = db.Column(db.Integer, db.ForeignKey('ides.id'), nullable=False)
    supervisor_id = db.Column(db.Integer, db.ForeignKey('membros.id'), nullable=True)
    lider_id = db.Column(db.Integer, db.ForeignKey('membros.id'), nullable=False)
    vice_lider_id = db.Column(db.Integer, db.ForeignKey('membros.id'), nullable=True)
    dia_reuniao = db.Column(db.String(20), nullable=True)
    horario_reuniao = db.Column(db.String(10), nullable=True)
    logradouro = db.Column(db.String(100), nullable=True)
    numero = db.Column(db.String(20), nullable=True)
    complemento = db.Column(db.String(100), nullable=True)
    bairro = db.Column(db.String(50), nullable=True)
    cidade = db.Column(db.String(50), nullable=True)
    estado = db.Column(db.String(2), nullable=True)
    cep = db.Column(db.String(10), nullable=True)
    ativo = db.Column(db.Boolean, default=True)
    
    # Relationships
    ide = db.relationship('Ide', foreign_keys=[ide_id], backref='celulas')
    supervisor = db.relationship('Membro', foreign_keys=[supervisor_id], backref='celulas_supervisionadas')
    lider = db.relationship('Membro', foreign_keys=[lider_id], backref='celulas_lideradas')
    vice_lider = db.relationship('Membro', foreign_keys=[vice_lider_id], backref='celulas_vice_lideradas')

    def to_dict(self):
        return {
            'id': self.id,
            'nome': self.nome,
            'ide_id': self.ide_id,
            'supervisor_id': self.supervisor_id,
            'lider_id': self.lider_id,
            'vice_lider_id': self.vice_lider_id,
            'pastor_id': self.ide.pastor_id if self.ide else None,
            'dia_reuniao': self.dia_reuniao,
            'horario_reuniao': self.horario_reuniao,
            'logradouro': self.logradouro,
            'numero': self.numero,
            'complemento': self.complemento,
            'bairro': self.bairro,
            'cidade': self.cidade,
            'estado': self.estado,
            'cep': self.cep,
            'ativo': self.ativo,
            'ide': {'id': self.ide.id, 'nome': self.ide.nome} if self.ide else None,
            'supervisor': {'id': self.supervisor.id, 'nome': self.supervisor.nome, 'telefone': self.supervisor.telefone} if self.supervisor else None,
            'lider': {'id': self.lider.id, 'nome': self.lider.nome, 'telefone': self.lider.telefone} if self.lider else None,
            'vice_lider': {'id': self.vice_lider.id, 'nome': self.vice_lider.nome, 'telefone': self.vice_lider.telefone} if self.vice_lider else None,
        }

class Nucleo(db.Model):
    __tablename__ = 'nucleos'
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    celula_id = db.Column(db.Integer, db.ForeignKey('celulas.id'), nullable=False)
    
    celula = db.relationship('Celula', backref=db.backref('nucleos', cascade='all, delete-orphan'))

    def to_dict(self):
        return {
            'id': self.id,
            'nome': self.nome,
            'celula_id': self.celula_id,
            'membros': [m.to_dict() for m in self.membros_nucleo]
        }

class MembroNucleo(db.Model):
    __tablename__ = 'membros_nucleo'
    id = db.Column(db.Integer, primary_key=True)
    nucleo_id = db.Column(db.Integer, db.ForeignKey('nucleos.id'), nullable=False)
    membro_id = db.Column(db.Integer, db.ForeignKey('membros.id'), nullable=True)
    is_convidado = db.Column(db.Boolean, default=False)
    nome_convidado = db.Column(db.String(100), nullable=True) # For quick visitors
    telefone_convidado = db.Column(db.String(20), nullable=True) # For quick visitors

    nucleo = db.relationship('Nucleo', backref=db.backref('membros_nucleo', cascade='all, delete-orphan'))
    membro = db.relationship('Membro')

    def to_dict(self):
        return {
            'id': self.id,
            'nucleo_id': self.nucleo_id,
            'membro_id': self.membro_id,
            'is_convidado': self.is_convidado,
            'nome_convidado': self.nome_convidado,
            'telefone_convidado': self.telefone_convidado,
            'membro': self.membro.to_dict() if self.membro else None
        }

class FrequenciaCelula(db.Model):
    __tablename__ = 'frequencias_celula'
    id = db.Column(db.Integer, primary_key=True)
    celula_id = db.Column(db.Integer, db.ForeignKey('celulas.id'), nullable=False)
    membro_nucleo_id = db.Column(db.Integer, db.ForeignKey('membros_nucleo.id'), nullable=False)
    data = db.Column(db.Date, nullable=False)
    presente = db.Column(db.Boolean, default=False)

    celula = db.relationship('Celula', backref=db.backref('frequencias', cascade='all, delete-orphan'))
    membro_nucleo = db.relationship('MembroNucleo', backref=db.backref('frequencias', cascade='all, delete-orphan'))

    def to_dict(self):
        return {
            'id': self.id,
            'celula_id': self.celula_id,
            'membro_nucleo_id': self.membro_nucleo_id,
            'data': self.data.isoformat(),
            'presente': self.presente
        }
class SolicitacaoTransferencia(db.Model):
    __tablename__ = 'solicitacoes_transferencia'
    id = db.Column(db.Integer, primary_key=True)
    membro_id = db.Column(db.Integer, db.ForeignKey('membros.id'), nullable=False)
    de_nucleo_id = db.Column(db.Integer, db.ForeignKey('nucleos.id'), nullable=True) # Pode ser nulo se não estava em célula
    para_nucleo_id = db.Column(db.Integer, db.ForeignKey('nucleos.id'), nullable=False)
    solicitante_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    status = db.Column(db.String(20), default='pendente') # 'pendente', 'aceito', 'recusado'
    data_solicitacao = db.Column(db.DateTime, default=datetime.utcnow)
    data_resposta = db.Column(db.DateTime, nullable=True)
    motivo_recusa = db.Column(db.Text, nullable=True)

    membro = db.relationship('Membro', foreign_keys=[membro_id], backref='solicitacoes_transferencia')
    de_nucleo = db.relationship('Nucleo', foreign_keys=[de_nucleo_id])
    para_nucleo = db.relationship('Nucleo', foreign_keys=[para_nucleo_id])
    solicitante = db.relationship('User', foreign_keys=[solicitante_id])

    def to_dict(self):
        return {
            'id': self.id,
            'membro_id': self.membro_id,
            'membro_nome': self.membro.nome if self.membro else None,
            'de_nucleo_id': self.de_nucleo_id,
            'de_nucleo_nome': self.de_nucleo.nome if self.de_nucleo else "Nenhum",
            'de_celula_nome': self.de_nucleo.celula.nome if self.de_nucleo and self.de_nucleo.celula else "Nenhuma",
            'para_nucleo_id': self.para_nucleo_id,
            'para_nucleo_nome': self.para_nucleo.nome if self.para_nucleo else None,
            'para_celula_nome': self.para_nucleo.celula.nome if self.para_nucleo and self.para_nucleo.celula else None,
            'solicitante_id': self.solicitante_id,
            'solicitante_nome': self.solicitante.membro.nome if self.solicitante and self.solicitante.membro else self.solicitante.username,
            'status': self.status,
            'data_solicitacao': self.data_solicitacao.isoformat(),
            'data_resposta': self.data_resposta.isoformat() if self.data_resposta else None
        }
