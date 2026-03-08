import os
import sys
from datetime import datetime

# Adiciona o diretório atual ao path para importar a app
sys.path.append(os.getcwd())

from app import create_app, db
from app.models import Evento

app = create_app('default')

with app.app_context():
    agora = datetime.utcnow()
    print(f"--- Diagnóstico de Eventos Públicos ---")
    print(f"Data/Hora Atual (UTC): {agora}")
    
    # Todos os eventos
    todos = Evento.query.all()
    print(f"Total de eventos no banco: {len(todos)}")
    
    # Eventos por visibilidade
    visibilidades = db.session.query(Evento.tipo_visibilidade, db.func.count(Evento.id)).group_by(Evento.tipo_visibilidade).all()
    print(f"Distribuição de visibilidade: {visibilidades}")
    
    # Detalhes dos eventos públicos
    publicos = Evento.query.filter(Evento.tipo_visibilidade == 'publico').all()
    print(f"Eventos com visibilidade 'publico': {len(publicos)}")
    
    for e in publicos:
        print(f"ID: {e.id} | Titulo: {e.titulo} | Data Fim: {e.data_fim} | Ativo: {e.ativo}")
        if e.data_fim < agora:
            print(f"  -> AVISO: Já expirou (data_fim < agora)")
        if not e.ativo:
            print(f"  -> AVISO: Inativo")
            
    # Testar a query exata usada no endpoint
    query_result = Evento.query.filter(
        Evento.ativo == True,
        Evento.data_fim >= agora,
        Evento.tipo_visibilidade == 'publico'
    ).all()
    print(f"Resultado da query do endpoint: {len(query_result)} eventos")
