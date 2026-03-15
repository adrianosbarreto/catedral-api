
from app import create_app, db
from app.models import Celula, User
import json

app = create_app('production')
with app.app_context():
    admin = User.query.filter_by(role='admin').first()
    if not admin:
        print("No admin user found")
        exit(1)
        
    print(f"Testing with Admin: {admin.username}")
    
    from app.scopes import CellScope
    q = Celula.query.filter_by(ativo=True)
    total_active = q.count()
    
    scoped_q = CellScope.apply(q, admin)
    admin_view = scoped_q.count()
    
    print(f"Total Active Cells: {total_active}")
    print(f"Admin View (Scoped): {admin_view}")
    
    cells_with_coords = q.filter(Celula.latitude.isnot(None), Celula.longitude.isnot(None)).count()
    print(f"Cells with coordinates: {cells_with_coords}")
    
    cells_missing_coords = total_active - cells_with_coords
    print(f"Cells missing coordinates: {cells_missing_coords}")
    
    if admin_view < total_active:
        print("RESULT: Admin sees fewer cells than total active!")
    else:
        print("RESULT: Admin sees all active cells.")
