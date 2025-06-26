from app.model.reports import Reports
from app.model.vehicletypes import VehicleTypes
from app.model.vehicles import Vehicles
from app import app,db, response,uploadconfig
import pickle
import numpy as np
import os
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask import request, jsonify, abort
from sqlalchemy import cast, Date
from config import Config
from werkzeug.utils import secure_filename
import uuid
import cv2
from PIL import Image
import pytesseract
import numpy as np
from rapidfuzz import fuzz
import tensorflow as tf
from tensorflow.keras.models import load_model
from tensorflow.keras.applications.mobilenet_v2 import preprocess_input
from sklearn.metrics.pairwise import cosine_similarity
import matplotlib.pyplot as plt
from sqlalchemy import desc


pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
print(pytesseract.get_tesseract_version())

MODEL_PATH = "app/models"
IMG_SIZE = (150, 150)  # sesuaikan dengan ukuran waktu training

def preprocess_image(image_file):
    img = Image.open(image_file).resize(IMG_SIZE)
    img = np.array(img) / 255.0
    return np.expand_dims(img, axis=0)

def calculate_mse(img_tensor, reconstructed_tensor):
    return np.mean((img_tensor - reconstructed_tensor) ** 2)

def extract_text(image_path):
    img = Image.open(image_path)
    text = pytesseract.image_to_string(img)
    return text

# ==== Load model dan data fitur ====
model = load_model('models/mobilenet_feature_extractor.h5')
features_db = np.load('app/models/fitur_spbu.npy')
filenames = np.load('app/models/filenames_spbu.npy', allow_pickle=True)

# ==== Fungsi untuk ekstrak fitur dari gambar uji ====
def extract_features(image_path):
    img = cv2.imread(image_path)
    img = cv2.resize(img, (224, 224))
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    img = preprocess_input(img)
    img = np.expand_dims(img, axis=0)
    features = model.predict(img)
    return features.flatten()

