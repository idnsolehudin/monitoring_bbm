import os
import numpy as np
import cv2
from tensorflow.keras.applications import MobileNetV2
from tensorflow.keras.applications.mobilenet_v2 import preprocess_input
from tensorflow.keras.models import Model
from tensorflow.keras.preprocessing import image

# Konfigurasi path
DATASET_DIR = 'app/dataset'
MODEL_DIR = 'app/models'
MODEL_PATH = os.path.join(MODEL_DIR, 'mobilenet_feature_extractor.h5')
FEATURES_PATH = os.path.join(MODEL_DIR, 'fitur_spbu.npy')
FILENAMES_PATH = os.path.join(MODEL_DIR, 'filenames_spbu.npy')

# Buat folder model jika belum ada
os.makedirs(MODEL_DIR, exist_ok=True)

# 1. Buat model CNN (tanpa classifier)
print("[INFO] Membuat model MobileNetV2...")
base_model = MobileNetV2(weights='imagenet', include_top=False, pooling='avg')
model = Model(inputs=base_model.input, outputs=base_model.output)

# 2. Simpan model
model.save(MODEL_PATH)
print(f"[INFO] Model disimpan di: {MODEL_PATH}")

# 3. Load dan proses gambar latih
features = []
filenames = []

print("[INFO] Mengekstrak fitur gambar dari:", DATASET_DIR)
for fname in os.listdir(DATASET_DIR):
    if fname.lower().endswith(('.jpg', '.png', '.jpeg')):
        img_path = os.path.join(DATASET_DIR, fname)

        img = cv2.imread(img_path)
        img = cv2.resize(img, (224, 224))
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        img = preprocess_input(img)
        img = np.expand_dims(img, axis=0)

        feature = model.predict(img).flatten()
        features.append(feature)
        filenames.append(fname)

        print(f"✓ {fname} → fitur shape: {feature.shape}")

# 4. Simpan fitur dan nama file
features = np.array(features)
np.save(FEATURES_PATH, features)
np.save(FILENAMES_PATH, np.array(filenames))

print(f"\n[INFO] Fitur disimpan di: {FEATURES_PATH}")
print(f"[INFO] Nama file disimpan di: {FILENAMES_PATH}")
print("[SELESAI] Semua data berhasil disiapkan.")
