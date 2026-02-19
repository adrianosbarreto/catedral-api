from app import create_app, db
from app.models import Membro, User, Role, Celula, MembroNucleo, Nucleo
from app.scopes import MembroScope

def verify_expanded_visibility():
    app = create_app()
    with app.app_context():
        print("🔍 Verificando visibilidade expandida para visitantes...")
        
        # 1. Identificar um visitante que tenha supervisor_id como None mas esteja em uma célula
        visitor = Membro.query.filter_by(tipo='visitante', ativo=True, supervisor_id=None).join(MembroNucleo).first()
        
        if not visitor:
            print("⚠️ Nenhum visitante adequado para teste encontrado (com supervisor_id nulo e em célula).")
            return
            
        print(f"👤 Visitante de Teste: {visitor.nome} (ID: {visitor.id})")
        
        # Pegar a célula do visitante
        link = MembroNucleo.query.filter_by(membro_id=visitor.id).first()
        celula = link.nucleo.celula
        supervisor_id = celula.supervisor_id
        
        if not supervisor_id:
            print("⚠️ A célula do visitante não possui supervisor vinculado.")
            return
            
        supervisor_membro = Membro.query.get(supervisor_id)
        supervisor_user = supervisor_membro.user
        
        if not supervisor_user:
            print(f"⚠️ O supervisor {supervisor_membro.nome} não possui conta de usuário para teste.")
            return

        print(f"👮 Simulando login do Supervisor: {supervisor_membro.nome} (ID: {supervisor_membro.id})")
        print(f"🏠 Célula supervisionada: {celula.nome} (ID: {celula.id})")
        
        # Testar MembroScope
        m_query = Membro.query.filter_by(ativo=True)
        m_scoped = MembroScope.apply(m_query, supervisor_user)
        
        visible_ids = [m.id for m in m_scoped.all()]
        
        if visitor.id in visible_ids:
            print(f"✅ SUCESSO: O visitante {visitor.nome} agora é VISÍVEL para seu supervisor via vínculo de célula!")
        else:
            print(f"❌ FALHA: O visitante {visitor.nome} continua INVISÍVEL para seu supervisor.")

if __name__ == '__main__':
    verify_expanded_visibility()
