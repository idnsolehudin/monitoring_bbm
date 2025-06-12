from app import app, db, response, uploadconfig
from app.model.vehicles import Vehicles
from flask import jsonify, request, abort
from datetime import datetime
import pickle
import numpy as np
import os
from werkzeug.utils import secure_filename
import uuid



def index():
    try:
        data_vehicles = Vehicles.query.filter_by(deleted_at = None).all()
        data = []
        for vehicle in data_vehicles:
            new_data = {
                'id' : vehicle.id,
                'code' : vehicle.code,
                'nopol' : vehicle.nopol,
                'type' : vehicle.vehicle_type.tipe,
                'merk' : vehicle.vehicle_type.merk,
                'images' : vehicle.images
            }
            data.append(new_data)

        return jsonify(data)
    except Exception as e:
        print(e)

def detail(id):
    data_detail = Vehicles.query.get(id)

    if not data_detail:
        abort(404)

    data_vehicle = {
        'id' : data_detail.id,
        'code' : data_detail.code,
        'type_id' : data_detail.type_id,
        'type' : data_detail.vehicle_type.tipe,
        'merk' : data_detail.vehicle_type.merk,
        'nopol' : data_detail.nopol,
        'images' : data_detail.images,
        'created_by' : data_detail.creator.name,
        'created_at' : data_detail.created_at,
        'updated_at' : data_detail.updated_at
    }

    return jsonify(data_vehicle)

def create():
    # data = request.get_json()
    code = request.form.get("code")
    type_id = int(request.form.get("type_id"))
    nopol = request.form.get("nopol")
    images = request.files.get("images")
    created_by = int(request.form.get("created_by"))
    created_at = datetime.now()
    updated_at = None

    # duplicate handler
    existing_code = Vehicles.query.filter_by(code=code, deleted_at=None).first()
    existing_nopol = Vehicles.query.filter_by(nopol=nopol, deleted_at=None).first()
    if existing_code:
        return jsonify({'error' : 'Kode Kendaraan Sudah ada!'}), 400
    
    if existing_nopol:
        return jsonify({'error' : 'Nomor Polisi Kendaraan Sudah ada!'}), 400

    #empty data handler
    if not code or not nopol or not images or not type_id or not created_by:
        return jsonify({"error" : "Data Harus Lengkap, Mohon Lengkapi Data Terlebih Dahulu!"})  

    #upload gambar
    if images and uploadconfig.allowed_file(images.filename):
        uid = uuid.uuid4()
        filename = secure_filename(images.filename)
        renamefile = "vehicle" + str(uid)+filename
    
        images.save(os.path.join(app.config['UPLOAD_FOLDER'], renamefile))
    
    data_vehicle = Vehicles(
        code = code,
        type_id = type_id,
        nopol = nopol,
        images = renamefile,
        created_by = created_by,
        created_at = created_at
    )

    db.session.add(data_vehicle)
    db.session.commit()

    return jsonify({
        'success' : 'Data berhasil ditambahkan!',
        'data' : {
            'code' : data_vehicle.code,
            'type' : data_vehicle.vehicle_type.tipe,
            'merk' : data_vehicle.vehicle_type.merk,
            'image' : data_vehicle.images,
            'nopol' : data_vehicle.nopol,
            'created_by' : data_vehicle.created_by,
            'created_at' : data_vehicle.created_at
        }
    })

def update(id):
    vehicles = Vehicles.query.get(id)

    if not vehicles:
        return jsonify({"error" : "Data tidak ditemukan"}), 404
    
    # data = request.get_json()

    code = request.form.get("code")
    type_id = int(request.form.get("type_id"))
    nopol = request.form.get("nopol")
    images = request.files.get("images")

    if not code and not nopol and not images and not type_id:
        return jsonify({"error" : "Data Harus Lengkap, Mohon Lengkapi Data Terlebih Dahulu!"})  
    
    if code:
        vehicles.code = code    

    if type_id:
        vehicles.type_id = type_id
    if nopol:
        vehicles.nopol = nopol
    if images and uploadconfig.allowed_file(images.filename):
        if vehicles.images:
            old_images_path = os.path.join(app.config['UPLOAD_FOLDER'], vehicles.images)
            if os.path.exists(old_images_path):
                print(f"[DEBUG] File lama ditemukan: {old_images_path}, menghapus...")
                os.remove(old_images_path)
            else:
                print(f"[DEBUG] File lama TIDAK ditemukan: {old_images_path}")

        uid = uuid.uuid4()
        filename = secure_filename(images.filename)
        renamefile = f"vehicle_{str(uid)}_{filename}"

        images.save(os.path.join(app.config['UPLOAD_FOLDER'], renamefile))
        vehicles.images = renamefile

    
    vehicles.updated_at = datetime.now()

    db.session.commit()

    return jsonify({
        'success' : 'Data Berhasil Diperbarui...',
        'data' : {
            'code' : vehicles.code,
            'type_id' : vehicles.vehicle_type.tipe,
            'nopol' : vehicles.nopol,
            'images' : vehicles.images,
            'created_by' : vehicles.creator.name,
            'updated_at' : vehicles.updated_at
        }
    }), 200

def delete(id):
    vehicle = Vehicles.query.get(id)
    vehicle.soft_delete()
    db.session.commit()
    
    return jsonify({"succes": "hapus data Sukses..."})




    
