# Hasil dan evaluasi yang didukung artefak

## Internal: 8.337 potongan test

Tabel lengkap 10 model beserta precision/recall/F1 macro ada di `04_MODELS_AND_EXPERIMENTS.md`; sumber primer `skripsi_residual_modulasi/results/metrics.csv`. E4a mencatat AUC 0,79619, EER 0,28667, accuracy 0,71357; B4 mencatat AUC 0,78927, EER 0,33753, accuracy 0,65839. `results/bootstrap_comparisons.csv` mencatat selisih AUC **B3−E4a = −0,10667** (CI 95% −0,11659 s.d. −0,09737) tetapi **B4−E4a = −0,00692** (CI −0,01594 s.d. 0,00138), sehingga beda AUC B4/E4a tidak signifikan menurut aturan file. Semua ini bersyarat pada split segmen yang bertumpang tindih dan risiko 11.152 potongan fake dari salinan sumber real `scratch`; lihat `03_DATASET_AND_PIPELINE.md`. `results/statistical_tests.csv`: 19/22 fitur FDR <0,05, effect size seluruhnya kategori negligible menurut kode. `results/evidence_consistency.csv`: B2/E4c rho 0,67114, kappa 0,56480 pada threshold 0,5; lihat `05_FORENSIC_ANALYSIS.md`.

## Eksternal: 272 file dan 10 checkpoint

Sumber: `hasil_validasi/validation_external_predictions.csv` dan `validation_external_metrics.csv` (salinan ada di `skripsi_residual_modulasi/results/`). Script `src/evaluate_validation_folder.py:31-47,110-239` menerapkan ambang `CALIBRATED_THRESHOLDS` yang hardcoded (0,50–0,65), berbeda dari threshold validation checkpoint; riwayat pemilihan ambang ini tidak tersedia. AUC/EER dihitung pada set eksternal, akurasi pada ambang manual tersebut. Angka ini **per file input**, bukan speaker-level; file real telah dipotong 2 detik sedangkan fake diwakili satu file yang bisa memuat 3–7 segmen fitur.

| Model | AUC | EER | Akurasi | Recall real | Recall fake | TN/FP/FN/TP |
|---|---:|---:|---:|---:|---:|---|
| B0 | 0,74173 | 0,43382 | 0,63235 | 0,41912 | 0,84559 | 57/79/21/115 |
| B1 | 0,76071 | 0,40074 | 0,63971 | 0,30882 | 0,97059 | 42/94/4/132 |
| B2 | 0,77200 | 0,41544 | 0,65074 | 0,37500 | 0,92647 | 51/85/10/126 |
| B3 | 0,51671 | 0,49265 | 0,57721 | 0,32353 | 0,83088 | 44/92/23/113 |
| B4 | 0,70496 | 0,33456 | **0,67647** | 0,60294 | 0,75000 | 82/54/34/102 |
| E4a | 0,67712 | 0,37132 | 0,62500 | 0,41176 | 0,83824 | 56/80/22/114 |
| E4b | 0,52276 | 0,49265 | 0,45221 | 0,72059 | 0,18382 | 98/38/111/25 |
| E4c | 0,63606 | 0,40441 | 0,62132 | 0,49265 | 0,75000 | 67/69/34/102 |
| E4d | 0,54709 | 0,50735 | 0,57353 | 0,36765 | 0,77941 | 50/86/30/106 |
| E4e | 0,66923 | 0,36029 | 0,63971 | 0,52206 | 0,75735 | 71/65/33/103 |

Confusion counts dibaca ulang dari kolom `label` dan `pred_cal_{ID}` pada CSV prediksi; positif = fake. Ini menjelaskan false positive/negative tanpa mengarang confusion matrix yang tidak disimpan sebagai gambar. Precision/F1 fake tersedia langsung di `validation_external_metrics.csv`; misalnya B4 F1 fake 0,69863, B2 0,72622.

## Empat generator dan dua kelompok real

Hitungan benar/jumlah untuk tiga model pembanding dari CSV prediksi (urutan B2/B4/E4a):

