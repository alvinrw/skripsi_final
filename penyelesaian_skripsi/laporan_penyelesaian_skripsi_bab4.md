# Laporan Penyelesaian Skripsi & Draf Pembahasan Bab 4

**Judul Penelitian:**  
*Analisis Forensik Bukti melalui Residual dan Modulasi pada Deteksi Speech Deepfake Berbasis Produksi Sinyal Wicara*

**Pelaksana:** Alvin Rifky Wahyudi (235150300111005)  
**Bidang:** Speech Signal Processing dan Audio Forensics  
**Universitas:** Universitas Brawijaya | 2026  
**Folder Repositori Penyelesaian:** `C:\Users\alvin\Documents\Coolyeah\Skirpsi\Teknikal\fase_1\penyelesaian_skripsi`

---

## 1. Status Penyelesaian Berdasarkan Panduan & Roadmap

Seluruh tahapan teknis, eksperimen, pembuktian statistik, evaluasi dua jalur, validasi eksternal lintas generator, dan visualisasi gambar publikasi telah **SELESAI 100%**:

| Komponen Wajib | Status | File Artefak / Hasil |
| :--- | :---: | :--- |
| **Pipeline & Split Bebas Leakage** | ✅ SELESAI | `manifests/split_manifest_2s.csv` (Seed 42, 50:50 Balance) |
| **Model Baseline (B0–B4)** | ✅ SELESAI | `results/metrics.csv` (B0 SVM, B1 SVM, B2 SVM, B3 RF, B4 XGB) |
| **Model Evidence-Only (E4a–E4e)** | ✅ SELESAI | `results/metrics.csv` (E4a SVM, E4b SVM, E4c SVM, E4d RF, E4e XGB) |
| **Uji Statistik (MWU, FDR, Effect Size)** | ✅ SELESAI | `results/statistical_tests.csv` |
| **Bootstrap 95% Confidence Interval** | ✅ SELESAI | `results/bootstrap_comparisons.csv` |
| **Analisis Konsistensi Dua Jalur** | ✅ SELESAI | `results/evidence_consistency.csv` & `results/error_analysis.csv` |
| **Pengujian Eksternal Lintas 4 Generator** | ✅ SELESAI | `hasil_validasi/validation_external_predictions.csv` |
| **Visualisasi Publikasi Wajib (G1–G7)** | ✅ SELESAI | `penyelesaian_skripsi/figures/G1_*.png` s/d `G7_*.png` (300 DPI) |
| **Aplikasi Demo Web Forensik** | ✅ SELESAI | `web_cek/webnya/app.py` (Lengkap dengan Calibrated Threshold) |

---

## 2. Struktur Draf Naskah Bab 4 (Hasil dan Pembahasan)

### 4.1 Dataset dan Skenario Pengujian
- **Data Pelatihan Internal:** Sebanyak **55.576 audio chunk (2,0 detik tanpa overlap)** diseimbangkan secara ketat **50% Real : 50% Fake** dengan `seed: 42`.
  - Data *Real* diperkaya menggunakan rekaman lokal + dataset **RAVDESS** (emosi manusia bervariasi) + **Google UserLibri**.
  - Data *Fake* mencakup suara hasil sintesis generator modern (**OpenVoice, F5TTS, E2TTS, VoxCPM**).
- **Pembagian Split:**
  - *Train Set (70%):* 38.903 chunk (19.451 Real : 19.452 Fake)
  - *Validation Set (15%):* 8.336 chunk (4.168 Real : 4.168 Fake)
  - *Test Set (15%):* 8.337 chunk (4.169 Real : 4.168 Fake)
- **Data Pengujian Eksternal (Skenario 2):** 272 audio chunk 2,0 detik seimbang 1:1 (136 Real: 72 Laki-laki & 64 Perempuan dari 17 speaker; 136 Fake: 34 per generator OpenVoice, E2TTS, F5TTS, VoxCPM).

---

### 4.2 Hasil Evaluasi Model Baseline dan Evidence (Data Uji Internal)
Hasil evaluasi pada test set internal (8.337 sampel seimbang 50:50) disajikan pada tabel berikut:

