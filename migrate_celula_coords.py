import os
import time
import requests
from app import create_app, db
from app.models import Celula

import json
from datetime import datetime

def backup_data(celulas):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"backup_celulas_{timestamp}.json"
    
    backup_list = []
    for c in celulas:
        backup_list.append(c.to_dict())
        
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(backup_list, f, ensure_ascii=False, indent=4)
    
    print(f"📦 Backup de segurança criado: {filename}")
    return filename

def migrate():
    app = create_app('production')
    with app.app_context():
        # Buscar TODAS as células ativas para o backup
        todas_celulas = Celula.query.filter_by(ativo=True).all()
        backup_file = backup_data(todas_celulas)

        # Buscar apenas as que precisam de geocodificação para o processamento
        celulas_pendentes = [c for c in todas_celulas if c.latitude is None or c.longitude is None]
        
        print(f"🔍 Encontradas {len(celulas_pendentes)} células para geocodificar.")

        if not celulas_pendentes:
            print("✅ Todas as células já possuem coordenadas.")
            return

        for celula in celulas_pendentes:
            # Montar a query de busca
            # Logradouro, Numero, Bairro, Cidade - Estado, Brasil
            address_parts = []
            if celula.logradouro: address_parts.append(celula.logradouro)
            if celula.numero: address_parts.append(celula.numero)
            if celula.bairro: address_parts.append(celula.bairro)
            if celula.cidade: address_parts.append(celula.cidade)
            if celula.estado: address_parts.append(celula.estado)
            address_parts.append("Brasil")

            search_query = ", ".join(address_parts)
            print(f"📍 Geocodificando: {celula.nome} -> {search_query}")

            try:
                # API Nominatim (OpenStreetMap) - Respeitar limite de 1req/sec
                response = requests.get(
                    "https://nominatim.openstreetmap.org/search",
                    params={
                        "format": "json",
                        "q": search_query,
                        "limit": 1
                    },
                    headers={
                        "User-Agent": "IgrejaEmFoco-App/1.0"
                    }
                )
                data = response.json()

                if data and len(data) > 0:
                    lat = float(data[0]["lat"])
                    lng = float(data[0]["lon"])
                    
                    celula.latitude = lat
                    celula.longitude = lng
                    db.session.commit()
                    print(f"   ✅ Sucesso: {lat}, {lng}")
                else:
                    # Tentar busca simplificada apenas com CEP se falhar
                    if celula.cep:
                        print(f"   ⚠️ Falha no endereço completo. Tentando apenas por CEP: {celula.cep}")
                        response = requests.get(
                            "https://nominatim.openstreetmap.org/search",
                            params={
                                "format": "json",
                                "q": f"{celula.cep}, Brasil",
                                "limit": 1
                            },
                            headers={
                                "User-Agent": "IgrejaEmFoco-App/1.0"
                            }
                        )
                        data = response.json()
                        if data and len(data) > 0:
                            lat = float(data[0]["lat"])
                            lng = float(data[0]["lon"])
                            celula.latitude = lat
                            celula.longitude = lng
                            db.session.commit()
                            print(f"   ✅ Sucesso pelo CEP: {lat}, {lng}")
                        else:
                            print(f"   ❌ Não foi possível localizar: {celula.nome}")
                    else:
                        print(f"   ❌ Não foi possível localizar: {celula.nome}")

            except Exception as e:
                print(f"   💥 Erro ao processar {celula.nome}: {e}")
                db.session.rollback()

            # Delay para evitar banimento do Nominatim
            time.sleep(1.2)

        print("\n🏁 Migração concluída.")

if __name__ == "__main__":
    migrate()
