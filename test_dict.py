import requests
import sys

def test_cell_api(cell_id):
    # This is a bit tricky without a token, but I can use the debug_data.py approach to get data directly from db
    # or just trust the debug_data.py results which showed pastor_id=13 for cell 10.
    pass

# Let's just run debug_data again but focusing on the to_dict results.
from app import create_app
from app.models import Celula, db

app = create_app('production')
with app.app_context():
    celula = Celula.query.filter_by(ativo=True).first()
    if celula:
        data = celula.to_dict()
        print(f"Cell ID: {data.get('id')}")
        print(f"Cell Name: {data.get('nome')}")
        print(f"Pastor ID: {data.get('pastor_id')}")
        print(f"Keys in dict: {list(data.keys())}")
    else:
        print("No active cells found")
