# Model dan seluruh eksperimen yang terbukti memiliki artefak

## Definisi aktual dan pelatihan

Definisi yang berlaku adalah daftar `experiments` pada `skripsi_residual_modulasi/src/train_baseline.py:262-276`, bukan label alternatif dalam draf Bab 4 atau G5/G6. Seluruh model memakai `SimpleImputer(median) → StandardScaler → classifier` yang difit pada train saja (`:80-127,130-167`). Skor adalah `predict_proba(X)[:,1]` (semakin tinggi, semakin fake). Threshold EER dihitung pada validation saja untuk metrik test internal (`:169-184`); `metrics.csv` juga menyimpan EER/threshold optimum test sebagai metrik diagnostik, sedangkan `used_threshold` test adalah threshold validation. Seed satu-satunya pada konfigurasi/artefak final adalah 42 (`configs/baseline.yaml`, `results/metrics.csv`).

| ID | Fitur masukan | Model | Dimensi | Tujuan kode |
|---|---|---|---:|---|
| B0 | MFCC | SVM RBF | 240 | Baseline MFCC |
| B1 | LFCC | SVM RBF | 40 | Baseline frekuensi linear |
| B2 | MFCC + LFCC | SVM RBF | 280 | Fusi dua fitur spektral |
| B3 | MFCC + LFCC | Random Forest | 280 | Pembanding pohon |
| B4 | MFCC + LFCC | XGBoost | 280 | Pembanding boosting |
| E4a | Residual LPC p16 | SVM RBF | 15 | Ablasi bukti residual |
| E4b | Modulasi | SVM RBF | 7 | Ablasi bukti modulasi |
| E4c | Residual + modulasi | SVM RBF | 22 | Model bukti gabungan terpisah |
| E4d | Residual + modulasi | Random Forest | 22 | Model bukti berbasis pohon |
| E4e | Residual + modulasi | XGBoost | 22 | Model bukti boosting |

Sumber: `train_baseline.py:55-77,262-276`; jumlah kolom dari header `results/features_train.csv`. **Tidak ada model dalam daftar ini yang memakai MFCC/LFCC bersama residual/modulasi.** Kode `B5` hanya disebut pada docstring dan factory KNN/MLP; tidak ada entri training, metrik, atau checkpoint B5.

SVM memakai `C=10`, kernel RBF, `probability=True`, `class_weight=balanced`; RF 200 pohon, depth tak dibatasi, `class_weight=balanced`; XGB 200 estimator, depth 6, learning rate 0,05, `eval_metric=logloss` (`configs/baseline.yaml`, `train_baseline.py:80-127`). Seluruhnya memakai seed 42. Data: train 38.903, validation 8.336, test 8.337 potongan 2 detik yang sama untuk semua ID. Checkpoint tersedia di `skripsi_residual_modulasi/checkpoints/{ID}_seed42.joblib`, satu per model. Kode menulis dictionary `model`, `features`, `feature_group`, `model_type`, `seed`, `val_threshold`, `experiment_id` (`train_baseline.py:207-231`). Isi biner checkpoint tidak dimuat dalam audit; keberadaan, nama, dan ukuran file diverifikasi.

## Hasil test internal dari `results/metrics.csv`

Semua angka berikut pada level potongan 2 detik, bukan speaker/rekaman sumber utuh. Precision/recall/F1 yang ditampilkan adalah macro; metrik kelas tersedia pada CSV asli. Accuracy adalah pada `used_threshold` yang dipilih dari validation.

| ID | AUC | EER | Accuracy | Precision macro | Recall macro | F1 macro |
|---|---:|---:|---:|---:|---:|---:|
| B0 | 0,72489 | 0,37256 | 0,62996 | 0,62997 | 0,62996 | 0,62996 |
| B1 | 0,76001 | 0,36380 | 0,63536 | 0,63536 | 0,63536 | 0,63536 |
| B2 | 0,72847 | 0,37579 | 0,62732 | 0,62733 | 0,62732 | 0,62732 |
| B3 | 0,68951 | 0,37412 | 0,62780 | 0,62782 | 0,62780 | 0,62779 |
| B4 | 0,78927 | 0,33753 | 0,65839 | 0,65844 | 0,65839 | 0,65837 |
| E4a | 0,79619 | 0,28667 | 0,71357 | 0,71357 | 0,71357 | 0,71357 |
| E4b | 0,60409 | 0,42305 | 0,57659 | 0,57665 | 0,57659 | 0,57650 |
| E4c | 0,78961 | 0,29759 | 0,70289 | 0,70289 | 0,70289 | 0,70289 |
| E4d | 0,60479 | 0,39870 | 0,60297 | 0,60299 | 0,60297 | 0,60296 |
| E4e | 0,77383 | 0,31414 | 0,68634 | 0,68635 | 0,68634 | 0,68633 |

`results/metrics.csv` juga berisi 10 baris validation; `results/utterance_scores.csv` memuat 16.673 skor validation+test, `results/bootstrap_comparisons.csv` memuat 45 perbandingan AUC. Confusion matrix tidak disimpan sebagai file khusus. TP/FP/FN/TN dapat dihitung dari skor dan `used_threshold`; CSV `metrics.csv` menyediakan recall per kelas. Pada set eksternal, confusion matrix eksplisit hasil perhitungan dari CSV prediksi ada di `06_RESULTS_AND_EVALUATION.md`.

## Kode eksperimen lain yang muncul pada rencana

Panduan DOCX, Tabel 30 memakai E0–E7 sebagai **tahapan rencana**, berbeda dari ID model E4a–E4e. E0 smoke test dan E2 ablasi LPC 12/16/20 disebut/didukung kode helper (`residual_features_ablation`) tetapi tidak ditemukan CSV/checkpoint p12/p20 final. E3 pita modulasi hadir sebagai empat fitur, tetapi bukan studi ablasi band tersendiri. E5 speaker-independent, E6 cross-dataset ASVspoof, tiga seed, dan GroupKFold tidak memiliki artefak hasil yang ditemukan. `skripsi_residual_modulasi/hasil.md` mencatat percobaan historis 2/3/5/7 detik serta proses yang sempat dihentikan; tidak ada fitur/metrik/checkpoint final dengan suffix durasi lain pada direktori hasil saat audit. Angka historis tidak dicampur dengan tabel final seed 42.

## Status

B0–B4 dan E4a–E4e **terverifikasi selesai dalam arti ada CSV validation/test serta checkpoint seed 42**. B5, tiga seed, ablasi p12/p20, E5, dan E6 adalah rencana/kode parsial tanpa artefak yang cukup untuk menyatakan selesai. Klaim generalisasi tidak dapat dipastikan dari hasil internal karena split segmen dan tumpang tindih sumber yang dijelaskan di `03_DATASET_AND_PIPELINE.md`.
