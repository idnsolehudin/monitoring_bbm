from app import app, db, response
from app.model.vehicletypes import VehicleTypes

from flask import Flask, request, jsonify, abort

def create():
    data = request.get_json()

    if not data or not 'tipe' in data or not 'cc' in data or not 'ratio' in data or not 'merk' in data:
        return jsonify({'error' : 'data harus lengkap!'}), 400
    
    new_type = VehicleTypes(
        tipe = data['tipe'],
        cc = data['cc'],
        ratio = data['ratio'],
        merk = data['merk'],
        type_encode = data['type_encode'],
        created_by = data['created_by'],
        created_at = data['created_at'],
        updated_at = data['updated_at']
    )

    db.session.add(new_type)
    db.session.commit()

    return jsonify({
        'tipe' : new_type.tipe,
        'cc' : new_type.cc,
        'ratio' : new_type.ratio,
        'merk' : new_type.merk,
        'type_encode' : new_type.type_encode,
        'created_by' : new_type.created_by,
        'created_at' : new_type.created_at,
        'updated_at' : new_type.updated_at
    })

def index():
    try:
        types = VehicleTypes.query.all()
        data = []
        for type in types:
            vehicle_types = {
                "id" : type.id,
                "type" : type.tipe,
                "cc" : type.cc,
                "ratio" : type.ratio,
                "merk" : type.merk,
                "type_encode" : type.type_encode,
                "created_by" : type.creator.name,
                "created_at" : type.created_at,
                "updated_at" : type.updated_at
            }
            data.append(vehicle_types)
        return jsonify(data)
    except Exception as e:
        print(e)

def update(id):
    vehicle_types = VehicleTypes.query.get(id)

    if not  vehicle_types:
        abort(404)

    data = request.get_json()

    if not data:
        return jsonify({"error": "Data mohon lengkapi dulu pak..."})
    
    if "tipe" in data:
        vehicle_types.tipe =  data["tipe"]
    if "cc" in data:
        vehicle_types.cc =  data["cc"]
    if "ratio" in data:
        vehicle_types.ratio =  data["ratio"]
    if "merk" in data:
        vehicle_types.merk =  data["merk"]
    if "created_by" in data:
        vehicle_types.created_by =  data["created_by"]
    if "type_encode" in data:
        vehicle_types.type_encode =  data["type_encode"]
    if "updated_at" in data:
        vehicle_types.updated_at =  data["updated_at"]
    
    db.session.commit()

    return jsonify({
        "message" : "Data berhasil diupdate"
    })

def delete(id):
    vehicle_types = VehicleTypes.query.get(id)

    if not vehicle_types:
        abort(404)

    db.session.delete(vehicle_types)
    db.session.commit()

    return jsonify({"message": "data berhasil dihapus..."})