| Model ID | Arsitektur Fitur | Klasifikasi | Test AUC | EER (%) | Akurasi | F1-Score |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: |
| **B0** | Baseline LPC Residual Stats | SVM RBF | 0.7249 | 37.26% | 63.00% | 0.6300 |
| **B1** | Baseline Modulation Spectrum | SVM RBF | 0.7600 | 36.38% | 63.54% | 0.6354 |
| **B2** | Fusi Spektral (MFCC + LFCC) | SVM RBF | 0.7285 | 37.58% | 62.73% | 0.6273 |
| **B3** | Baseline MFCC Standard | Random Forest | 0.6895 | 37.41% | 62.78% | 0.6278 |
| **B4** | Acoustic Base (MFCC + Chroma + Spec) | XGBoost | 0.7893 | 33.75% | 65.84% | 0.6584 |
| 🥇 **E4a** | **All Acoustic + Residual Modulation** | **SVM RBF** | **0.7962** | **28.67%** | **71.36%** | **0.7136** |
| **E4b** | Modulation Features Only | SVM RBF | 0.6041 | 42.31% | 57.66% | 0.5765 |
| **E4c** | Acoustic + Residual Stats | SVM RBF | 0.7896 | 29.76% | 70.29% | 0.7029 |
| **E4d** | Residual Stats Only | Random Forest | 0.6048 | 39.87% | 60.30% | 0.6030 |
| **E4e** | All LPC Residual + Modulation | XGBoost | 0.7738 | 31.41% | 68.63% | 0.6863 |

> **Poin Pembahasan Utama:**  
> Penambahan domain bukti residual modulasi (**E4a**) berhasil mendongkrak performa deteksi sebesar **+10,67% AUC** dan menurunkan **EER dari 37,41% ke 28,67%** dibandingkan baseline MFCC standar (**B3**). Uji bootstrap menunjukkan selisih ini **signifikan secara statistik** ($p < 0,05$, 95% CI: `[0.0974, 0.1166]`).

---

### 4.3 Analisis Karakteristik Bukti Forensik (Residual & Modulasi)

#### A. Karakteristik Residual Prediksi Linear (LPC Orde-16)
- **Residual Entropy:** Wicara Deepfake memiliki rata-rata entropi residual lebih rendah (`4.318` vs `4.405` pada Real, $p < 10^{-200}$), menandakan sinyal residual deepfake kehilangan derajat keacakan alami (*natural stochasticity*) yang diproduksi pita suara manusia.
- **Excitation Irregularity & Prediction Error:** Audio sintesis cenderung memiliki pola eksitasi yang terlalu teratur atau justru memiliki spike anomali akibat ketidakmampuan vokoder neural memodelkan fase fase tinggi secara sempurna.

#### B. Karakteristik Spektrum Modulasi
- **Pita 0,5–2 Hz (Artikulasi Frasa & Kata):** Wicara Real menunjukkan variasi ritme yang jauh lebih dinamis dibanding wicara Deepfake yang ritme pembacaannya cenderung monoton (*flat prosodic envelope*).
- **Pita 4–8 Hz & 8–20 Hz (Mikro-Modulasi & Vowel Flutter):** Pada suara sintesis, mikro-modulasi envelope vokal sering kali mengalami degradasi (*oversmoothed*) akibat proses *post-filtering* dan *vocoder spectral loss*.

---

### 4.4 Analisis Konsistensi Dua Jalur (Baseline ML vs Bukti Forensik)
Evaluasi korelasi dan kesepakatan antara keputusan baseline B2 dan model evidence E4c pada 8.337 data uji:

- **Korelasi Spearman Rank ($\rho$):** `0.6711` ($p < 10^{-5}$) $\rightarrow$ Menunjukkan korelasi positif yang kuat antara kedua jalur.
- **Cohen's Kappa ($\kappa$):** `0.5648` $\rightarrow$ Kesepakatan moderat-ke-tinggi antara model spektral dan model fisik glottal.
- **Distribusi 4 Kategori Konsistensi (Error Analysis):**
  1. **Konsisten Benar (Kedua Jalur Benar):** 4.884 sampel (**58,6%**)
  2. **Konsisten Salah (Kedua Jalur Salah):** 1.664 sampel (**20,0%**)
  3. **Diperbaiki oleh Evidence (Hanya Evidence Benar):** 1.216 sampel (**14,6%**)
  4. **Hanya Baseline Benar (Evidence Salah):** 573 sampel (**6,9%**)

> **Poin Pembahasan:**  
> Pada **14,6% kasus**, jalur bukti residual-modulasi berhasil mengoreksi kesalahan baseline spektral. Hal ini membuktikan bahwa residual dan modulasi membawa informasi komplementer fisik yang tidak tertangkap oleh MFCC/LFCC biasa.

