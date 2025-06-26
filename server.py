import json
from app import app, response
from app.controller import UserController
from app.controller import RoutesController
from app.controller import VehicleTypesController
from app.controller import VehicleController
from app.controller import ReportsController
from flask import jsonify, request, Flask, send_from_directory
from flask_jwt_extended import get_jwt_identity
from flask_jwt_extended import jwt_required, JWTManager, jwt_required, get_jwt
from config import Config
from flask_cors import CORS, cross_origin
# from flask_cors import CORS

# app = Flask(__name__)
# CORS(app)



@app.route('/')
def index():
    return "Hello, World!"

@app.route('/protected', methods = ['GET'])
@jwt_required()
def protected():
    identity = get_jwt_identity()
    user_data = json.loads(identity)
    return response.success(user_data, 'Sukses')

@app.route('/user', methods = ['GET','POST'])
@jwt_required()
def users():
    if request.method == 'GET':
        return UserController.index()
    else:
        return UserController.create()
    
@app.route('/createadmin', methods=['POST'])
@jwt_required()
def createAdmin():
    return UserController.createAdmin()

@app.route('/vehicletypes', methods=['GET','POST'])
def vehicletypes():
    if request.method == 'GET':
        return VehicleTypesController.index()
    else:
        return VehicleTypesController.create()
    
@app.route('/vehicletypes/<int:id>', methods=["PUT", "DELETE", "GET"])
def vehicletypes_update(id):
    if request.method == "PUT":
        return VehicleTypesController.update(id)
    elif request.method == "GET":
        return VehicleTypesController.show(id)
    else:
        return VehicleTypesController.delete(id)
    
@app.route('/vehicles', methods=['GET', 'POST'])
@jwt_required()
def vehicle():
    if request.method == 'GET':
        return VehicleController.index()
    else:
        return VehicleController.create()
    
@app.route('/vehicles/<int:id>', methods=['GET','PUT', 'DELETE'])
@cross_origin(origins=["http://frontendskripsi.test:60"])
def detail_vehicle(id):
    if request.method == 'GET':
        return VehicleController.detail(id)
    if request.method == 'PUT':
        return VehicleController.update(id)
    if request.method == 'DELETE':
        return VehicleController.delete(id)
    
@app.route('/login', methods= ['POST'])
def login():
    return UserController.login()

@app.route('/routes', methods = ['GET','POST'])
def route():
    if request.method == 'GET':
        return RoutesController.index()
    else:
        return RoutesController.create()


@app.route('/routes/<int:id>', methods=['GET', 'PUT', 'DELETE'])
def detail_routes(id):
    if request.method == 'GET':
        return RoutesController.detail(id)
    elif request.method == 'PUT':
        return RoutesController.update(id)
    else:
        return RoutesController.delete(id)

@app.route('/user/<int:id>', methods=['GET','PUT','DELETE'])
@jwt_required()
def detail_user(id):
    if request.method == 'GET':
        return UserController.detail(id)
    elif request.method == 'PUT':
        return UserController.update(id)
    else:
        return UserController.delete(id)

@app.route('/reports', methods=['GET','POST'])
@jwt_required()
def reports():
    if request.method == 'GET':
        return ReportsController.index()
    else:
        return ReportsController.create()
    
@app.route('/reports/<int:id>', methods=['GET','PUT','DELETE'])
@jwt_required()
def detail_reports(id):
    if request.method == 'GET':
        return ReportsController.detail(id)
    elif request.method == 'PUT':
        return ReportsController.update(id)
    else:
        return ReportsController.delete(id)
    
@app.route('/user_reports/<int:id>', methods=['GET'])
@jwt_required()
def user_reports(id):
    return ReportsController.user_reports(id)

@app.route('/current_reports', methods=['GET'])
@jwt_required()
def currentreports():
    return ReportsController.current_reports()

@app.route('/filtered_reports', methods=['GET'])
@jwt_required()
def filteredreports():
    return ReportsController.filtered_reports()

@app.route('/upload', methods=['POST'])
def uploads():
    return UserController.upload()

@app.route('/files/<path:renamefile>')
def uploaded_file(renamefile):
    return send_from_directory(app.config['UPLOAD_FOLDER'], renamefile)

@app.route('/api/gambar/<filename>', methods = ['GET'])
def gambar(filename):
    return send_from_directory('static/upload', filename)


# Simulasi blacklist token
blacklist = set()
jwt = JWTManager(app)
@app.route('/auth/logout', methods=['POST'])
@jwt_required()
def logout():
    jti = get_jwt()["jti"]  # JWT ID
    blacklist.add(jti)
    return jsonify({"message": "Logout successful"}), 200

# Tambahkan fungsi untuk mengecek apakah token diblacklist
@jwt.token_in_blocklist_loader
def check_if_token_in_blacklist(jwt_header, jwt_payload):
    return jwt_payload["jti"] in blacklist

if __name__ == '__main__':
    app.run(debug=False, host="0.0.0.0")