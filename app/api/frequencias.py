from flask import jsonify, request
from flask_jwt_extended import jwt_required
from app.api import api
from app.models import db, FrequenciaCelula, MembroNucleo
from datetime import datetime

@api.route('/celulas/<int:celula_id>/frequencias', methods=['GET'])
@jwt_required()
def get_frequencias(celula_id):
    data_str = request.args.get('data')
    if not data_str:
        return jsonify({'error': 'Data is required'}), 400
    
    try:
        data_obj = datetime.strptime(data_str, '%Y-%m-%d').date()
    except ValueError:
        return jsonify({'error': 'Invalid date format (YYYY-MM-DD)'}), 400

    frequencias = FrequenciaCelula.query.filter_by(
        celula_id=celula_id, 
        data=data_obj
    ).all()
    
    return jsonify([f.to_dict() for f in frequencias])

@api.route('/celulas/<int:celula_id>/frequencias', methods=['POST'])
@jwt_required()
def save_frequencias(celula_id):
    data_list = request.get_json() or []
    if not isinstance(data_list, list):
        data_list = [data_list]

    for item in data_list:
        membro_nucleo_id = item.get('membro_nucleo_id')
        data_str = item.get('data')
        presente = item.get('presente', False)

        if not membro_nucleo_id or not data_str:
            continue

        data_obj = datetime.strptime(data_str, '%Y-%m-%d').date()

        # Check for existing record
        frequencia = FrequenciaCelula.query.filter_by(
            celula_id=celula_id,
            membro_nucleo_id=membro_nucleo_id,
            data=data_obj
        ).first()

        if frequencia:
            frequencia.presente = presente
        else:
            frequencia = FrequenciaCelula(
                celula_id=celula_id,
                membro_nucleo_id=membro_nucleo_id,
                data=data_obj,
                presente=presente
            )
            db.session.add(frequencia)

    db.session.commit()
    return jsonify({'message': 'Frequencies saved successfully'})
@api.route('/celulas/<int:celula_id>/frequencias/datas', methods=['GET'])
@jwt_required()
def get_frequencia_datas(celula_id):
    # Get dates and count of attendees for this cell
    from sqlalchemy import func
    results = db.session.query(
        FrequenciaCelula.data,
        func.count(FrequenciaCelula.id).filter(FrequenciaCelula.presente == True).label('presentes')
    ).filter_by(
        celula_id=celula_id
    ).group_by(FrequenciaCelula.data).order_by(FrequenciaCelula.data.desc()).all()
    
    return jsonify([{
        'data': r.data.isoformat(),
        'presentes': r.presentes
    } for r in results])
