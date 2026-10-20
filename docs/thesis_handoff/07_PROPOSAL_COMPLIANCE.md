# Kesesuaian rancangan tertulis dengan implementasi

## Status dokumen acuan

Tidak ada berkas yang diberi nama proposal/praproposal formal atau Bab 1–3 dalam workspace. Acuan yang dapat dibaca adalah `Panduan_Skripsi_Alvin_Residual_Modulasi_Speech_Deepfake.docx` (judul “Panduan Pelaksanaan Skripsi”), terutama paragraf 20, 27–39, 45–67, 70–108, 115–126 dan tabel 8, 18, 24–30. Karena panduan itu merujuk “praproposal” lain yang tidak tersedia, audit ini **tidak menyimpulkan kepatuhan terhadap proposal resmi**. Matriks berikut membandingkan panduan yang tersedia dengan kode/artefak, sebagai bahan diskusi dengan dosen.

| Komponen | Rancangan tertulis | Implementasi/bukti | Status audit |
|---|---|---|---|
| Rumusan 1: klasifikasi MFCC/LFCC | Kinerja SVM, RF, XGB; KNN/MLP disebut dalam rumusan, tetapi paragraf 70 menyatakan tambahan bila waktu cukup | B0–B4 pada `src/train_baseline.py:262-276`; `results/metrics.csv`; sepuluh checkpoint | Hasil tersedia untuk SVM/RF/XGB; KNN/MLP tanpa hasil; validitas speaker-independent belum terpenuhi |
| Rumusan 2: karakteristik residual/modulasi | Lima residual, pita modulasi, uji statistik/effect size | `src/residual_features.py:104-170`; `src/modulation_features.py:68-145`; `results/statistical_tests.csv` 22 fitur, 19 signifikan; G3/G4 | Implementasi dan hasil ada; ukuran efek kecil, uji memakai segmen yang saling terkait; G4 band power, bukan spectrogram waktu–frekuensi |
| Rumusan 3: konsistensi | Skor/label pada audio sama; internal, lintas speaker, lintas dataset | `results/utterance_scores.csv`, `evidence_consistency.csv`, `error_analysis.csv`; B2/E4c pada test internal | Perbandingan internal tersedia; klaim lintas speaker/dataset belum memadai; threshold konsistensi 0,5 berbeda dari threshold validation |
| Tujuan dua jalur | Baseline klasifikasi terpisah dari bukti forensik | B0–B4 vs E4a–E4e dalam `train_baseline.py`; statistik dan consistency | Prinsip dua jalur terimplementasi; model evidence-only tambahan tersedia; tidak ada fusi MFCC/LFCC dengan residual/modulasi dalam daftar eksperimen aktual |
| Dataset utama | DEEP-VOICE pada panduan tabel 8; ASVspoof 2021 DF eksternal | Manifest final `dataset=CUSTOM_DATASET`, sumber lokal/UserLibri/RAVDESS/folder generator; tidak ada hasil ASVspoof | Berbeda dari rencana; asal tiap segmen tidak direkam cukup rinci untuk menyatakan komposisi DEEP-VOICE |
| Unit analisis | Utterance; segmen 1–3 detik untuk ekstraksi lokal dan agregasi skor | Baris internal berupa WAV 2 detik, `n_segments=1`; `aggregate_scores.py` tidak menghasilkan output utama | Metrik internal sebenarnya level segmen; kata `utterance` di output merujuk ID potongan |
| Pembagian data | Speaker/utterance split **sebelum** segmentasi; semua turunan satu sumber satu split | `prepare_dataset.py:181-215` membagi setelah segmentasi; 4.576 speaker_id lintas split | Penyimpangan metodologis jelas, bukan sekadar dokumentasi; perlu dijelaskan sebagai keterbatasan ketika mengutip angka |
| Duplikasi/ketertelusuran | Audit hash dan sumber | `source_manifest.csv` berisi `sha256=N/A`; `check_leakage.py:41-61` hanya memeriksa `utterance_id` | Bukti pencegahan duplikasi/speaker leakage tidak memadai |
| Validitas label sumber | Real/fake sesuai sumber dan metadata | `prepare_dataset.py:67-87` memberi seluruh `scratch` label fake; 8.439 path scratch mempunyai pasangan bernama sama dalam sumber real; 34 real validasi asal juga terbaca fake | Risiko salah label lintas kelas terdokumentasi, perlu pembatasan interpretasi angka |
| Audio | Mono, resample 16 kHz, normalisasi per utterance; panduan hop awal 1 detik | `prepare_dataset.py` dan `audio_io.py` resample 16 kHz; normalisasi peak saat ekstraksi; hop final 2 detik | Dilaksanakan dengan hop tanpa overlap; beda parameter dapat dilaporkan |
| Threshold | Pilih pada validation, jangan atur ulang pada test/eksternal | Internal `train_baseline.py:169-184` memakai threshold validation; eksternal `evaluate_validation_folder.py:31-47` memakai angka manual lain | Internal sesuai; asal kalibrasi eksternal tidak terdokumentasi |
| Reproduksibilitas | ≥3 seed, versi library, hash, command/timestamp | `configs/baseline.yaml` seed 42 saja; checkpoint/metrics seed 42; tidak ada lockfile/log final yang ditemukan | Satu seed dan metadata parsial |
| Ablasi LPC | Orde 12/16/20 | Fungsi dan CLI tersedia, artefak hanya p16 | Implementasi siap, hasil ablation tidak ditemukan |
| Visualisasi | G1–G7 termasuk waveform, distribusi, spektrum, ROC, scatter, error | Ketujuh PNG tersedia | Ada; G2 punya fallback sintetis, G1/G5/G6 salah label model; provenance perlu cek |
| Uji eksternal | Lintas dataset/speaker bebas training | CSV validasi 272 file dari 17 speaker/4 generator | Evaluasi dilakukan, tetapi sumber yang sama sudah masuk rekap/training; tidak membuktikan blind atau cross-dataset ASVspoof |

## Catatan interpretasi rumusan masalah

**RM1:** Bukti numerik untuk sepuluh model tersedia. Namun, performa generalisasi ke speaker tak dikenal belum dapat disimpulkan dari test internal karena split per potongan. **RM2:** Ekstraksi residual dan modulasi serta perbandingan distribusi tersedia; 19/22 uji signifikan tetapi semua effect size berkategori negligible menurut ambang kode, dan sinyal residual tidak membuktikan sebab biologis tertentu. **RM3:** Ada perbandingan skor/label B2–E4c pada potongan sama dan error case yang tersimpan. Kecukupannya untuk klaim konsistensi lintas speaker/generator/dataset dan penjelasan kesalahan berdasarkan fitur individu masih terbatas.

## Batasan masalah dan tujuan

Panduan tabel 3 menyatakan tidak wajib deep learning/SSL, fusion tiga domain, likelihood ratio hukum, atau dashboard. Repository menyediakan demo web tetapi itu tambahan. Tujuan minimum (`panduan`, paragraf 34–39) mencakup pipeline baseline, residual proxy Wiener–Hopf, modulasi, statistik, dan konsistensi: setiap komponen mempunyai kode/artefak. Kepatuhan ilmiah keseluruhan tetap harus mempertimbangkan protokol dataset dan validasi. Perbedaan di atas dicatat sebagai fakta diskusi, tanpa mengubah proposal atau keputusan penelitian.