def create():
    # reports = request.get_json()
    shipment = int(request.form.get("shipment"))
    route_id = int(request.form.get("route_id"))
    vehicle_id = int(request.form.get("vehicle_id"))
    spbu_code = int(request.form.get("spbu_code"))
    # last_km = int(request.form.get("last_km"))
    # first_km = int(request.form.get("first_km"))
    # volume_isi = int(request.form.get("volume"))
    receipt = request.files.get("receipt")
    odometer = request.files.get("odometer")
    dispenser = request.files.get("dispenser")
    fulfillment = request.files.get("fulfillment")
    created_by = int(request.form.get("created_by"))


    existing_reports = Reports.query.filter_by(shipment=shipment).first()
    if existing_reports:
        return jsonify({"error": "Nomor Shipment Sudah Ada, Tidak Boleh Sama"})


    if not shipment or not route_id or not vehicle_id or not spbu_code or not receipt:
        return jsonify({"error": "Data harus lengkap!"})
    
    #buat kode upload gambar
    if all ([
        uploadconfig.allowed_file(receipt.filename),
        uploadconfig.allowed_file(odometer.filename),
        uploadconfig.allowed_file(dispenser.filename),
        uploadconfig.allowed_file(fulfillment.filename)
    ]):
        uid = uuid.uuid4()
        file_receipt = secure_filename(receipt.filename)
        file_odometer = secure_filename(odometer.filename)
        file_dispenser = secure_filename(dispenser.filename)
        file_fulfillment = secure_filename(fulfillment.filename)
        rename_receipt = "receipt"+str(uid)+file_receipt
        rename_odometer = "odometer"+str(uid)+file_odometer
        rename_dispenser = "dispenser"+str(uid)+file_dispenser
        rename_fulfillment = "fulfillment"+str(uid)+file_fulfillment



        receipt_path = os.path.join(app.config['UPLOAD_FOLDER'], rename_receipt)
        odometer_path = os.path.join(app.config['UPLOAD_FOLDER'], rename_odometer)
        dispenser_path = os.path.join(app.config['UPLOAD_FOLDER'], rename_dispenser)
        fulfillment_path = os.path.join(app.config['UPLOAD_FOLDER'], rename_fulfillment)
    
        receipt.save(receipt_path)
        odometer.save(odometer_path)
        dispenser.save(dispenser_path)
        fulfillment.save(fulfillment_path)

        #===========prediksi kemiripan foto spbu/fulfillment=============
       
        # === Load model dan fitur dataset ===
        model = load_model('app/models/mobilenet_feature_extractor.h5')
        features_db = np.load('app/models/fitur_spbu.npy')
        filenames = np.load('app/models/filenames_spbu.npy', allow_pickle=True)

        # === Fungsi untuk ekstraksi fitur dari gambar uji ===
        def extract_features(image_path):
            img = cv2.imread(image_path)
            img = cv2.resize(img, (224, 224))
            img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            img = preprocess_input(img)
            img = np.expand_dims(img, axis=0)
            features = model.predict(img)
            return features.flatten()

        # === Gambar uji ===
        test_feature = extract_features(fulfillment_path)

        # === Hitung kemiripan ===
        similarities = cosine_similarity([test_feature], features_db)[0]

        # === Simpan skor kemiripan tertinggi ===
        highest_similarity_score = np.max(similarities)

        # === Cetak hasil jika ingin verifikasi (opsional) ===
        print(f"Skor kemiripan tertinggi: {highest_similarity_score:.2f}")

        #================================================================

        #extract gambar
        # ==============================================================

        def preprocess_image_for_ocr(image_path):
            img = cv2.imread(image_path)
            
            # Resize agar teks lebih besar (tingkatkan akurasi)
            img = cv2.resize(img, None, fx=2, fy=2, interpolation=cv2.INTER_LINEAR)

            # Grayscale
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

            # Bilateral filter untuk hilangkan noise tanpa hilangkan detail tepi
            filtered = cv2.bilateralFilter(gray, 11, 17, 17)

            # Adaptive threshold (hasil lebih halus dan akurat untuk struk)
            thresh = cv2.adaptiveThreshold(
                filtered, 255,
                cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                cv2.THRESH_BINARY, 31, 10
            )

            return thresh

        def extract_text(image_path):
            processed_image = preprocess_image_for_ocr(image_path)
            custom_config = r'--oem 3 --psm 6'
            text = pytesseract.image_to_string(processed_image, config=custom_config)
            return text


        # Eksekusi
        result = extract_text(receipt_path)
        print("=== Hasil OCR ===")
        print(result)



        # =================================================

        odo_text = extract_text(odometer_path)
        ful_text = extract_text(fulfillment_path)
        dis_text = extract_text(dispenser_path)
        rec_text = extract_text(receipt_path)

        import re
        
        # km = re.search(r'Odometer[:\s]*([\d,\.]+)', rec_text)
        liter = re.search(r'\(L\)\s*([\d.,]+)', rec_text, re.IGNORECASE)
        volume = float(liter.group(1).replace(',','.')) if liter else 0
        print(liter)
        
        lines = rec_text.splitlines()

        odometer = None
        for line in lines:
            if fuzz.partial_ratio(line.lower(), 'odometer') > 75:
                match = re.search(r'([\d.,]{4,})', line)
                if match:
                    odometer = match.group(1).replace(',', '').replace('.', '')
                    odometer = int(odometer)
                    break

        print("Odometer:", odometer)
        # km_val = int(km.group(1).replace('.','').replace(',','')) if km else 0

        print(f"liter = {liter}")
        print(f"vol= {volume}")
        # print(f"km = {km_val}")
        if volume == 0:
            return jsonify({"error": "Volume BBM tidak terbaca dari struk. Harap unggah gambar yang jelas."}),400

        if odometer == 0:
            return jsonify({"error": "Kilometer tidak terbaca dari struk. Harap unggah gambar yang jelas."}),400

        #mengambil data kendaraan berdasarkan id kendaraan  yang diinput
        vehicle = Vehicles.query.filter_by(id= vehicle_id, deleted_at = None).first()
        if not vehicle:
            return jsonify({"error": "Kendaraan tidak ditemukan!"})
        
        #kilometer awal
        reports = Reports.query.filter_by(vehicle_id=vehicle_id, deleted_at = None).order_by(Reports.id.desc()).first()
        if reports:
            first_km = reports.last_km
        else:
            first_km = vehicle.first_km
        
        
        distance = odometer - first_km if odometer != 0 else 0
        ratio = distance / volume if volume != 0 else 0
        #mengambil data tipe kendaraan berdasarkan tipe id
        vehicle_types = VehicleTypes.query.filter_by(id=vehicle.type_id).first()
        if not vehicle_types:
            return jsonify({"error": "Tipe Kendaraan Tidak ditemukan!"})
        vehicle_types_encode = vehicle_types.type_encode

        
        model_path = os.path.join(os.path.dirname(__file__), 'isolation_forest_model.pkl')

        with open(model_path, 'rb') as file:
            model = pickle.load(file)

        features = np.array([[ratio, vehicle_types_encode]])

        prediction = model.predict(features)

        created_at = datetime.now()

        data = Reports(
            shipment = shipment,
            route_id = route_id,
            vehicle_id = vehicle_id,
            spbu_code = spbu_code,
            first_km = first_km,
            last_km = odometer,
            distance = distance,
            ratio = ratio,
            volume = volume,
            status = prediction[0],
            receipt = rename_receipt,
            odometer = rename_odometer,
            dispenser = rename_dispenser,
            fulfillment = rename_fulfillment,
            similarity = round(highest_similarity_score, 2),
            created_by = created_by,
            created_at = created_at
        )

        db.session.add(data)
        db.session.commit()

        return jsonify({'success':"data berhasil ditambahkan"})



