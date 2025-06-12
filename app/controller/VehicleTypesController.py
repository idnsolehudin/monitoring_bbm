from app import app, db, response
from app.model.vehicletypes import VehicleTypes
from datetime import datetime

from flask import Flask, request, jsonify, abort

def create():
    cc = request.form.get('cc')
    ratio = float(request.form.get('ratio'))
    merk = request.form.get('merk')
    created_by = request.form.get('created_by')
    tipe = request.form.get('type')

    if not cc or not ratio or not merk or not created_by:
        return jsonify({'error' : 'data harus lengkap!'}), 400
    
   
    if ratio >= 11:
        type_encode = 6
    elif ratio >= 9 and ratio <= 10:
        type_encode = 5
    elif ratio >= 7 and ratio <= 8:
        type_encode = 4
    elif ratio > 5 and ratio <= 6:
        type_encode = 3
    elif ratio >= 4.5 and ratio <= 5:
        type_encode = 2
    elif ratio < 4.5:
        type_encode = 1
    

    new_type = VehicleTypes(
        tipe = tipe,
        cc = cc,
        ratio = ratio,
        merk = merk,
        type_encode = type_encode,
        created_by = created_by,
        created_at = datetime.now(),
        updated_at = "null"
    )

    db.session.add(new_type)
    db.session.commit()

    return jsonify({
        'tipe' : new_type.tipe,
        'cc' : new_type.cc,
        'ratio' : new_type.ratio,
        'merk' : new_type.merk,
        'type_encode' : new_type.type_encode,
        'created_by' : new_type.created_by
    })

def index():
    try:
        types = VehicleTypes.query.filter_by(deleted_at=None).all()
        data = []
        for tipe in types:
            vehicle_types = {
                "id" : tipe.id,
                "type" : tipe.tipe,
                "cc" : tipe.cc,
                "ratio" : tipe.ratio,
                "merk" : tipe.merk,
                "type_encode" : tipe.type_encode,
                "created_by" : tipe.creator.name,
                "created_at" : tipe.created_at,
                "updated_at" : tipe.updated_at
            }
            data.append(vehicle_types)
        return jsonify(data)
    except Exception as e:
        print(e)

def update(id):
    vehicle_types = VehicleTypes.query.get(id)

    if not  vehicle_types:
        return jsonify({"message" : "Data tidak ditemukan!"})

    cc = request.form.get('cc'),
    ratio = request.form.get('ratio'),
    merk = request.form.get('merk'),
    tipe = request.form.get('type'),

    if not cc or not ratio or not merk:
        return jsonify({'error' : 'data harus lengkap!'}), 400

    if tipe:
        vehicle_types.tipe =  tipe
    if cc:
        vehicle_types.cc = cc
    if ratio:
        vehicle_types.ratio =  ratio
        if isinstance(ratio, tuple):
            ratio = ratio[0]
            ratio = float(ratio)

            if ratio >= 11:
                type_encode = 6
            elif ratio >= 9 and ratio <= 10:
                type_encode = 5
            elif ratio >= 7 and ratio <= 8:
                type_encode = 4
            elif ratio > 5 and ratio <= 6:
                type_encode = 3
            elif ratio >= 4.5 and ratio <= 5:
                type_encode = 2
            elif ratio < 4.5:
                type_encode = 1

            vehicle_types.type_encode =  type_encode

    if merk:
        vehicle_types.merk =  merk
        
    vehicle_types.updated_at =  datetime.now()
    
    db.session.commit()

    return jsonify({
        "message" : "Data berhasil diperbarui"
    })

def show(id):
    vehicle_types = VehicleTypes.query.get(id)
    if not vehicle_types:
        return jsonify({"error" : "Data tidak ditemukan!"}),404
    
    data_vehicletypes = {
        'id' : vehicle_types.id,
        'type' : vehicle_types.tipe,
        'cc' : vehicle_types.cc,
        'ratio' : vehicle_types.ratio,
        'type_encode' : vehicle_types.type_encode,
        'merk' : vehicle_types.merk,
        'created_at' : vehicle_types.created_at,
        'updated_at' : vehicle_types.updated_at
    }
    return jsonify(data_vehicletypes)

def delete(id):
    vehicle_types = VehicleTypes.query.get(id)
    vehicle_types.soft_delete()
    db.session.commit()

    return jsonify({"message": "data berhasil dihapus..."})
