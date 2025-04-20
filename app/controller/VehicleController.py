from app import app, db, response
from app.model.vehicles import Vehicles
from flask import jsonify, request, abort

def index():
    try:
        data_vehicles = Vehicles.query.all()
        data = []
        for vehicle in data_vehicles:
            new_data = {
                'id' : vehicle.id,
                'code' : vehicle.code,
                'images' : vehicle.images,
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
        'type_id' : data_detail.vehicle_type.tipe,
        'nopol' : data_detail.nopol,
        'images' : data_detail.images,
        'created_by' : data_detail.creator.name,
        'created_at' : data_detail.created_at,
        'updated_at' : data_detail.updated_at
    }

    return jsonify(data_vehicle)

def create():
    data = request.get_json()

    if not data or not all(key in data for key in ['code','type_id','created_by','nopol', 'images']):
        return jsonify({'error' : 'Invalid data'}), 400
    
    data_vehicle = Vehicles(
        code = data['code'],
        type_id = data['type_id'],
        nopol = data['nopol'],
        images = data['images'],
        created_by = data['created_by'],
        created_at = data['created_at'],
        updated_at = data['updated_at']
    )

    db.session.add(data_vehicle)
    db.session.commit()

    return jsonify({
        'code' : data_vehicle.code,
        'type_id' : data_vehicle.type_id,
        'nopol' : data_vehicle.nopol,
        'images' : data_vehicle.images,
        'created_by' : data_vehicle.created_by,
        'created_at' : data_vehicle.created_at,
        'updated_at' : data_vehicle.updated_at
    })

def update(id):
    vehicles = Vehicles.query.get(id)

    if not vehicles:
        abort(404)
    
    data = request.get_json()

    if not data or not all(key in data for key in ['code','type_id','created_by','nopol', 'images']):
        return jsonify({'error' : 'lengkapi data dulu!!'}), 400
    
    vehicles.code = data['code']
    vehicles.type_id = data['type_id']
    vehicles.nopol = data['nopol']
    vehicles.images = data['images']
    vehicles.created_by = data['created_by']
    vehicles.updated_at = data['updated_at']

    db.session.commit()

    return jsonify({
        'code' : vehicles.code,
        'type_id' : vehicles.type_id,
        'nopol' : vehicles.nopol,
        'images' : vehicles.images,
        'created_by' : vehicles.creator.name,
        'updated_at' : vehicles.updated_at
    }), 200

def delete(id):
    vehicles = Vehicles.query.get(id)

    if not vehicles:
        abort(404)
    
    db.session.delete(vehicles)
    db.session.commit()
    
    return jsonify({"succes": "hapus data Sukses..."})




    
