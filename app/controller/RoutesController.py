from app.model.routes import Routes
from app.model.users import Users
from app import response, app, db
from flask import request, jsonify, abort
from datetime import datetime

def index():
    try:
        routes = Routes.query.filter_by(deleted_at = None).all()
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
    code = request.form.get("code")
    description = request.form.get("description")
    distance = request.form.get("distance")
    created_id = request.form.get("created_id")

    existing_code = Routes.query.filter_by(code=code, deleted_at=None).first()
    if  existing_code:
        return jsonify({'error':'Kode sudah ada'}),400
    
    if not code or not description or not distance or not created_id:
        return jsonify({'error': 'Invalid data'}), 400

    new_route = Routes(
        code=code,
        description=description,
        distance=distance,
        created_id=created_id,
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

    code = request.form.get("code")
    description = request.form.get("description")
    distance = request.form.get("distance")
    

    if not code or not description or not distance:
        return jsonify({"error": "Data Harus Lengkap!"}), 400
    
    routes.code = code
    routes.description = description
    routes.distance = distance
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

    routes.soft_delete()
    db.session.commit()

    return jsonify({"message" : "berhasil hapus data"})





