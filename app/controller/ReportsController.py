from app.model.reports import Reports
from app.model.vehicletypes import VehicleTypes
from app.model.vehicles import Vehicles
from app import db, response
import pickle
import numpy as np
import os
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask import request, jsonify, abort
from sqlalchemy import cast, Date


def index():
    reports = Reports.query.all()
    data = []
    for report in reports:
        new_data = {
            'shipment' : report.shipment,
            'route_id' : report.route_id,
            'vehicle_id' : report.vehicle.code,
            'spbu_code' : report.spbu_code,
            'first_km' : report.first_km,
            'last_km' : report.last_km,
            'distance' : report.distance,
            'ratio' : report.ratio,
            'volume' : report.volume,
            'receipt' : report.receipt,
            'status' : report.status,
            'created_by' : report.creator.name,
            'created_at' : report.created_at,
            'updated_at' : report.updated_at
        }
        data.append(new_data)

    return jsonify(data)

def detail(id):
    report = Reports.query.get(id)
    if not report:
        return jsonify({'message': 'Report not found'}), 404
 
    data_reports = {
        'shipment' : report.shipment,
        'route_id' : report.route_id,
        'vehicle_id' : report.vehicle.code,
        'spbu_code' : report.spbu_code,
        'first_km' : report.first_km,
        'last_km' : report.last_km,
        'distance' : report.distance,
        'ratio' : report.ratio,
        'volume' : report.volume,
        'receipt' : report.receipt,
        'status' : report.status,
        'created_by' : report.creator.name,
        'created_at' : report.created_at,
        'updated_at' : report.updated_at
    }

    return jsonify(data_reports)

def filtered_reports():
    start_date_str = request.args.get('start_date')
    end_date_str = request.args.get('end_date')

    if not start_date_str or not end_date_str:
        return jsonify({"error": "masukkan tanggal terlebih dahulu"}), 400
    
    try:
        start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
        end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()

        reports = Reports.query.filter(
            cast(Reports.created_at, Date) >= start_date,
            cast(Reports.created_at, Date) <= end_date
        ).all()

        if not reports:
            return jsonify({"error": "data tidak ditemukan"}), 404
        
        # result = [
        #     {"shipment": r.shipment, "ratio": r.ratio, "created_at": r.created_at.strftime('%Y-%m-%d')}
        #     for r in reports
        # ]
        # return jsonify(result)
    
        data = []
        for report in reports:
            new_data = {
                'shipment' : report.shipment,
                'route_id' : report.route_id,
                'vehicle_id' : report.vehicle.code,
                'spbu_code' : report.spbu_code,
                'first_km' : report.first_km,
                'last_km' : report.last_km,
                'distance' : report.distance,
                'ratio' : report.ratio,
                'volume' : report.volume,
                'receipt' : report.receipt,
                'status' : report.status,
                'created_by' : report.creator.name,
                'created_at' : report.created_at,
                'updated_at' : report.updated_at
            }
            data.append(new_data)

        return jsonify(data)
    except ValueError:
        return jsonify({"error": "Invalid date format. Use YYYY-MM-DD"}), 400
    
def current_reports():
    today = datetime.today().date()
    reports = Reports.query.filter(cast(Reports.created_at, Date) == today).all()

    if not reports: 
        return jsonify({"error": "data tidak ditemukan"}), 404

    data = []
    for report in reports:
        new_data = {
            'shipment' : report.shipment,
            'route_id' : report.route_id,
            'vehicle_id' : report.vehicle.code,
            'spbu_code' : report.spbu_code,
            'first_km' : report.first_km,
            'last_km' : report.last_km,
            'distance' : report.distance,
            'ratio' : report.ratio,
            'volume' : report.volume,
            'receipt' : report.receipt,
            'status' : report.status,
            'created_by' : report.creator.name,
            'created_at' : report.created_at,
            'updated_at' : report.updated_at
        }
        data.append(new_data)

    return jsonify(data)
    

