# 🤖 Dokumentasi & Panduan Model Checkpoints Skripsi

Dokumentasi ini menjelaskan seluruh model *machine learning* (format `.joblib`) yang dihasilkan dari pipeline penelitian:
**"Analisis Forensik Bukti melalui Residual dan Modulasi pada Deteksi Speech Deepfake"**

---

## 📋 Daftar Model yang Tersedia

Total terdapat **10 model terlatih** (Seed 42) yang terbagi dalam dua kelompok:

### 1. Kelompok Baseline Spektral (MFCC & LFCC)
Model berbasis representasi akustik dan frekuensi standar:

| File Model | Algoritma | Fitur Input | Dimensi | Ukuran File | Keterangan & Performa |
|---|---|---|---|---|---|
| `B0_seed42.joblib` | SVM (RBF Kernel) | MFCC (Static, $\Delta$, $\Delta\Delta$) | 240 | ~43.7 MB | Baseline akustik standar (mel-scale) |
| `B1_seed42.joblib` | SVM (RBF Kernel) | LFCC | 40 | ~7.1 MB | Filterbank linear (sensitif frekuensi tinggi) |
| `B2_seed42.joblib` | SVM (RBF Kernel) | MFCC + LFCC | 280 | ~50.5 MB | Fusi spektral sederhana |
| `B3_seed42.joblib` | Random Forest (200 trees) | MFCC + LFCC | 280 | ~166.7 MB | Model non-linear ensemble pohon |
| `B4_seed42.joblib` | **XGBoost Classifier** | **MFCC + LFCC** | **280** | **~0.8 MB** | ⭐ **Model Baseline Terbaik (AUC: 0.8636, EER: 38.6%)** |

### 2. Kelompok Bukti Forensik Fisik (Evidence-Only)
Model yang dilatih murni pada karakteristik anomali sumber eksitasi suara (Residual) dan ritme bicara (Modulasi):

| File Model | Algoritma | Fitur Input | Dimensi | Ukuran File | Keterangan & Performa |
|---|---|---|---|---|---|
| `E4a_seed42.joblib` | SVM (RBF Kernel) | LP Residual (p=16) | 15 | ~3.3 MB | Ablasi domain eksitasi vokal |
| `E4b_seed42.joblib` | SVM (RBF Kernel) | Spektrum Modulasi (0.5–20 Hz) | 7 | ~2.6 MB | Ablasi ritme biologis artikulasi |
| `E4c_seed42.joblib` | **SVM (RBF Kernel)** | **Residual + Modulasi** | **22** | **~4.7 MB** | ⭐ **Model Forensik Utama (AUC: 0.5909, EER: 52.3%)** |
| `E4d_seed42.joblib` | Random Forest (200 trees) | Residual + Modulasi | 22 | ~230.7 MB | Model non-linear ensemble bukti forensik |
| `E4e_seed42.joblib` | XGBoost Classifier | Residual + Modulasi | 22 | ~0.9 MB | Gradient boosting bukti forensik |

---

## 📦 Struktur Isi File `.joblib`

Setiap file `.joblib` disimpan sebagai objek `dict` Python dengan struktur standar berikut:

```python
{
    'model': pipeline_object,       # Sklearn Pipeline (Imputer -> StandardScaler -> Classifier)
    'features': feature_names_list, # List nama kolom fitur input yang diharapkan
    'feature_group': str,           # 'mfcc', 'lfcc', 'mfcc_lfcc', 'residual', 'modulation', dll.
    'model_type': str,              # 'svm', 'rf', atau 'xgboost'
    'seed': int,                    # 42
    'val_threshold': float,         # Ambang batas keputusan (EER threshold) dari validation set
    'experiment_id': str            # Contoh: 'B4', 'E4c', dll.
}
```

---

## 💻 Cara Me-load & Menggunakan Model di Python

### 1. Load Model
```python
import joblib
import numpy as np

# Load model B4 (Baseline XGBoost)
checkpoint = joblib.load("B4_seed42.joblib")
model = checkpoint['model']
threshold = checkpoint['val_threshold']
feature_names = checkpoint['features']

print(f"Model ID: {checkpoint['experiment_id']}")
print(f"Threshold EER: {threshold}")
print(f"Jumlah Fitur yang Dibutuhkan: {len(feature_names)}")
```

### 2. Melakukan Prediksi
```python
# Misalkan X_input adalah matriks fitur berdimensi (n_samples, n_features)
# Pastikan urutan kolom sesuai dengan checkpoint['features']

# Prediksi probabilitas / decision function (skor deepfake)
if hasattr(model, "predict_proba"):
    scores = model.predict_proba(X_input)[:, 1]
else:
    scores = model.decision_function(X_input)

# Klasifikasi biner menggunakan threshold EER validation set
predictions = (scores >= threshold).astype(int)
# 0 = Suara Asli (Real / Bonafide)
# 1 = Suara Palsu (Deepfake / Spoofed)

for score, pred in zip(scores, predictions):
    label_str = "DEEPFAKE" if pred == 1 else "REAL"
    print(f"Skor: {score:.4f} | Keputusan: {label_str}")
```

---

## ⚠️ Catatan Batasan GitHub & Distribusi File

1. **Kenapa file model ini di-zip terpisah?**
   - GitHub memiliki **batas ukuran file 100 MB per file** untuk commit git standar.
   - File model `E4d_seed42.joblib` (230 MB) dan `B3_seed42.joblib` (166 MB) melebihi batas tersebut.
   - Total seluruh model yang sudah di-zip adalah **~187 MB**.
2. **Cara Distribusi yang Direkomendasikan:**
   - **GitHub Releases:** Buat release baru di repositori GitHub (`https://github.com/alvinrw/skripsi_final/releases/new`), lalu unggah file `models_checkpoints.zip` (Releases mendukung file hingga 2 GB).
   - **Google Drive / OneDrive:** Unggah file zip ke cloud storage publik, dan cantumkan tautannya pada `README.md` utama.
