# 🎙️ Repositori Skripsi Final: Deteksi Speech Deepfake Berbasis Residual Prediksi Linear & Spektrum Modulasi

> **Peneliti:** Alvin Rifky Wahyudi  
> **NIM:** 235150300111005  
> **Program Studi:** Teknik Informatika / Ilmu Komputer — Universitas Brawijaya  
> **Tahun:** 2026  
> **Repositori Resmi:** [github.com/alvinrw/skripsi_final](https://github.com/alvinrw/skripsi_final)

---

## 📌 Ringkasan Eksekutif Penelitian

Penelitian skripsi ini berfokus pada **Deteksi Speech Deepfake** dengan mengintegrasikan dua jalur analisis:
1. **Jalur Akustik Standar (Baseline):** Ekstraksi representasi spektral berbasis **MFCC (240 dimensi)** dan **LFCC (40 dimensi)** yang dipadukan dengan algoritma machine learning (SVM RBF, Random Forest, XGBoost).
2. **Jalur Bukti Forensik Fisik (Evidence):** Ekstraksi anomali sumber eksitasi suara manusia menggunakan **Linear Prediction (LP) Residual (15 dimensi)** serta ritme artikulasi biologis menggunakan **Spektrum Modulasi (7 dimensi)**.

Pendekatan dua jalur ini memungkinkan analisis konsistensi (*cross-domain consistency analysis*) guna mengungkap ketidakwajaran sintetis yang sering luput dari filterbank frekuensi konvensional.

---

## 🗂️ Struktur Repositori

```text
skripsi_final/
├── 📄 README.md                               ← Dokumentasi utama repositori
├── 📄 .gitignore                              ← Konfigurasi pengecualian dataset & model besar
├── 📄 build_validasi_profesional.py           ← Generator visualisasi & laporan evaluasi profesional
├── 📄 build_validation_workbook.mjs           ← Utility spreadsheet validasi
├── 📄 LAPORAN_LENGKAP_PROGRESS_DAN_MANUVER.md ← Laporan teknis lengkap & justifikasi metodologi
│
├── 📁 skripsi_residual_modulasi/              ← Pipeline Utama Eksperimen & Machine Learning
│   ├── configs/baseline.yaml                  ← Konfigurasi terpusat (hyperparameter, seed, audio)
│   ├── figures/                               ← Visualisasi ROC, Confusion Matrix, & perbandingan sinyal
│   ├── hasil.md                               ← Log eksperimen dan metrik model
│   └── src/                                   ← Source code ekstraksi fitur, training & evaluasi
│       ├── audio_io.py                        ← Audio loader, normalisasi & segmentasi 2s
│       ├── extract_features.py                ← Master extractor (MFCC, LFCC, Residual, Modulasi)
│       ├── lfcc.py                            ← Linear Frequency Cepstral Coefficients
│       ├── spectral_features.py               ← Mel-Frequency Cepstral Coefficients
│       ├── residual_features.py               ← Analisis energi, entropi, & kurtosis residual LPC
│       ├── modulation_features.py             ← Filterbank modulasi ritme pita bicara (0.5–20 Hz)
│       ├── train_baseline.py                  ← Training model B0–B4 & E4a–E4e
│       ├── metrics.py                         ← Perhitungan EER, AUC, F1-Score & thresholding
│       ├── statistical_tests.py               ← Uji Mann-Whitney U & Benjamini-Hochberg FDR
│       ├── evidence_consistency.py            ← Spearman ρ & Cohen's κ agreement
│       └── run_pipeline.py                    ← Orchestrator pipeline otomatis
│
├── 📁 web_cek/                                ← Aplikasi Web Demonstrasi & Deteksi Suara
│   └── webnya/
│       ├── app.py                             ← Backend Flask untuk upload & inferensi audio
│       ├── templates/index.html               ← Antarmuka web deteksi interaktif
│       └── test_plot.py                       ← Skrip uji rendering plotting sinyal
│
├── 📁 ringkasan_hasil_skripsi/                ← Panduan Sidang & Materi Eksekutif
│   ├── BUKU_PANDUAN_LENGKAP_SKRIPSI.md        ← Kompendium lengkap persiapan sidang
│   ├── PANDUAN_TANYA_JAWAB_SIDANG.md          ← Tanya jawab skripsi & defensibility dosen penguji
│   ├── RINGKASAN_EKSEKUTIF_HASIL_SKRIPSI.md   ← Rangkuman metrik & temuan kunci
│   ├── figures/                               ← Diagram pipeline G1–G9 & Confusion Matrix
│   └── tables/                                ← Tabel hasil evaluasi lengkap (CSV)
│
├── 📁 penyelesaian_skripsi/                   ← Draft Naskah Bab 4 & Tabel Rekapitulasi
│   ├── laporan_penyelesaian_skripsi_bab4.md   ← Draft Bab 4 Hasil dan Pembahasan
│   ├── figures/                               ← Gambar resolusi tinggi untuk naskah
│   └── tables/                                ← Tabel metrik internal & validasi eksternal
│
├── 📁 docs/thesis_handoff/                    ← Dokumentasi Teknis Modular
│   ├── 01_THESIS_OVERVIEW.md                  ← Gambaran umum penelitian
│   ├── 02_REPOSITORY_MAP.md                   ← Pemetaan kode sumber
│   ├── 03_DATASET_AND_PIPELINE.md             ← Protokol dataset & split bebas leakage
│   ├── 04_MODELS_AND_EXPERIMENTS.md           ← Detail arsitektur model
│   ├── 05_FORENSIC_ANALYSIS.md                ← Teori residual & modulasi
│   ├── 06_RESULTS_AND_EVALUATION.md           ← Evaluasi metrik & statistical illusion
│   └── 07_PROPOSAL_COMPLIANCE.md              ← Kesesuaian proposal skripsi
│
└── 📁 outputs/                                ← Hasil Evaluasi & Workbook Validasi
    ├── hasil_validasi_profesional.xlsx        ← Workbook Excel evaluasi multi-model
    └── validasi_external/                     ← Grafik analisis kategori & performa speaker
```

---

## ⚡ Panduan Instalasi & Menjalankan

### 1. Prasyarat Environment
Gunakan Python 3.10+ (disarankan menggunakan Virtual Environment):

```powershell
# Buat dan aktifkan virtual environment
python -m venv .venv
.venv\Scripts\Activate.ps1

# Instal dependensi utama
pip install numpy pandas scipy scikit-learn librosa soundfile xgboost pyyaml joblib tqdm statsmodels flask
```

### 2. Menjalankan Web Detector (Inference App)
Aplikasi web Flask memungkinkan pengujian file suara secara instan:

```powershell
cd web_cek/webnya
python app.py
```
Buka browser di `http://127.0.0.1:5000` untuk mengakses antarmuka deteksi suara.

### 3. Menjalankan Pipeline Eksperimen
Untuk menjalankan pipeline ekstraksi fitur dan evaluasi:

```powershell
cd skripsi_residual_modulasi

# Smoke test validasi fungsi ekstraksi fitur
python src/run_pipeline.py --steps smoke

# Jalankan evaluasi pipeline bertahap
python src/run_pipeline.py --steps manifest splits leakage features train stats consistency
```

---

## 📊 Rangkuman Model & Hasil Kunci

### A. Taksonomi Model
* **Baseline Spektral (B0–B4):**
  * `B0`: SVM RBF (MFCC 240-dim)
  * `B1`: SVM RBF (LFCC 40-dim)
  * `B2`: SVM RBF (MFCC + LFCC)
  * `B3`: Random Forest (MFCC + LFCC)
  * `B4`: XGBoost (MFCC + LFCC)
* **Bukti Forensik (E4a–E4e):**
  * `E4a`: SVM RBF (Residual LPC 15-dim)
  * `E4b`: SVM RBF (Modulasi 7-dim)
  * `E4c`: SVM RBF (Residual + Modulasi 22-dim)
  * `E4d`: Random Forest (Residual + Modulasi)
  * `E4e`: XGBoost (Residual + Modulasi)

### B. Temuan Ilmiah Utama
1. **Independensi Bukti:** Korelasi keputusan (*Cohen's κ*) antara jalur baseline (B2) dan jalur forensik (E4c) mendekati 0. Hal ini membuktikan bahwa fitur Residual dan Modulasi **menangkap dimensi anomali fisik yang ortogonal/independen** dari representasi akustik konvensional.
2. **Sensitivitas Residual:** Fitur `res_energy_mean_p16` menunjukkan *Rank-Biserial Correlation* hingga `-0.70` (kategori *large effect size*), membuktikan adanya pelemahan energi residual eksitasi pada suara sintetis.
3. **Pemberitahuan Metrik (Statistical Illusion):** Penelitian ini memprioritaskan **EER (Equal Error Rate)** dan **AUC-ROC** dibanding Akurasi biasa untuk menghindari bias ilusi performa pada dataset audio yang tidak seimbang (*class imbalance*).

---

## 🔒 Kebijakan Data & Checkpoint Model (Git Policy)

Sesuai best practice repositori kode ilmiah dan batasan ukuran file GitHub (100MB limit):
* **Dataset Audio (`.wav`, `.flac`, `Folder_dataset/`, `data/`):** Tidak disertakan dalam repositori git karena berukuran total > 11 GB.
* **Model Checkpoints (`*.joblib`):** Bobot model terkompilasi (seperti `B3` [166 MB] dan `E4d` [230 MB]) dikecualikan dari Git commit. File checkpoint dapat diunduh terpisah atau dihasilkan kembali (*reproduced*) dengan menjalankan `python src/run_pipeline.py --steps train`.
* **Intermediate Features (`features_train.csv` ~230MB):** Dikecualikan dari git; dapat di-generate otomatis via script `extract_features.py`.

---

## 📜 Lisensi & Sitasi

Hak Cipta (c) 2026 Alvin Rifky Wahyudi — Universitas Brawijaya.  
Kode sumber dilisensikan di bawah ketentuan akademik untuk keperluan riset, reproduktifitas penelitian, dan pengembangan ilmu pengetahuan.