def create():
    reports = request.get_json()

    data_requirement = ['vehicle_id','first_km', 'last_km','volume']

    if not reports or not all(key in reports for key in data_requirement):
        return jsonify({"error": "tolong lengkapi data dulu kawann..."})
    
    distance = reports["last_km"] - reports["first_km"]
    ratio = distance / reports["volume"]
    #mengambil data kendaraan berdasarkan id kendaraan  yang diinput
    vehicle = Vehicles.query.filter_by(id= reports["vehicle_id"]).first()
    #mengambil data tipe kendaraan berdasarkan tipe id
    vehicle_types = VehicleTypes.query.filter_by(id=vehicle.type_id).first()
    vehicle_types_encode = vehicle_types.type_encode
    
    model_path = os.path.join(os.path.dirname(__file__), 'isolation_forest_model.pkl')

    with open(model_path, 'rb') as file:
        model = pickle.load(file)

    features = np.array([[ratio, vehicle_types_encode]])

    prediction = model.predict(features)

    created_at = datetime.now()

    data = Reports(
       shipment = reports["shipment"],
        route_id = reports["route_id"],
        vehicle_id = reports["vehicle_id"],
        spbu_code = reports["spbu_code"],
        first_km = reports["first_km"],
        last_km = reports["last_km"],
        distance = distance,
        ratio = ratio,
        volume = reports["volume"],
        status = prediction[0],
        receipt = reports["receipt"],
        created_by = reports["created_by"],
        created_at = created_at
    )

    db.session.add(data)
    db.session.commit()

    return jsonify({'sucess':"data berhasil ditambahkan"})

def update(id):
    reports = Reports.query.get(id)
    if not reports: 
        return jsonify({'message': 'Report not found'}), 404
    
    data = request.get_json()

    if not data:
        return jsonify({"error" : "mohon lengkapi data terlebih dahulu!"})
    
    distance = data["last_km"] - data["first_km"]
    ratio = distance / data["volume"]
    #mengambil data kendaraan berdasarkan id kendaraan  yang diinput
    vehicle = Vehicles.query.filter_by(id= data["vehicle_id"]).first()
    #mengambil data tipe kendaraan berdasarkan tipe id
    vehicle_types = VehicleTypes.query.filter_by(id=vehicle.type_id).first()
    vehicle_types_encode = vehicle_types.type_encode
    
    model_path = os.path.join(os.path.dirname(__file__), 'isolation_forest_model.pkl')

    with open(model_path, 'rb') as file:
        model = pickle.load(file)

    features = np.array([[ratio, vehicle_types_encode]])

    prediction = model.predict(features)
    
    if 'shipment' in data:
        reports.shipment = data['shipment']
    if 'route_id' in data:
        reports.route_id = data['route_id']
    if 'vehicle_id' in data:
        reports.vehicle_id = data['vehicle_id']
    if 'first_km' in data:
        reports.first_km = data['first_km']
    if 'last_km' in data:
        reports.last_km = data['last_km']
    if 'volume' in data:
        reports.volume = data['volume']
    if 'receipt' in data:
        reports.receipt = data['receipt']  
    reports.updated_at = datetime.now()
    reports.distance = distance
    reports.ratio = ratio
    reports.status = prediction[0]

    db.session.commit()

    return jsonify({
       'shipment' : reports.shipment,
        'route_id' : reports.route_id,
        'vehicle' : reports.vehicle.code,
        'spbu_code' : reports.spbu_code,
        'first_km' : reports.first_km,
        'last_km' : reports.last_km,
        'distance' : reports.distance,
        'ratio' : reports.ratio,
        'volume' : reports.volume,
        'receipt' : reports.receipt,
        'status' : reports.status,
        'created_by' : reports.creator.name,
        'created_at' : reports.created_at,
        'updated_at' : reports.updated_at
    }),200

def delete(id):
    report = Reports.query.get(id)

    if not report:
        abort(404)

    db.session.delete(report)
    db.session.commit()

    return jsonify({"message": "Data berhasil dihapus"}), 200
