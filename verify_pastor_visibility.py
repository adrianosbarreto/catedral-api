from app import create_app, db
from app.models import Membro, User, Role, Ide, Celula
from app.scopes import MembroScope, CellScope

def verify():
    app = create_app()
    with app.app_context():
        print("🔍 Iniciando verificação de visibilidade...")
        
        # 1. Buscar um usuário que seja Pastor de Rede
        pastor_rede_role = Role.query.filter_by(name='pastor_de_rede').first()
        if not pastor_rede_role:
            print("❌ Role 'pastor_de_rede' não encontrada.")
            return

        # Buscar membros que tenham essa role
        from app.models import PapelMembro
        pastores = db.session.query(Membro).join(PapelMembro).filter(
            (PapelMembro.role_id == pastor_rede_role.id) | (PapelMembro.papel == 'pastor_de_rede')
        ).all()
            
        if not pastores:
            print("❌ Nenhum pastor de rede encontrado.")
            return

        for p in pastores:
            print(f"\n👤 Testando para: {p.nome} (ID: {p.id})")
            
            # Verificar relação ides_lideradas
            ides = p.ides_lideradas.all()
            print(f"  🏢 IDEs lideradas: {[ide.nome for ide in ides]}")
            
            # Simular usuário
            user = p.user
            if not user:
                print(f"  ⚠️ Membro {p.nome} não possui usuário associado.")
                continue
                
            # Testar MembroScope
            m_query = Membro.query.filter_by(ativo=True)
            m_scoped = MembroScope.apply(m_query, user)
            m_count = m_scoped.count()
            print(f"  👥 Membros visíveis: {m_count}")
            
            # Testar CellScope
            c_query = Celula.query.filter_by(ativo=True)
            c_scoped = CellScope.apply(c_query, user)
            c_count = c_scoped.count()
            print(f"  🏠 Células visíveis: {c_count}")
            
            if m_count == 0 and c_count == 0:
                print("  ❌ Visibilidade ZERADA. Verifique os vínculos no banco.")
            else:
                print("  ✅ Visibilidade confirmada.")

if __name__ == '__main__':
    verify()
