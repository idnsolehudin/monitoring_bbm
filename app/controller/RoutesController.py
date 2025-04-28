from app.model.routes import Routes
from app.model.users import Users
from app import response, app, db
from flask import request, jsonify, abort
from datetime import datetime

def index():
    try:
        routes = Routes.query.all()
        data = []
        for route in routes:
            routes_data = {
                'id': route.id,
                'code': route.code,
                'description': route.description,
                'distance': route.distance,
                'created_by': route.creator.name,  # Mengambil username dari relasi
                'created_at': route.created_at, 
                'updated_at': route.updated_at  
            }
            data.append(routes_data)  
        return jsonify(data)
    except Exception as e:
        print(e)

def detail(id):
    routes_detail = Routes.query.get(id)
    if not routes_detail:
        return jsonify({'message':'Data tidak ditemukan'})

    data_routes = {
        'id': routes_detail.id,
        'code': routes_detail.code,
        'description': routes_detail.description,
        'distance': routes_detail.distance,
        'created_by': routes_detail.creator.name,  # Mengambil username dari relasi
        'created_at': routes_detail.created_at, 
        'updated_at': routes_detail.updated_at  
    }

    return jsonify(data_routes)

def create():
    data = request.get_json()

    required_fields = ['code', 'description', 'distance', 'created_id']
    if not data or not all(key in data for key in required_fields):
        return jsonify({'error': 'Invalid data'}), 400

    new_route = Routes(
        code=data['code'],
        description=data['description'],
        distance=data['distance'],
        created_id=data['created_id'],
        created_at = datetime.now()
    )

    db.session.add(new_route)
    db.session.commit()

    return jsonify({
        'code': new_route.code,
        'description': new_route.description,
        'distance': new_route.distance,
        'created_by': new_route.creator.name,
        'created_at': new_route.created_at
    })

def update(id):
    routes = Routes.query.get(id)

    data = request.get_json()

    if not data or not all(key in data for key in['code', 'description','distance','created_id']):
        return jsonify({"error": "Data Harus Lengkap!"}), 400
    
    routes.code = data['code'],
    routes.description = data['description'],
    routes.distance = data['distance'],
    routes.created_id = data['created_id'],
    routes.updated_at = datetime.now()

    db.session.commit()

    return jsonify({
        'code': routes.code,
        'description': routes.description,
        'distance': routes.distance,
        'created_by': routes.creator.name,
        'updated_at': routes.updated_at
    })

def delete(id):
    routes = Routes.query.get(id)

    if not routes:
        abort(404)

    db.session.delete(routes)
    db.session.commit()

    return jsonify({"message" : "berhasil hapus data"})