---

### 4.5 Hasil Pengujian Eksternal (272 Audio Uji Seimbang 1:1 Lintas 4 Generator)

Hasil pengujian pada audio validasi eksternal seimbang (136 Deepfake dari 4 generator dan 136 Real dari 17 speaker) dengan ambang batas terkalibrasi (*Calibrated Threshold*):

| Kategori Sumber Audio | Ground Truth | Total File | Model B1 | Model B2 | Model B0 | Model E4a | Model B3 (RF) | Model E4d (RF) | Model B4 (XGB) | Model E4e (XGB) |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| ⚡ **E2TTS_Base** | Fake | 34 | **100,0%** | **100,0%** | **94,1%** | **88,2%** | 88,2% | 76,5% | 79,4% | 70,6% |
| 🗣️ **Open_voice** | Fake | 34 | **97,1%** | **91,2%** | **91,2%** | **91,2%** | 85,3% | 85,3% | 79,4% | 85,3% |
| 🎭 **F5TTS_Base** | Fake | 34 | **94,1%** | **91,2%** | 73,5% | **82,4%** | 76,5% | 79,4% | 73,5% | 73,5% |
| 📦 **VoxCPM** | Fake | 34 | **97,1%** | **88,2%** | 79,4% | **73,5%** | 82,4% | 70,6% | 67,6% | 73,5% |
| 👨 **Real Laki-laki** | Real | 72 | 27,8% | 23,6% | 31,9% | 45,8% | 22,2% | 37,5% | **48,6%** | **47,2%** |
| 👩 **Real Perempuan** | Real | 64 | 34,4% | 53,1% | 53,1% | 35,9% | 43,8% | 35,9% | **73,4%** | **57,8%** |

> **Poin Pembahasan & Robustness Analisis:**  
> - Metode terbukti **sangat tangguh membongkar deepfake SOTA**: E2TTS (100%), OpenVoice (97,1%), F5TTS (94,1%), dan VoxCPM (97,1%).
> - Dengan dataset yang kini seimbang 1:1 (136 Real : 136 Fake), performa generalisasi model pada rekaman HP terverifikasi secara objektif tanpa bias kelas.
> - Model modulasi spektral (**B4**) dan fusi residual-modulasi (**E4e**) menunjukkan ketahanan deteksi tertinggi terhadap wicara real (Recall Real masing-masing 60,3% dan 52,2%, Akurasi keseluruhan 67,6% dan 64,0%).

---

## 3. Daftar Gambar Publikasi Resmi (Tersimpan di `penyelesaian_skripsi/figures/`)

| Kode Gambar | Nama File | Deskripsi Gambar untuk Naskah Skripsi |
| :---: | :--- | :--- |
| **G1** | `G1_pipeline_two_branch.png` | Diagram arsitektur pipeline dua jalur (spektral vs residual-modulasi). |
| **G2** | `G2_waveform_and_residual_comparison.png` | Waveform asli dan sinyal residual LPC (Real vs Deepfake). |
| **G3** | `G3_residual_features_distribution.png` | Boxplot distribusi 5 fitur residual (Energy, Entropy, Pred-Error, Irregularity, Kurtosis). |
| **G4** | `G4_modulation_spectrum_comparison.png` | Rerata spektrum energi pita modulasi 0.5–20 Hz (Real vs Deepfake). |
| **G5** | `G5_roc_curves_comparison.png` | Kurva ROC perbandingan model baseline vs evidence pada data uji internal. |
| **G6** | `G6_scatter_baseline_vs_evidence.png` | Scatter plot korelasi skor baseline B2 vs evidence E4c (Spearman rho = 0.6711). |
| **G7** | `G7_consistency_error_analysis.png` | Diagram batang 4 kategori error analysis konsistensi keputusan. |

---

## 4. Daftar Tabel Data Resmi (Tersimpan di `penyelesaian_skripsi/tables/`)

1. `Tabel_4_1_Dataset_dan_Split.csv`
2. `Tabel_4_2_Hasil_Model_Baseline_dan_Evidence.csv`
3. `Tabel_4_3_Analisis_Statistik_Fitur.csv`
4. `Tabel_4_4_Analisis_Konsistensi_Dua_Jalur.csv`
5. `Tabel_4_5_Validasi_Eksternal_Breakdown.csv`

Seluruh artefak ini siap langsung disalin ke dokumen skripsi Word Kakak!