| Kategori | Ground truth | n | B2 benar | B4 benar | E4a benar |
|---|---|---:|---:|---:|---:|
| E2TTS_Base | Fake | 34 | 34 | 27 | 30 |
| F5TTS_Base | Fake | 34 | 31 | 25 | 28 |
| Open_voice | Fake | 34 | 31 | 27 | 31 |
| VoxCPM | Fake | 34 | 30 | 23 | 25 |
| Laki_laki | Real | 72 | 17 | 35 | 33 |
| perempuan | Real | 64 | 34 | 47 | 23 |

Contoh: B2 mengenali 34/34 E2TTS sebagai fake, tetapi salah menyebut 85/136 real sebagai fake. Klaim deteksi generator perlu selalu dipasangkan dengan false positive real. `validation_external_category_breakdown.csv` hanya memberi breakdown E4a; tabel di atas dihitung dari prediksi per file.

## Tujuh belas speaker

Alias direktori tidak ditampilkan di tabel ini; S01–S17 diurutkan alfabetis menurut alias direktori, dan pemetaan dapat dilacak di `penyelesaian_skripsi/tables/Tabel_Bedah_17_Speaker.csv` serta `rel_path` dalam CSV prediksi. Tiap speaker mempunyai 8 real + 8 fake (16 file). Benar/salah B4 di bawah dihitung dari `correct_cal_B4`; jumlah benar E4a juga disajikan.

| ID | B4 benar/salah | E4a benar/salah | ID | B4 benar/salah | E4a benar/salah |
|---|---:|---:|---|---:|---:|
| S01 | 10/6 | 6/10 | S10 | 13/3 | 10/6 |
| S02 | 14/2 | 8/8 | S11 | 13/3 | 12/4 |
| S03 | 7/9 | 10/6 | S12 | 11/5 | 12/4 |
| S04 | 10/6 | 13/3 | S13 | 12/4 | 12/4 |
| S05 | 12/4 | 9/7 | S14 | 7/9 | 9/7 |
| S06 | 14/2 | 11/5 | S15 | 10/6 | 10/6 |
| S07 | 7/9 | 9/7 | S16 | 12/4 | 9/7 |
| S08 | 8/8 | 10/6 | S17 | 14/2 | 10/6 |
| S09 | 10/6 | 10/6 | | | |

Pada beberapa speaker, 13/16 atau 14/16 = 81,25% atau 87,5%. Itulah **akurasi per speaker**, tidak sama dengan accuracy keseluruhan 272 file. Tidak ada angka accuracy keseluruhan ~80% dalam `validation_external_metrics.csv`. Dokumen lama menyebut tahap 170 file (136 fake + 34 real) dengan komposisi 20:80 dan “sekitar 80%”, tetapi artefak prediksi 170-file tidak ditemukan. Sumber historis: `LAPORAN_LENGKAP_PROGRESS_DAN_MANUVER_SKRIPSI.md:96-120`.

## Interpretasi dan kasus kesalahan

Prediksi per file memungkinkan identifikasi semua 54 false positive dan 34 false negative B4, atau 80 false positive dan 22 false negative E4a, melalui filter `label` dan `pred_cal_{ID}`. `results/error_analysis.csv` memuat 3.453 kasus internal yang tidak “bersama benar” untuk B2/E4c: 573 hanya baseline benar, 1.216 hanya evidence benar, 1.664 keduanya salah. Analisis per generator pada **fitur forensik** dan penjelasan nilai fitur untuk setiap kasus error belum tersedia dalam output tersebut.

Validasi 272 file tidak dapat disebut blind/cross-speaker dengan bukti saat ini: 170 file asal set validasi sudah hadir dalam rekap sumber internal, 163 di antaranya menghasilkan 460 potongan terpilih (321 train); 34 file real asal terbaca fake pada pemindaian lama. Lihat `03_DATASET_AND_PIPELINE.md`. Tidak ada hasil ASVspoof atau cross-dataset terverifikasi.