def index():
    reports = Reports.query.order_by(desc(Reports.created_at)).all()
    data = []
    for report in reports:
        new_data = {
            'id' : report.id,
            'shipment' : report.shipment,
            'route_id' : report.route_id,
            'route' : report.route.description,
            'vehicle_id' : report.vehicle.code,
            'spbu_code' : report.spbu_code,
            'first_km' : report.first_km,
            'last_km' : report.last_km,
            'distance' : report.distance,
            'ratio' : report.ratio,
            'volume' : report.volume,
            'receipt' : report.receipt,
            'status' : report.status,
            'compliance' : report.similarity,
            'created_by' : report.creator.name,
            'created_at' : report.created_at,
            'updated_at' : report.updated_at
        }
        data.append(new_data)

    return jsonify(data)

def detail(id):
    report = Reports.query.get(id)
    if not report:
        return jsonify({'message': 'Report not found'}), 404
 
    data_reports = {
        'id' : report.id,
        'shipment' : report.shipment,
        'route_id' : report.route_id,
        'route' : report.route.description,
        'vehicle_id' : report.vehicle_id,
        'vehicle' : report.vehicle.code,
        'spbu_code' : report.spbu_code,
        'first_km' : report.first_km,
        'last_km' : report.last_km,
        'distance' : report.distance,
        'ratio' : report.ratio,
        'volume' : report.volume,
        'receipt' : report.receipt,
        'odometer' : report.odometer,
        'dispenser' : report.dispenser,
        'fulfillment' : report.fulfillment,
        'status' : report.status,
        'compliance' : report.similarity,
        'created_by' : report.creator.name,
        'created_at' : report.created_at,
        'updated_at' : report.updated_at
    }

    return jsonify(data_reports)

def filtered_reports():
    start_date_str = request.args.get('start_date')
    end_date_str = request.args.get('end_date')

    if not start_date_str or not end_date_str:
        return jsonify({"error": "masukkan tanggal terlebih dahulu"}), 400
    
    try:
        start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
        end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()

        reports = Reports.query.filter(
            cast(Reports.created_at, Date) >= start_date,
            cast(Reports.created_at, Date) <= end_date
        ).order_by(desc(Reports.created_at)).all()

        if not reports:
            return jsonify({"error": "data tidak ditemukan"}), 404

        data = []
        for report in reports:
            new_data = {
                'id' : report.id,
                'shipment' : report.shipment,
                'route_id' : report.route_id,
                'route' : report.route.description,
                'vehicle_id' : report.vehicle.code,
                'spbu_code' : report.spbu_code,
                'first_km' : report.first_km,
                'last_km' : report.last_km,
                'distance' : report.distance,
                'ratio' : report.ratio,
                'volume' : report.volume,
                'receipt' : report.receipt,
                'status' : report.status,
                'compliance' : report.similarity,
                'created_by' : report.creator.name,
                'created_at' : report.created_at,
                'updated_at' : report.updated_at
            }
            data.append(new_data)

        return jsonify(data)
    except ValueError:
        return jsonify({"error": "Invalid date format. Use YYYY-MM-DD"}), 400
    
def current_reports():
    today = datetime.today().date()
    reports = Reports.query.filter(cast(Reports.created_at, Date) == today).order_by(desc(Reports.created_at)).all()

    if not reports: 
        return jsonify({"error": "data tidak ditemukan"}), 404

    data = []
    for report in reports:
        new_data = {
            'id' : report.id,
            'shipment' : report.shipment,
            'route_id' : report.route_id,
            'route' : report.route.description,
            'vehicle_id' : report.vehicle.code,
            'spbu_code' : report.spbu_code,
            'first_km' : report.first_km,
            'last_km' : report.last_km,
            'distance' : report.distance,
            'ratio' : report.ratio,
            'volume' : report.volume,
            'receipt' : report.receipt,
            'status' : report.status,
            'compliance' : report.similarity,
            'created_by' : report.creator.name,
            'created_at' : report.created_at,
            'updated_at' : report.updated_at
        }
        data.append(new_data)

    return jsonify(data),200
    
    
