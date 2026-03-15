
from app import create_app, db
from app.models import User, Celula
from flask import Flask, request
from sqlalchemy import func
from app.scopes import CellScope

app = create_app('production')
with app.app_context():
    user = User.query.filter_by(username='diego@diego.com').first()
    if not user:
        print("User diego@diego.com not found")
        exit(1)
    
    print(f"Testing for user: {user.username} (Role: {user.role})")
    
    lat, lng = -1.4716302, -48.4910653
    radius = 50.0
    
    distance_expr = func.acos(
        func.cos(func.radians(lat)) * func.cos(func.radians(Celula.latitude)) * 
        func.cos(func.radians(Celula.longitude) - func.radians(lng)) + 
        func.sin(func.radians(lat)) * func.sin(func.radians(Celula.latitude))
    ) * 6371

    query = db.session.query(Celula, distance_expr.label('distance')).filter(
        Celula.ativo == True,
        Celula.latitude.isnot(None),
        Celula.longitude.isnot(None)
    )

    # Manual apply scope
    query = CellScope.apply(query, user)
    
    nearby_cells_query = query.filter(distance_expr <= radius).order_by('distance').limit(20)
    results = nearby_cells_query.all()
    
    print(f"Found {len(results)} cells within {radius}km for this user's scope.")
    for cell, distance in results[:5]:
        print(f" - {cell.nome} (IDE ID: {cell.ide_id}) - Distance: {distance:.2f}km")

    # Verify if filtered correctly
    if user.role == 'pastor_de_rede':
        my_ide_ids = [ide.id for ide in user.membro.ides_lideradas.all()]
        if not my_ide_ids and user.membro.ide_id:
            my_ide_ids = [user.membro.ide_id]
        
        print(f"User leads IDEs: {my_ide_ids}")
        for cell, distance in results:
            if cell.ide_id not in my_ide_ids:
                print(f"WARNING: Cell {cell.nome} (IDE {cell.ide_id}) should NOT be visible!")
            else:
                print(f"OK: Cell {cell.nome} (IDE {cell.ide_id}) is in scope.")
