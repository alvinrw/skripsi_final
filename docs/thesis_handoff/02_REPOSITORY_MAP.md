# Peta repository dan jalur bukti

Path di bawah relatif terhadap `fase_1/`. Audio mentah, checkpoint, dan hasil tetap di tempatnya.

| Lokasi | Fungsi aktual dan bukti |
|---|---|
| `skripsi_residual_modulasi/configs/baseline.yaml` | Konfigurasi final yang tersedia: seed 42, 16 kHz, 2 detik/hop 2 detik, LPC 16, parameter fitur/model. |
| `skripsi_residual_modulasi/src/prepare_dataset.py` | Pemindai seluruh workspace, label berbasis path, potong/balance/split 2 detik; sumber manifest utama (`process_dataset`, baris 37–225). |
| `skripsi_residual_modulasi/src/build_manifest.py`, `make_splits.py`, `check_leakage.py` | Rute alternatif manifest SHA-256 dan GroupShuffleSplit; artefak manifest yang ada **bukan** keluarannya: `sha256=N/A`, `label_idx` string/kolom tambahan, split per segmen. `check_leakage` hanya memeriksa `utterance_id` (`:26-80`). |
| `skripsi_residual_modulasi/src/audio_io.py` | Baca mono, resample, normalisasi peak; segmentasi 2 detik (`load_audio:19`, `segment_audio:60`). |
| `src/spectral_features.py`, `src/lfcc.py` | MFCC dan LFCC (`mfcc_features:38`, `lfcc_features:73`). |
| `src/residual_features.py`, `src/modulation_features.py` | Ekstraksi 15 residual dan 7 fitur modulasi (`residual_feature_vector:104`, `modulation_features:68`). |
| `src/extract_features.py` | Menggabungkan empat domain fitur dan metadata per baris; multiprocessing/auto-resume (`extract_utterance_features:56`, `extract_all_features:218`). |
| `src/train_baseline.py`, `src/metrics.py` | Definisi B0–B4/E4a–E4e, fit model, threshold validation, metrik, skor, checkpoint (`train_all:235`, `compute_metrics:60`). |
| `src/statistical_tests.py`, `src/bootstrap_difference.py`, `src/evidence_consistency.py` | MWU/FDR/effect size, bootstrap perbandingan AUC, korelasi/kappa/empat kategori (`run_statistical_tests:77`, `compare_models:109`, `analyze_consistency:46`). |
| `src/evaluate_validation_folder.py`, `src/prepare_balanced_validation_real.py` | Skenario 17 speaker/four generator; potongan real, ekstraksi dan prediksi 10 model, ambang manual (`find_audio_files:50`, `main:110`). |
| `src/generate_all_figures.py` | Membuat G1–G7 dari fitur/skor, tetapi sejumlah label gambar berbeda dari definisi model dalam kode; G2 punya fallback sinyal buatan (`generate_g2:109-160`). |
| `src/run_pipeline.py` | Orkestrator beberapa rute; `step_prepare` memanggil `prepare_dataset.py` dengan argumen yang tidak dikenali oleh parser script tersebut (`:137-146`), sehingga jangan mengasumsikan seluruh artefak dibuat lewat satu perintah master. |
| `skripsi_residual_modulasi/manifests/` | `source_manifest.csv`, `split_manifest.csv`, `split_manifest_2s.csv`; ketiganya 55.576 baris. Source manifest saat ini `sha256=N/A`. |
| `skripsi_residual_modulasi/results/` | CSV fitur, metrik, skor, statistik, bootstrap, konsistensi, analisis kesalahan dan validasi eksternal. Lihat `06_RESULTS_AND_EVALUATION.md`. |
| `skripsi_residual_modulasi/checkpoints/` | Sepuluh `.joblib` seed 42, B0–B4 dan E4a–E4e. Struktur metadata yang disimpan didefinisikan pada `train_baseline.py:207-231`; isi biner tidak dieksekusi dalam audit. |
| `skripsi_residual_modulasi/figures/` | G1–G7 PNG; salinan pada `penyelesaian_skripsi/figures/` dan `ringkasan_hasil_skripsi/figures/`. |
| `Folder_dataset/` | Sumber audio lokal, RAVDESS, UserLibri, dan folder Training generator; `results/dataset_recap_raw.csv` mencatat file yang dipindai. |
| `skripsi_residual_modulasi/scratch/` | Salinan/cache UserLibri yang ikut terjangkau pemindaian `prepare_dataset.py`; perlu dibedakan dari sumber independen. |
| `Suara_untuk_validasi/` | Audio evaluasi 17 speaker, 4 generator; `Data_real_raw_backup/` berisi rekaman asal sebelum pemotongan. |
| `hasil_validasi/` | Salinan CSV evaluasi eksternal; `outputs/hasil_validasi_profesional.xlsx` adalah presentasi angka. |
| `penyelesaian_skripsi/`, `ringkasan_hasil_skripsi/` | Narasi Bab 4, tabel/gambar turunan dan bahan sidang; label eksperimen di beberapa narasi bertentangan dengan `train_baseline.py`. |
| `web_cek/` | Demo web dan salinan sepuluh checkpoint; bukan sumber utama hasil penelitian. `webnya/app.py:69-143` memberi nama B0/E4a yang bertentangan dengan definisi training; hasil antarmuka perlu dibaca bersama daftar fitur checkpoint/kode. |
| `LAPORAN_LENGKAP_PROGRESS_DAN_MANUVER_SKRIPSI.md`, `skripsi_residual_modulasi/README.md`, `hasil.md`, `task_todo.md` | Narasi/progres historis; gunakan dengan tanggal dan verifikasi ke CSV utama. |
| `Panduan_Skripsi_Alvin_Residual_Modulasi_Speech_Deepfake.docx` | Panduan pelaksanaan terdekat dengan rancangan proposal. Proposal formal tidak tersedia. |

`skripsi_residual_modulasi/notebooks/` kosong pada inventaris; tidak ada notebook `.ipynb`. Tidak ditemukan log command final, `requirements-lock.txt`, metadata versi lingkungan, atau protokol ASVspoof yang telah dieksekusi. File `download_data.py`, `download_real_speech.py`, dan `download_asvspoof.py` adalah helper perolehan data, bukan bukti penggunaan dataset tertentu. `build_validasi_profesional.py` dan file `.mjs` membuat/memeriksa workbook dan bukan jalur training.

## Relasi artefak

`dataset_recap_raw.csv` → `split_manifest_2s.csv` → `features_{train,validation,test}.csv` → `metrics.csv` + `utterance_scores.csv` + `checkpoints/*.joblib` → `statistical_tests.csv`, `bootstrap_comparisons.csv`, `evidence_consistency.csv`, `error_analysis.csv` → G1–G7 dan tabel Bab 4. Validasi eksternal membaca checkpoint dan audio `Suara_untuk_validasi/`, lalu menulis `validation_external_*.csv`. Relasi berasal dari panggilan file pada `prepare_dataset.py:102-225`, `extract_features.py:218-307`, `train_baseline.py:130-291`, dan `evaluate_validation_folder.py:110-276`.
