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
from dotenv import load_dotenv
from config import Config
from flask import Flask

load_dotenv()

app = Flask(__name__)
app.config.from_object(Config)

# def upload():
#     try:
#         title = request.form.get('title')

#         if 'file' not in request.files:
#             return response.badRequest([],'File tidak tersedia')
#         file = request.files['file']

#         if file.filename == '':
#             return response.badRequest([],'File tidak tersedia')
        
#         if file and uploadconfig.allowed_file(file.filename):
#             uid = uuid.uuid4()
#             filename = secure_filename(file.filename)
#             renamefile = "img"+str(uid)+filename

#             file.save(os.path.join(app.config['UPLOAD_FOLDER'], renamefile))

#             uploads = Images(title=title, pathname=renamefile)
#             db.session.add(uploads)
#             db.session.commit()
            
#             return response.success(
#                 {
#                     'title' : title,
#                     'pathname' : renamefile
#                 },
#                 "Sukses mengupload file"
#             )
            
#         else:
#             return response.badRequest([],'File tidak diizinkan')
#     except Exception as e:
#         print(e)

def index():
    try:
        users = Users.query.filter_by(deleted_at =None)
        data = []
        for user in users:
            user_data = {
                'id' : user.id,
                'nik' : user.nik,
                'name' : user.name,
                'status' : user.status,
                'phone' : user.phone,
                'images' : user.image,
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
        'id' : user_detail.id,
        'nik' : user_detail.nik,
        'name' : user_detail.name,
        'status' : user_detail.status,
        'images' : user_detail.image,
        'phone' : user_detail.phone,
        'created_at' : user_detail.created_at,
        'updated_at' : user_detail.updated_at
    }

    return jsonify(data_user)

def create():
    try:
        # mengambil data JSON dari request
        # data = request.get_json()

        name = request.form.get("name")
        nik = request.form.get("nik")
        status = request.form.get("status")
        password = request.form.get("password")
        phone = request.form.get("phone")
        file = request.files.get('images')

        # memeriksa kelengkapan data
        if not name or not nik or not status or  not password:
            return jsonify({'error':'Data tidak lengkap!'}), 400
        
        existing_nik = Users.query.filter_by(nik=nik, deleted_at=None).first()
        if existing_nik:
            return jsonify({"error": "NIK sudah ada!"}),400

        renamefile = None
        
        if file and uploadconfig.allowed_file(file.filename):
            uid = uuid.uuid4()
            filename = secure_filename(file.filename)
            renamefile = "usr"+str(uid)+filename

            file.save(os.path.join(app.config['UPLOAD_FOLDER'], renamefile))

        
        # membuat objek user baru
        new_user = Users (
            name = name,
            nik = nik,
            status = status,
            phone = phone,
            image = renamefile,
            # password = data['password'],
            created_at = datetime.datetime.now(),
            updated_at = None
        )
        # menyimpan objek ke database
        new_user.setPassword(password)
        db.session.add(new_user)
        db.session.commit()

        return jsonify({
            'success' : 'Data Berhasil Disimpan...',
            'data' : {
                'name' : new_user.name,
                'nik' : new_user.nik,
                'status' : new_user.status,
                'phone' : new_user.phone,
                'created_at' : new_user.created_at,
                'image' : new_user.image
            }
        }), 201

    except Exception as e:
        print(e)
        return jsonify({'error': str(e)}), 500 
    

def update(id):
    users = Users.query.get(id)

    if not users:
        return jsonify({"message" : "Data tidak ditemukan"})
    
    nik = request.form.get("nik")
    name = request.form.get("name")
    status = request.form.get("status")
    phone = request.form.get("phone")
    password = request.form.get("password")
    file = request.files.get("images")

    if not nik and not name and not status and not password:
        return jsonify({"error": "lengkapi data terlebih dahulu"}),404
    
    if nik:
        users.nik = nik
    if name:
        users.name = name
    if status:
        users.status = status
    if phone:
        users.phone = phone
    if password:
        users.setPassword(password)
    if file and uploadconfig.allowed_file(file.filename):
        uid = uuid.uuid4()
        filename = secure_filename(file.filename)
        renamefile = "usr"+str(uid)+filename

        file.save(os.path.join(app.config['UPLOAD_FOLDER'], renamefile))
        users.image = renamefile

    users.updated_at = datetime.datetime.now()

    db.session.commit()

    return jsonify({
        'success': 'Data berhasil diperbarui',
        'data' : 
                {
                    'name' : users.name,
                    'nik' : users.nik,
                    'status' : users.status,
                    'phone' : users.phone,
                    'images' : users.image,
                    'updated_at' : users.updated_at
                }
    }),200

def delete(id):
    users = Users.query.get(id)

    if not users:
        abort(404)

    users.soft_delete()
    db.session.commit()

    return jsonify({"message": "Data berhasil dihapus"}), 200

def singleObject(data):
    data = {
        'id' : data.id,
        'nik' : data.nik,
        'name' : data.name,
        'status' : data.status,
        'phone' : data.phone,
        'password' : data.password,
        'image' : data.image
    }

    return data

def login():
    try:
        nik = request.form.get('nik')
        password = request.form.get('password')
        
        user = Users.query.filter_by(nik=nik, deleted_at=None).first()
        # pass_key = Users.query.filter_by(password=password).first()

        if not nik and not password:
            return response.badRequest([],"NIK dan Password tidak boleh kosong")

        if not nik:
            return response.badRequest([],"NIK tidak boleh kosong")
        
        if not password:
            return response.badRequest([],"Password tidak boleh kosong")

        if not user:
            return response.badRequest([], "NIK tidak terdaftar")
        
        if not user.checkPassword(password):
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