def user_reports(id):
    reports = Reports.query.filter(Reports.created_by ==  id, Reports.deleted_at == None).order_by(desc(Reports.created_at)).all()

    if not reports: 
        return jsonify({"error": "data tidak ditemukan"}), 404

    data = []
    for report in reports:
        new_data = {
            'id' : report.id,
            'shipment' : report.shipment,
            'route_id' : report.route_id,
            'route' : report.route.description,
            'vehicle_id' : report.vehicle.code,
            'spbu_code' : report.spbu_code,
            'first_km' : report.first_km,
            'last_km' : report.last_km,
            'distance' : report.distance,
            'ratio' : report.ratio,
            'volume' : report.volume,
            'receipt' : report.receipt,
            'status' : report.status,
            'compliance' : report.similarity,
            'created_by' : report.creator.name,
            'created_at' : report.created_at,
            'updated_at' : report.updated_at
        }
        data.append(new_data)

    return jsonify(data),200
    

def update(id):
    reports = Reports.query.get(id)
    if not reports: 
        return jsonify({'message': 'Report not found'}), 404
    
    
    if not request.form.get("vehicle_id"):
        return jsonify({"error":"Kode Kendaraan Tidak Boleh Kosong"})
    elif not request.form.get("last_km") or not request.form.get("first_km"):
        return jsonify({"error":"Kilometer Awal dan Akhir tidak boleh kosong"})
    elif not request.form.get("volume"):
        return jsonify({"error":"Volume Tidak Boleh Kosong"})
    elif not request.files.get("receipt"):
        return jsonify({"error": "Bukti Transaksi Tidak Boleh Kosong"})
 
    shipment = int(request.form.get("shipment"))
    route_id = int(request.form.get("route_id"))
    vehicle_id = int(request.form.get("vehicle_id"))
    spbu_code = int(request.form.get("spbu_code"))
    last_km = int(request.form.get("last_km"))
    first_km = int(request.form.get("first_km"))
    volume = int(request.form.get("volume"))
    receipt = request.files.get("receipt")

    if not shipment and not route_id and not vehicle_id and not spbu_code and not last_km and not first_km and not volume and not receipt:
        return jsonify({"error" : "Data Tidak Boleh Kosong!"})
    
    distance = last_km - first_km
    ratio = distance / volume
    #mengambil data kendaraan berdasarkan id kendaraan  yang diinput
    vehicle = Vehicles.query.filter_by(id= vehicle_id).first()
    #mengambil data tipe kendaraan berdasarkan tipe id
    vehicle_types = VehicleTypes.query.filter_by(id=vehicle.type_id).first()
    vehicle_types_encode = vehicle_types.type_encode
    
    model_path = os.path.join(os.path.dirname(__file__), 'isolation_forest_model.pkl')

    with open(model_path, 'rb') as file:
        model = pickle.load(file)

    features = np.array([[ratio, vehicle_types_encode]])

    prediction = model.predict(features)
    
    if shipment:
        reports.shipment = shipment
    if route_id:
        reports.route_id = route_id
    if vehicle_id:
        reports.vehicle_id = vehicle_id
    if first_km:
        reports.first_km = first_km
    if last_km:
        reports.last_km = last_km
    if volume:
        reports.volume = volume
    if receipt and uploadconfig.allowed_file(receipt.filename):
        uid = uuid.uuid4()
        filename = secure_filename(receipt.filename)
        renamefile = "reports"+str(uid)+filename

        receipt.save(os.path.join(app.config['UPLOAD_FOLDER'], renamefile))  
        reports.receipt = renamefile

    reports.updated_at = datetime.now()
    reports.distance = distance
    reports.ratio = ratio
    reports.status = prediction[0]

    db.session.commit()

    return jsonify({
        'success' : 'Data Berhasil Diperbarui',
        'data' : {
            'shipment' : reports.shipment,
            'route_id' : reports.route_id,
            'vehicle' : reports.vehicle.code,
            'spbu_code' : reports.spbu_code,
            'first_km' : reports.first_km,
            'last_km' : reports.last_km,
            'distance' : reports.distance,
            'ratio' : reports.ratio,
            'volume' : reports.volume,
            'receipt' : reports.receipt,
            'status' : reports.status,
            'created_by' : reports.creator.name,
            'created_at' : reports.created_at,
            'updated_at' : reports.updated_at
        }
    }),200

def delete(id):
    report = Reports.query.get(id)

    if not report:
        abort(404)

    try:
        path = {
        "receipt_path" : os.path.join(app.config['UPLOAD_FOLDER'], report.receipt) if report.receipt else None,
        "odometer_path" : os.path.join(app.config['UPLOAD_FOLDER'], report.odometer) if report.odometer else None,
        "dispenser_path" : os.path.join(app.config['UPLOAD_FOLDER'], report.dispenser) if report.dispenser else None,
        "fulfillment_path" : os.path.join(app.config['UPLOAD_FOLDER'], report.fulfillment) if report.fulfillment else None,
        }
        for file in path.values():
            if file and os.path.exists(file):
                os.remove(file)
            
        db.session.delete(report)
        db.session.commit()

        return jsonify({"message": "Data berhasil dihapus"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': 'Gagal menghapus data!', 'error':str(e)}),500





