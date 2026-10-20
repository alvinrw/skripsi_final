# 📌 RINGKASAN EKSEKUTIF HASIL PENELITIAN SKRIPSI
*(Dokumen Panduan Cepat untuk Asisten & Tim Riset)*

**Judul Penelitian:**  
*Analisis Forensik Bukti melalui Residual dan Modulasi pada Deteksi Speech Deepfake Berbasis Produksi Sinyal Wicara*

**Peneliti:** Alvin Rifky Wahyudi (235150300111005)  
**Bidang:** Speech Signal Processing & Audio Forensics | Universitas Brawijaya 2026  
**Folder Arsip Paket:** `C:\Users\alvin\Documents\Coolyeah\Skirpsi\Teknikal\fase_1\ringkasan_hasil_skripsi\`

---

## 💡 1. Latar Belakang & Ide Inti Penelitian (What is this about?)

### Masalah:
Metode deteksi pemalsuan suara (Speech Deepfake) konvensional saat ini umumnya hanya mengandalkan fitur spektral standar seperti **MFCC (Mel-Frequency Cepstral Coefficients)**. Namun, generator AI modern (*neural vocoder / diffusion / flow matching*) kini sudah sangat mahir meniru spektrum frekuensi vokal manusia, sehingga metode MFCC biasa sering tertipu dan menghasilkan akurasi yang rendah.

### Solusi yang Diteliti (Metode Usulan):
Penelitian ini membangun **dua jalur (Two-Branch Detection)**:
1. **Jalur 1 (Baseline Spektral):** Menggunakan fitur konvensional MFCC dan LFCC dengan algoritma machine learning (SVM, Random Forest, XGBoost).
2. **Jalur 2 (Bukti Forensik Wicara):** Mengekstraksi cacat fisik biologis dari produksi sinyal wicara manusia yang gagal ditiru oleh AI:
   - **Residual Prediksi Linear (LPC Orde-16):** Mengukur gelombang eksitasi glottal pita suara (Energy, Entropy, Prediction Error, Excitation Irregularity, Kurtosis).
   - **Spektrum Modulasi (Modulation Spectrum 0.5–20 Hz):** Mengukur dinamika artikulasi ritme vokal pada pita frekuensi lambat (0.5–2 Hz, 2–4 Hz, 4–8 Hz, 8–20 Hz).

---

## 📊 2. Dataset & Protokol Eksperimen yang Digunakan

- **Total Data Pelatihan Internal:** **55.576 audio chunk** (durasi 2,0 detik tanpa overlap).
- **Keseimbangan Kelas:** **Strict 50:50 Balance** (27.788 Real : 27.788 Fake).
  - *Data Real:* Rekaman suara asli lokal + dataset **RAVDESS** (suara aktor dengan 8 emosi dinamis) + **Google UserLibri**.
  - *Data Fake:* Suara kloning AI dari berbagai generator modern (**OpenVoice, F5TTS, E2TTS, VoxCPM**).
- **Pembagian Data (Stratified Split, Seed 42, Bebas Data Leakage):**
  - **Train Set (70%):** 38.903 chunk
  - **Validation Set (15%):** 8.336 chunk (ambang batas keputusan / *threshold EER* ditentukan di sini)
  - **Test Set (15%):** 8.337 chunk (pengujian internal objektif)
- **Data Uji Eksternal (Skenario 2):** **272 audio chunk** seimbang sempurna 50:50 (136 Real dan 136 Fake dari 4 generator SOTA lintas 17 pembicara).

---

## 🏆 3. Hasil Utama Penelitian (The Core Results)

### A. Hasil Evaluasi Data Uji Internal (n = 8.337 Sampel)

| Model ID | Fitur yang Digunakan | Model ML | Test AUC | EER (%) | Akurasi | F1-Score |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: |
| **B3** | Baseline MFCC Standard | Random Forest | 0.6895 | 37.41% | 62.78% | 0.6278 |
| **B0** | Baseline LPC Residual Stats | SVM RBF | 0.7249 | 37.26% | 63.00% | 0.6300 |
| **B2** | Fusi Spektral (MFCC + LFCC) | SVM RBF | 0.7285 | 37.58% | 62.73% | 0.6273 |
| **B1** | Baseline Modulation Spectrum | SVM RBF | 0.7600 | 36.38% | 63.54% | 0.6354 |
| **B4** | Acoustic Base (MFCC + Chroma + Spec) | XGBoost | 0.7893 | 33.75% | 65.84% | 0.6584 |
| 🥇 **E4a** | **All Acoustic + Residual Modulation** | **SVM RBF** | **0.7962** | **28.67%** | **71.36%** | **0.7136** |
| **E4c** | Acoustic + Residual Stats | SVM RBF | 0.7896 | 29.76% | 70.29% | 0.7029 |
| **E4e** | All LPC Residual + Modulation | XGBoost | 0.7738 | 31.41% | 68.63% | 0.6863 |
| **E4d** | Residual Stats Only | Random Forest | 0.6048 | 39.87% | 60.30% | 0.6030 |
| **E4b** | Modulation Features Only | SVM RBF | 0.6041 | 42.31% | 57.66% | 0.5765 |

> **🌟 Kesimpulan Metrik:**  
> Model Usulan **E4a (All Acoustic + Residual Modulation)** terbukti memberikan performa terbaik dengan **AUC 79,62%**, **Akurasi 71,36%**, dan **EER terendah 28,67%**.  
> Terjadi peningkatan **+10,67% AUC** dibandingkan baseline standar MFCC (B3), dan uji **Bootstrap 95% Confidence Interval** mengonfirmasi peningkatan ini **signifikan secara statistik ($p < 0,05$)**.

---

### B. Bukti Fisik yang Ditemukan (Mengapa Suara AI Berbeda?)

1. **Entropi Residual Lebih Rendah ($p < 10^{-200}$):**  
   Sinyal eksitasi residual suara deepfake memiliki entropi rata-rata yang lebih rendah dibanding suara asli manusia (`4.318` vs `4.405`). Hal ini membuktikan generator AI gagal mereproduksi dinamika keacakan mikro (*natural stochasticity*) dari getaran pita suara asli.
2. **Kehilangan Mikro-Modulasi pada Spektrum Modulasi (4–20 Hz):**  
   Suara sintesis mengalami penumpulan/penghalusan (*oversmoothing*) pada frekuensi modulasi tinggi akibat keterbatasan vokoder neural dalam memproduksi artikulasi vokal cepat.

---

### C. Analisis Konsistensi Dua Jalur (Apakah Bukti Fisik Berguna?)

Perbandingan pada 8.337 data uji menunjukkan:
- **Korelasi Spearman Rank ($\rho$):** `0.6711` ($p < 10^{-5}$)
- **Cohen's Kappa ($\kappa$):** `0.5648` (Tingkat kesepakatan tinggi)
- **Error Analysis (4 Kategori):**
  - Kedua Jalur Benar: 4.884 sampel (**58,6%**)
  - Kedua Jalur Salah: 1.664 sampel (**20,0%**)
  - **Diperbaiki oleh Evidence (Hanya Jalur Fisik yang Benar): 1.216 sampel (14,6%)**
  - Hanya Baseline Benar: 573 sampel (**6,9%**)

> **Artinya:** Pada **14,6% kasus**, ketika baseline MFCC gagal menebak, bukti fisik residual-modulasi **berhasil mengoreksi kesalahan tersebut**. Ini membuktikan kedua jalur bersifat komplementer (saling melengkapi).

---

### D. Hasil Pengujian Eksternal (272 Audio Seimbang 50:50 Lintas 4 Generator SOTA)

Diuji pada audio baru di luar data training (*blind test*) dengan keseimbangan 136 Real : 136 Fake:
- ⚡ **E2TTS_Base:** **88,2% – 100,0% Terdeteksi Fake**
- 🗣️ **Open_voice:** **85,3% – 97,1% Terdeteksi Fake**
- 🎭 **F5TTS_Base:** **73,5% – 94,1% Terdeteksi Fake**
- 📦 **VoxCPM:** **70,6% – 97,1% Terdeteksi Fake**
- 👨 **Real Laki-laki (72 chunk):** Terdeteksi hingga **48,6%** (B4 XGBoost) & **45,8%** (E4a SVM)
- 👩 **Real Perempuan (64 chunk):** Terdeteksi hingga **73,4%** (B4 XGBoost) & **57,8%** (E4e XGBoost)
- 🏆 **Model Terbaik pada Validasi Eksternal:** **B4 (Akurasi 67,65%, AUC 70,50%)** dan **B2 (AUC 77,20%, Akurasi 65,07%)**.

---

## 📂 4. Daftar File Penting dalam Folder Ini

Folder `C:\Users\alvin\Documents\Coolyeah\Skirpsi\Teknikal\fase_1\ringkasan_hasil_skripsi\` berisi:

1. **`RINGKASAN_EKSEKUTIF_HASIL_SKRIPSI.md`** $\rightarrow$ Dokumen rangkuman utama ini.
2. **`PANDUAN_TANYA_JAWAB_SIDANG.md`** $\rightarrow$ Kumpulan tanya-jawab kritis seputar metodologi & hasil.
3. **Folder `figures/` (Grafik Publikasi 300 DPI):**
   - `G1_pipeline_two_branch.png` : Diagram alir dua jalur sistem.
   - `G2_waveform_and_residual_comparison.png` : Waveform asli vs residual LPC.
   - `G3_residual_features_distribution.png` : Boxplot 5 fitur residual.
   - `G4_modulation_spectrum_comparison.png` : Rerata pita spektrum modulasi.
   - `G5_roc_curves_comparison.png` : Kurva ROC komparasi model.
   - `G6_scatter_baseline_vs_evidence.png` : Scatter plot konsistensi skor ($\rho = 0.6711$).
   - `G7_consistency_error_analysis.png` : Diagram 4 kuadran error analysis.
4. **Folder `tables/` (File CSV Resmi):**
   - `Tabel_4_1_Dataset_dan_Split.csv`
   - `Tabel_4_2_Hasil_Model_Baseline_dan_Evidence.csv`
   - `Tabel_4_3_Analisis_Statistik_Fitur.csv`
   - `Tabel_4_4_Analisis_Konsistensi_Dua_Jalur.csv`
   - `Tabel_4_5_Validasi_Eksternal_Breakdown.csv`
