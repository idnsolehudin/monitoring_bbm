from app.model.reports import Reports
from app.model.vehicletypes import VehicleTypes
from app.model.vehicles import Vehicles
from app import app,db, response,uploadconfig
import pickle
import numpy as np
import os
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask import request, jsonify, abort
from sqlalchemy import cast, Date
from config import Config
from werkzeug.utils import secure_filename
import uuid



def index():
    reports = Reports.query.all()
    data = []
    for report in reports:
        new_data = {
            'id' : report.id,
            'shipment' : report.shipment,
            'route_id' : report.route_id,
            'route' : report.route.description,
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
        'id' : report.id,
        'shipment' : report.shipment,
        'route_id' : report.route_id,
        'route' : report.route.description,
        'vehicle_id' : report.vehicle_id,
        'vehicle' : report.vehicle.code,
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
                'id' : report.id,
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
            'id' : report.id,
            'shipment' : report.shipment,
            'route_id' : report.route_id,
            'route' : report.route.description,
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

    return jsonify(data),200
    

def create():
    # reports = request.get_json()

    shipment = int(request.form.get("shipment"))
    route_id = int(request.form.get("route_id"))
    vehicle_id = int(request.form.get("vehicle_id"))
    spbu_code = int(request.form.get("spbu_code"))
    last_km = int(request.form.get("last_km"))
    first_km = int(request.form.get("first_km"))
    volume = int(request.form.get("volume"))
    receipt = request.files.get("receipt")
    created_by = int(request.form.get("created_by"))

    existing_reports = Reports.query.filter_by(shipment=shipment).first()
    if existing_reports:
        return jsonify({"error": "Nomor Shipment Sudah Ada, Tidak Boleh Sama"})


    if not shipment or not route_id or not vehicle_id or not spbu_code or not first_km or not last_km or not volume or not receipt:
        return jsonify({"error": "Data harus lengkap!"})
    
    #buat kode upload gambar
    if receipt and uploadconfig.allowed_file(receipt.filename):
        uid = uuid.uuid4()
        filename = secure_filename(receipt.filename)
        renamefile = "reports"+str(uid)+filename

        receipt.save(os.path.join(app.config['UPLOAD_FOLDER'], renamefile))

    
    distance = last_km - first_km
    ratio = distance / volume
    #mengambil data kendaraan berdasarkan id kendaraan  yang diinput
    vehicle = Vehicles.query.filter_by(id= vehicle_id).first()
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
       shipment = shipment,
        route_id = route_id,
        vehicle_id = vehicle_id,
        spbu_code = spbu_code,
        first_km = first_km,
        last_km = last_km,
        distance = distance,
        ratio = ratio,
        volume = volume,
        status = prediction[0],
        receipt = renamefile,
        created_by = created_by,
        created_at = created_at
    )

    db.session.add(data)
    db.session.commit()

    return jsonify({'sucess':"data berhasil ditambahkan"})

def update(id):
    reports = Reports.query.get(id)
    if not reports: 
        return jsonify({'message': 'Report not found'}), 404
    
    
    if not request.form.get("vehicle_id"):
        return jsonify({"error":"Kode Kendaraan Tidak Boleh Kosong"})
    elif not request.form.get("last_km") or not request.form.get("first_km"):
        return jsonify({"error":"Kilometer Awal dan Akhir tidak boleh kosong"})
    elif not request.form.get("volume"):
        return jsonify({"error":"Volume Tidak Boleh Kosong"})
    elif not request.files.get("receipt"):
        return jsonify({"error": "Bukti Transaksi Tidak Boleh Kosong"})
 
    shipment = int(request.form.get("shipment"))
    route_id = int(request.form.get("route_id"))
    vehicle_id = int(request.form.get("vehicle_id"))
    spbu_code = int(request.form.get("spbu_code"))
    last_km = int(request.form.get("last_km"))
    first_km = int(request.form.get("first_km"))
    volume = int(request.form.get("volume"))
    receipt = request.files.get("receipt")

    if not shipment and not route_id and not vehicle_id and not spbu_code and not last_km and not first_km and not volume and not receipt:
        return jsonify({"error" : "Data Tidak Boleh Kosong!"})
    
    distance = last_km - first_km
    ratio = distance / volume
    #mengambil data kendaraan berdasarkan id kendaraan  yang diinput
    vehicle = Vehicles.query.filter_by(id= vehicle_id).first()
    #mengambil data tipe kendaraan berdasarkan tipe id
    vehicle_types = VehicleTypes.query.filter_by(id=vehicle.type_id).first()
    vehicle_types_encode = vehicle_types.type_encode
    
    model_path = os.path.join(os.path.dirname(__file__), 'isolation_forest_model.pkl')

    with open(model_path, 'rb') as file:
        model = pickle.load(file)

    features = np.array([[ratio, vehicle_types_encode]])

    prediction = model.predict(features)
    
    if shipment:
        reports.shipment = shipment
    if route_id:
        reports.route_id = route_id
    if vehicle_id:
        reports.vehicle_id = vehicle_id
    if first_km:
        reports.first_km = first_km
    if last_km:
        reports.last_km = last_km
    if volume:
        reports.volume = volume
    if receipt and uploadconfig.allowed_file(receipt.filename):
        uid = uuid.uuid4()
        filename = secure_filename(receipt.filename)
        renamefile = "reports"+str(uid)+filename

        receipt.save(os.path.join(app.config['UPLOAD_FOLDER'], renamefile))  
        reports.receipt = renamefile

    reports.updated_at = datetime.now()
    reports.distance = distance
    reports.ratio = ratio
    reports.status = prediction[0]

    db.session.commit()

    return jsonify({
        'success' : 'Data Berhasil Diperbarui',
        'data' : {
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
        }
    }),200

def delete(id):
    report = Reports.query.get(id)

    if not report:
        abort(404)

    db.session.delete(report)
    db.session.commit()

    return jsonify({"message": "Data berhasil dihapus"}), 200
