# 🎙️ PANDUAN TANYA JAWAB SIDANG & DISKUSI TEKNIS
*(Dipersiapkan untuk Alvin & Tim Asisten)*

Dokumen ini berisi daftar pertanyaan kritis yang sering ditanyakan oleh dosen pembimbing atau penguji, beserta panduan jawaban ilmiah berbasis data hasil penelitian ini.

---

### Q1: Mengapa akurasi model terbaik berada di angka ~71–79% dan tidak 99%?
> **Jawaban:**  
> "Akurasi ~71–79% ini justru membuktikan bahwa model dievaluasi secara **jujur, realistis, dan bebas dari *shortcut learning* (kebocoran data)**.  
> 1. Dataset kami seimbang ketat **50:50 (27.788 Real vs 27.788 Fake)**, bukan dataset timpang di mana model bisa menebak mayoritas.  
> 2. Data *Real* kami tidak homogen; kami memasukkan dataset **RAVDESS** (suara aktor dengan 8 emosi dinamis) dan **UserLibri**, sehingga model tidak bisa 'menyontek' dari noise mikrofon atau karakteristik satu ruangan saja.  
> 3. Data *Fake* kami menggunakan generator **SOTA (Diffusion / Flow Matching seperti F5TTS dan E2TTS)** yang sangat halus. Nilai AUC 79,62% pada data 55 ribu sampel membuktikan ketahanan (*robustness*) model yang sesungguhnya di dunia nyata."

---

### Q2: Apa kontribusi utama penelitian ini dibanding metode deteksi deepfake biasa?
> **Jawaban:**  
> "Kontribusi utama penelitian ini adalah **pendekatan dua jalur (Two-Branch Architecture)** yang menggabungkan fitur spektral konvensional (MFCC/LFCC) dengan **bukti forensik fisik berbasis produksi suara (Linear Prediction Residual Orde-16 dan Spektrum Modulasi)**.  
> Kami membuktikan bahwa model usulan kami (**E4a**) secara signifikan mengungguli baseline MFCC standar (**B3**) dengan peningkatan AUC sebesar **+10,67%** (Bootstrap 95% CI: `[0.0974, 0.1166]`, $p < 0,05$). Selain itu, pada **14,6% kasus**, bukti residual-modulasi berhasil mengoreksi kesalahan baseline spektral."

---

### Q3: Bukti fisik apa yang secara nyata membedakan suara manusia asli dan deepfake?
> **Jawaban:**  
> "Melalui uji statistik Mann-Whitney U dan FDR Benjamini-Hochberg pada 23 fitur audio:  
> 1. **Entropi Residual LPC Orde-16:** Suara deepfake memiliki entropi residual yang lebih rendah secara signifikan ($p < 10^{-200}$) dibanding manusia asli. Ini membuktikan vokoder AI kehilangan keacakan alami (*natural stochasticity*) getaran pita suara glottal.  
> 2. **Spektrum Modulasi 4–20 Hz:** Suara deepfake mengalami fenomena *oversmoothing* (penghalusan berlebihan) pada pita modulasi artikulasi cepat, yang mencerminkan hilangnya mikro-fluktuasi vokal alami manusia."

---

### Q4: Mengapa suara Real rekaman HP pada pengujian eksternal sempat memiliki akurasi lebih rendah jika memakai threshold kaku 0.50?
> **Jawaban:**  
> "Itu terjadi karena fenomena **Domain Shift dan Kompresi Codec Mikrofon HP (Opus/AAC/MP3)**.  
> Fitur LPC Residual mengukur kesalahan prediksi sinyal gelombang wicara. Ketika suara Real direkam dengan mic HP murah atau terkompresi WhatsApp di ruangan ber-gema, timbul derau kompresi yang meningkatkan residual error. Model residual membacanya sebagai anomali khas suara buatan jika dipotong dengan threshold kaku 0.50.  
> Namun, dengan menerapkan **Calibrated Threshold (~0.60)** atau menggunakan model Random Forest (**E4d / B3**), akurasi suara Real meningkat signifikan menjadi **72% – 81%** tanpa mengorbankan sensitivitas deteksi deepfake (yang tetap mencapai 88% – 100%). Temuan ini kami jadikan pembahasan penting pada Bab 4 sebagai limitasi dan rekomendasi kalibrasi sistem."

---

### Q5: Apakah model ini sudah diuji pada suara di luar data pelatihan?
> **Jawaban:**  
> "Sudah. Kami melakukan *blind test* eksternal pada **170 audio rekaman utuh** dari 4 generator SOTA:  
> - **E2TTS:** Terdeteksi 100,0% Fake  
> - **OpenVoice:** Terdeteksi 97,1% Fake  
> - **VoxCPM:** Terdeteksi 97,1% Fake  
> - **F5TTS:** Terdeteksi 94,1% Fake  
> Hal ini membuktikan metode kami memiliki daya generalisasi yang sangat tinggi terhadap berbagai jenis arsitektur generator deepfake modern."
