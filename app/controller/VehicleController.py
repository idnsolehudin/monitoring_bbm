from app import app, db, response
from app.model.vehicles import Vehicles
from flask import jsonify, request, abort
from datetime import datetime

def index():
    try:
        data_vehicles = Vehicles.query.all()
        data = []
        for vehicle in data_vehicles:
            new_data = {
                'id' : vehicle.id,
                'code' : vehicle.code,
                'nopol' : vehicle.nopol,
                'type' : vehicle.vehicle_type.tipe,
                'merk' : vehicle.vehicle_type.merk
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
        'code' : data_detail.code,
        'type_id' : data_detail.type_id,
        'type' : data_detail.vehicle_type.tipe,
        'merk' : data_detail.vehicle_type.merk,
        'nopol' : data_detail.nopol,
        # 'images' : data_detail.images,
        'created_by' : data_detail.creator.name,
        'created_at' : data_detail.created_at,
        'updated_at' : data_detail.updated_at
    }

    return jsonify(data_vehicle)

def create():
    data = request.get_json()

    if not data or not all(key in data for key in ['code','type_id','created_by','nopol']):
        return jsonify({'error' : 'Mohon lengkapi data terlebih dahulu!'}), 400
    
    code = data.get('code')
    type_id = data.get('type_id')
    nopol = data.get('nopol')
    created_by = data.get('created_by')
    created_at = datetime.now()

    # duplicate handler
    existing_code = Vehicles.query.filter_by(code=code).first()
    existing_nopol = Vehicles.query.filter_by(nopol=nopol).first()
    if existing_code:
        return jsonify({'error' : 'Kode Kendaraan Sudah ada!'}), 400
    
    if existing_nopol:
        return jsonify({'error' : 'Nomor Polisi Kendaraan Sudah ada!'}), 400

    data_vehicle = Vehicles(
        code = code,
        type_id = type_id,
        nopol = nopol,
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
            'nopol' : data_vehicle.nopol,
            'created_by' : data_vehicle.created_by,
            'created_at' : data_vehicle.created_at
        }
    })

def update(id):
    vehicles = Vehicles.query.get(id)

    if not vehicles:
        return jsonify({"message" : "Data tidak ditemukan"}), 404
    
    data = request.get_json()

    if not data:
        return jsonify({'error' : 'Mohon lengkapi data dulu!!'}), 400
    
    if 'code' in data:
        vehicles.code = data['code']    

    if 'type_id' in data:
        vehicles.type_id = data['type_id']
    if 'nopol' in data:
        vehicles.nopol = data['nopol']
    # vehicles.images = data['images']
    if 'created_by' in data:
        vehicles.created_by = data['created_by']
    vehicles.updated_at = datetime.now()

    db.session.commit()

    return jsonify({
        'success' : 'Data Berhasil Diperbarui...',
        'data' : {
            'code' : vehicles.code,
            'type_id' : vehicles.vehicle_type.tipe,
            'nopol' : vehicles.nopol,
            # 'images' : vehicles.images,
            'created_by' : vehicles.creator.name,
            'updated_at' : vehicles.updated_at
        }
    }), 200

def delete(id):
    vehicles = Vehicles.query.get(id)

    if not vehicles:
        abort(404)
    
    db.session.delete(vehicles)
    db.session.commit()
    
    return jsonify({"succes": "hapus data Sukses..."})




    
