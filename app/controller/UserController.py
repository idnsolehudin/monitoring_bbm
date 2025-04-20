import json
from app.model.users import Users
from app.model.images import Images
from app import response, app, db, uploadconfig
from flask import request, jsonify, abort, request
import os
from flask_jwt_extended import *
import datetime
import uuid
from werkzeug.utils import secure_filename

def upload():
    try:
        title = request.form.get('title')

        if 'file' not in request.files:
            return response.badRequest([],'File tidak tersedia')
        file = request.files['file']

        if file.filename == '':
            return response.badRequest([],'File tidak tersedia')
        
        if file and uploadconfig.allowed_file(file.filename):
            uid = uuid.uuid4()
            filename = secure_filename(file.filename)
            renamefile = "flask"+str(uid)+filename

            file.save(os.path.join(app.config['UPLOAD_FOLDER'], renamefile))

            uploads = Images(title=title, pathname=renamefile)
            db.session.add(uploads)
            db.session.commit()
            
            return response.success(
                {
                    'title' : title,
                    'pathname' : renamefile
                },
                "Sukses mengupload file"
            )
            
        else:
            return response.badRequest([],'File tidak diizinkan')
    except Exception as e:
        print(e)

def index():
    try:
        users = Users.query.all()
        data = []
        for user in users:
            user_data = {
                'id' : user.id,
                'nik' : user.nik,
                'name' : user.name,
                'status' : user.status,
            }
            data.append(user_data)
        return jsonify(data)
    except Exception as e:
        print(e)

#Controller untuk membuat admin
def createAdmin() :
    try:
        name = request.form.get('name')
        nik = request.form.get('nik')
        password = request.form.get('password')
        status = "admin"

        admin = Users(nik=nik, name=name, status=status)
        admin.setPassword(password)
        db.session.add(admin)
        db.session.commit()

        return jsonify({"message" : "Admin berhasil dibuat"}), 200
    except Exception as e:
        print(e)


def detail(id):
    user_detail = Users.query.get(id)
    if not user_detail:
        abort(404)

    data_user = {
        'nik' : user_detail.nik,
        'name' : user_detail.name,
        'password' : user_detail.password,
        'status' : user_detail.status,
        'created_at' : user_detail.created_at,
        'updated_at' : user_detail.updated_at
    }

    return jsonify(data_user)

def create():
    # mengambil data JSON dari request
    data = request.get_json()

    # memeriksa kelengkapan data
    if not data or 'name' not in data or 'nik' not in data or 'status' not in data or 'created_at' not in data or 'password'  not in data:
        jsonify({'error':'Data tidak lengkap!'}), 400

    # membuat objek user baru
    new_user = Users (
        name = data['name'],
        nik = data['nik'],
        status = data['status'],
        password = data['password'],
        created_at = data['created_at'],
        updated_at = data['updated_at']
    )

    # menyimpan objek ke database
    db.session.add(new_user)
    db.session.commit()

    return jsonify({
        'name' : new_user.name,
        'nik' : new_user.nik,
        'status' : new_user.status,
        'password' : new_user.password,
        'created_at' : new_user.created_at,
        'updated_at' : new_user.updated_at
    }), 201

# def login():
#     """
#     Endpoint untuk login pengguna.
#     Menerima NIK dan password dalam format JSON.
#     """
#     try:
#         # Ambil semua pengguna dari database
#         users = Users.query.all()

#         # Ambil data dari request body
#         data = request.get_json()

#         if not data or "nik" not in data or "password" not in data:
#             return jsonify({"success": False, "message": "NIK dan Password wajib diisi"}), 400

#         nik = data.get("nik")
#         password = data.get("password")

#         # Validasi tipe data
#         if not isinstance(nik, int) or not isinstance(password, str):
#             return jsonify({"success": False, "message": "Format data salah. NIK harus integer dan Password string"}), 400

#         # Periksa data dengan "database" pengguna
#         for user in users:
#             if user.nik == nik and user.password == password:
#                 return jsonify({"success": True, "message": "Login berhasil"}), 200

#         # Jika tidak ditemukan
#         return jsonify({"success": False, "message": "NIK atau Password salah"}), 401

#     except Exception as e:
#         print("Error:", str(e))  # Debug log
#         return jsonify({"success": False, "message": f"Terjadi kesalahan: {str(e)}"}), 500

def update(id):
    users = Users.query.get(id)

    if not users:
        return jsonify({"message" : "Data tidak ditemukan"})
    
    data = request.get_json()

    if not data:
        return jsonify({"error": "lengkapi data terlebih dahulu"})
    
    if 'nik' in data:
        users.nik = data['nik']
    if 'name' in data:
        users.name = data['name']
    if 'status' in data:
        users.status = data['status']
    if 'password' in data:
        users.password = data['password']
    if 'updated_at' in data:
        users.updated_at = data['updated_at']

    db.session.commit()

    return jsonify({
        'message': 'Data berhasil diupdate',
        'data' : 
                {
                    'name' : users.name,
                    'nik' : users.nik,
                    'status' : users.status,
                    'updated_at' : users.updated_at
                }
    }),200

def delete(id):
    users = Users.query.get(id)

    if not users:
        abort(404)

    db.session.delete(users)
    db.session.commit()

    return jsonify({"message": "Data berhasil dihapus"}), 200

def singleObject(data):
    data = {
        'id' : data.id,
        'nik' : data.nik,
        'name' : data.name,
        'status' : data.status,
        'password' : data.password
    }

    return data

def login():
    try:
        nik = request.form.get('nik')
        password = request.form.get('password')
        
        user = Users.query.filter_by(nik=nik).first()

        if not user:
            return response.badRequest([], "NIK tidak terdaftar")
        
        if not user.password:
            return response.badRequest([], "Password salah!")
        
        data = singleObject(user)
        expires = datetime.timedelta(days=1)
        expires_refresh = datetime.timedelta(days=3)

        access_token = create_access_token(identity=json.dumps(data), fresh=True, expires_delta=expires)
        refresh_token = create_refresh_token(identity=json.dumps(data), expires_delta=expires_refresh)

        return response.success({
            "data":data,
            "access_token": access_token,
            "refresh_token": refresh_token,
        }, "Success!")

    except Exception as e:
        print(e)


# Jalankan aplikasi Flask
if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1', port=5000)
