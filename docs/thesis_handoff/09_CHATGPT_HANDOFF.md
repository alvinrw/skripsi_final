# Handoff penelitian skripsi — baca dokumen ini terlebih dahulu

Dokumen ini dirancang untuk diunggah langsung ke ChatGPT lain. Ia merangkum **apa yang benar-benar ada** pada repository `fase_1/` per 18 Oktober 2026. Jangan mengubah desain eksperimen atau menyimpulkan bahwa training harus diulang tanpa keputusan peneliti/dosen. Ketika menjawab pertanyaan lanjutan, bedakan kode, artefak angka, rencana tertulis, dan informasi lisan pemilik.

## 1. Pertanyaan penelitian dan ruang lingkup

Judul: *Analisis Forensik Bukti melalui Residual dan Modulasi pada Deteksi Speech Deepfake Berbasis Produksi Sinyal Wicara*. Fokusnya: (1) mendeteksi real/fake dengan MFCC/LFCC dan ML; (2) menelaah karakteristik residual prediksi linear dan modulasi; (3) membandingkan hasil klasifikasi dengan bukti forensik pada audio yang sama. Dua jalur konseptualnya adalah **MFCC/LFCC → classifier** dan **residual/modulasi → analisis bukti**. Perbandingan tidak mensyaratkan fitur digabung dalam satu model. Rancangan ini didukung `Panduan_Skripsi_Alvin_Residual_Modulasi_Speech_Deepfake.docx` paragraf 20, 27–39, 70, 77–108. Berkas proposal/praproposal formal tidak ditemukan.

## 2. Fakta terverifikasi dari kode dan artefak

### Pipeline data

`skripsi_residual_modulasi/src/prepare_dataset.py:37-225` memindai audio workspace, memberi label berdasar path, resample/mono 16 kHz, memotong WAV 2 detik tanpa overlap, menyeimbangkan real/fake, mengacak, lalu membagi **segmen** secara terstratifikasi 70/15/15 dengan seed 42. Hasil `manifests/split_manifest_2s.csv` berisi 55.576 baris: 27.788 real/27.788 fake, train 38.903, validation 8.336, test 8.337. `results/features_*.csv` cocok jumlahnya, semuanya `n_segments=1`. `src/audio_io.py:19-108` melakukan peak normalization ketika fitur diekstraksi. Metrik internal karena itu **segment-level** walau nama kolom/skrip memakai kata `utterance`.

Sumber audio internal yang terjangkau pemindaian ada di `Folder_dataset/`, `skripsi_residual_modulasi/scratch/`, dan `Suara_untuk_validasi/`; `results/dataset_recap_raw.csv` mencatat 17.908 file path sebelum pemotongan. **Sebanyak 8.439 path `scratch` (5.559 UserLibri FLAC + 2.880 RAVDESS WAV) mempunyai pasangan nama relatif sama dalam sumber real tetapi diberi label fake oleh pemindai.** Sampel tiga pasangan per korpus memiliki hash identik; semua pasangan belum di-hash. Sebanyak 6.136 sumber scratch menghasilkan 11.152 potongan fake terpilih, 7.815 di train. Ini risiko salah label/duplikasi lintas kelas yang sangat penting saat menafsirkan angka. Manifest final menyebut semua `CUSTOM_DATASET`, `generator_id` tidak tersedia, `sha256=N/A`, sehingga asal dan jumlah unik per speaker/generator internal tidak dapat dinyatakan pasti. `Folder_dataset/Training/` mempunyai folder E5TTS, F5TTS, Openvoice, Voxcpm; ini berbeda dari empat kategori set eksternal.

**Batas penting:** `prepare_dataset.py:181-215` membagi sesudah pemotongan pada level segmen. Audit manifest menemukan 4.576 `speaker_id` melintasi train/validation/test. `src/check_leakage.py:41-61` pada implementasi sekarang hanya mengecek `utterance_id`. Rute GroupShuffleSplit ada di `src/make_splits.py`, tetapi manifest final berasal dari jalur segmen (`source_manifest.csv` mempunyai `sha256=N/A`). Jadi jangan menyebut test internal speaker-independent atau bebas leakage.

### Fitur yang benar-benar dihitung

- **MFCC:** `librosa.feature.mfcc`, 20 koefisien, FFT 512, window 400 sampel (25 ms), hop 160 (10 ms); delta dan delta-delta; mean, std, Q25, Q75 untuk masing-masing → 240 angka (`src/spectral_features.py:21-78`, `configs/baseline.yaml`).
- **LFCC:** `scipy.signal.stft` (400/240 overlap/FFT512), 40 filter segitiga linear 0–8 kHz, log dan DCT-II, ambil 20 koefisien, mean+std → 40 angka (`src/lfcc.py:29-134`).
- **Residual:** frame 25 ms/hop 10 ms, jendela Hamming, skip energi <1e-8, `librosa.lpc(order=16)` lalu `lfilter(a,[1],x)`. Ini residual prediksi LPC/autokorelasi, proxy Wiener–Hopf; **bukan sumber glotal murni**. Lima fitur frame: energy, entropy histogram, rasio prediction error, irregularity selisih residual, kurtosis; mean/std/median → 15 angka (`src/residual_features.py:36-184`).
- **Modulasi:** envelope Hilbert → low-pass 40 Hz → resample 100 Hz → de-mean → daya FFT 0–20 Hz. Empat energi relatif band 0,5–2/2–4/4–8/8–20 Hz + centroid, entropy, depth → tujuh angka (`src/modulation_features.py:39-151`). Implementasi ini spektrum envelope per segmen, **bukan matriks spectrogram waktu–frekuensi**.
- `src/extract_features.py:56-187` menggabungkan empat domain pada tiap baris. Sepuluh model pada file `src/train_baseline.py:262-276` memakai grup terpisah. Tidak ada model aktual yang menggabungkan MFCC/LFCC dengan residual/modulasi.

### Eksperimen yang selesai menurut artefak

Semua sepuluh ID berikut memiliki dua baris metrik (validation/test), skor, dan checkpoint `checkpoints/{ID}_seed42.joblib`. Imputer median, StandardScaler, dan classifier difit di train; threshold metrik internal dipilih pada validation (`src/train_baseline.py:80-231`). SVM RBF C=10, RF 200 pohon, XGB 200 estimator/depth 6/learning rate 0,05; seed 42 (`configs/baseline.yaml`). Angka di bawah dari **test internal 8.337 segmen**, `results/metrics.csv`.

| ID | Fitur → model | AUC | EER | Accuracy |
|---|---|---:|---:|---:|
| B0 | MFCC → SVM | 0,72489 | 0,37256 | 0,62996 |
| B1 | LFCC → SVM | 0,76001 | 0,36380 | 0,63536 |
| B2 | MFCC+LFCC → SVM | 0,72847 | 0,37579 | 0,62732 |
| B3 | MFCC+LFCC → RF | 0,68951 | 0,37412 | 0,62780 |
| B4 | MFCC+LFCC → XGB | 0,78927 | 0,33753 | 0,65839 |
| E4a | Residual → SVM | **0,79619** | **0,28667** | **0,71357** |
| E4b | Modulasi → SVM | 0,60409 | 0,42305 | 0,57659 |
| E4c | Residual+modulasi → SVM | 0,78961 | 0,29759 | 0,70289 |
| E4d | Residual+modulasi → RF | 0,60479 | 0,39870 | 0,60297 |
| E4e | Residual+modulasi → XGB | 0,77383 | 0,31414 | 0,68634 |

`results/metrics.csv` juga mempunyai precision/recall/F1 per kelas dan macro, threshold, n. `results/bootstrap_comparisons.csv`: E4a unggul AUC 0,10667 atas B3 (CI selisih B3−E4a −0,11659 s.d. −0,09737), tetapi selisih E4a vs B4 tidak signifikan menurut CI yang melintasi nol. Jangan menyebut E4a “gabungan akustik+forensik”: label itu pada beberapa laporan/gambar **salah menurut kode**. `B5` KNN/MLP, LPC p12/p20, tiga seed, dan hasil ASVspoof tidak ditemukan walaupun rencana/kode bantu ada.

### Bukti forensik dan konsistensi

`results/statistical_tests.csv` membandingkan 22 fitur bukti pada train: **19/22** signifikan setelah Benjamini–Hochberg FDR. Semua `effect_size_label` adalah **negligible** menurut aturan `src/statistical_tests.py:164-176` (|rank-biserial| maksimum 0,250114). `res_entropy_mean_p16` mean real 4,405121 vs fake 4,318604; `mod_band_0.5_2` real 0,385113 vs fake 0,357046; `mod_band_4_8` real 0,237439 vs fake 0,254954. Band 2–4 dan 8–20 Hz tidak signifikan setelah FDR. Ini bukti perbedaan distribusi pada dataset/segmen itu, bukan bukti langsung mekanisme pita suara atau oversmoothing semua pita.

`results/evidence_consistency.csv` membandingkan **B2 MFCC+LFCC** dengan **E4c residual+modulasi** pada 8.337 segmen test: Spearman rho 0,67114, Cohen kappa 0,56480; keduanya benar 4.884, B2 saja benar 573, E4c saja benar 1.216, keduanya salah 1.664. `results/error_analysis.csv` berisi 3.453 kasus selain keduanya benar. **Threshold analisis ini 0,5** (`src/evidence_consistency.py:46-88`), sementara threshold validation dalam metrik B2 0,43459 dan E4c 0,40951. Belum ada tabel yang menautkan nilai fitur forensik individu pada kasus salah yang sama; adanya model bukti dan empat kategori tidak membuktikan penyebab kesalahan.

### Evaluasi 17 speaker dan empat generator

`hasil_validasi/validation_external_predictions.csv` adalah artefak primer: **272 file**, 136 real dari 17 speaker (masing-masing 8 real), 136 fake dari E2TTS_Base/F5TTS_Base/Open_voice/VoxCPM (34 tiap generator; masing-masing speaker dua file per generator). `src/prepare_balanced_validation_real.py:25-104` membuat real dari 34 rekaman asal menjadi empat file 2 detik; file fake tidak dipotong di folder, dan ekstraksinya merata-ratakan fitur 3–7 segmen (`n_segments` CSV). Unit metrik adalah **file input**. `src/evaluate_validation_folder.py:31-47` memakai ambang manual per model yang berbeda dari threshold validation.

`hasil_validasi/validation_external_metrics.csv`: accuracy tertinggi **B4 0,67647** (184/272 benar; 82 TN, 54 FP, 34 FN, 102 TP); AUC tertinggi **B2 0,77200** (accuracy 0,65074); E4a accuracy 0,62500, AUC 0,67712. Untuk E4a, deteksi fake per generator: 30/34 E2TTS, 28/34 F5TTS, 31/34 Open_voice, 25/34 VoxCPM; tetapi real yang benar hanya 56/136. Tabel lengkap semua model, confusion counts, generator, dan speaker anonim S01–S17 ada di `06_RESULTS_AND_EVALUATION.md`. Sebagian speaker mempunyai akurasi 13/16 atau 14/16 (>80%), **bukan** accuracy agregat. Klaim pemilik “akurasi tertinggi sekitar 80%” tidak dapat dipetakan ke satu hasil keseluruhan dari CSV 272-file; laporan historis menyebut tahap 170-file, tetapi CSV prediksinya tidak tersedia.

**Validasi ini bukan blind test terverifikasi.** Rekap `results/dataset_recap_raw.csv` sebelum training mencakup 170 file asal dari `Suara_untuk_validasi`; pencocokan ID hash path dari `prepare_dataset.py:129-139` menemukan 163 file terpilih menjadi 460 potongan internal (321 train, 72 validation, 67 test). Dari 34 real asal, 33 terpilih menjadi 117 potongan berlabel **fake** karena `Data_real` tidak cocok dengan aturan label real `prepare_dataset.py:67-87`. Sebagian speaker/audio terkait dengan training; keterpisahan eksternal tidak didukung. Ini temuan audit dataset, bukan perintah training ulang.

## 3. Rencana tertulis yang berbeda dari realisasi

Panduan DOCX menyebut DEEP-VOICE sebagai dataset utama, ASVspoof 2021 DF sebagai cross-dataset, split speaker/utterance sebelum segmentasi, hop awal 1 detik, minimal tiga seed, ablasi LPC 12/16/20, serta evaluasi speaker-independent/GroupKFold. Artefak final memakai `CUSTOM_DATASET`, hop 2 detik, satu seed 42, orde LPC 16, split potongan, dan tidak ada hasil ASVspoof. Panduan menyebut evidence-only model sebagai target operasional dalam paragraf 103–108; implementasi E4a–E4e memang ada. Perbedaan rancangan dengan hasil perlu disampaikan apa adanya ke dosen. Matriks rinci: `07_PROPOSAL_COMPLIANCE.md`.

## 4. Informasi yang hanya berasal dari pemilik/narasi

Pemilik menyatakan 17 sumber suara, empat generator cloning, segmen sekitar 2 detik, training berbagai model, dan angka akurasi sekitar 80%. Empat hal pertama **terkonfirmasi untuk skenario validasi 272 file atau pipeline internal sebagaimana dijelaskan**, tetapi angka 80% belum terkonfirmasi sebagai akurasi total evaluasi final. Laporan `ringkasan_hasil_skripsi/RINGKASAN_EKSEKUTIF_HASIL_SKRIPSI.md` dan `penyelesaian_skripsi/laporan_penyelesaian_skripsi_bab4.md` memuat sejumlah nama fitur per ID model yang bertentangan dengan `train_baseline.py`; gunakan angka CSV serta daftar model dari kode. `skripsi_residual_modulasi/hasil.md` merekam percobaan 2026 yang lebih awal dan bukan tabel final seed 42.

## 5. Hal yang belum dapat diverifikasi dan aturan menjawab

- Proposal formal, persetujuan dosen, lisensi/riwayat dataset, versi generator, dan prosedur cloning tidak ada dalam workspace yang diaudit.
- Tidak ditemukan log/CSV final untuk tiga seed, LPC p12/p20, ASVspoof, GroupKFold, atau hasil 170-file yang dapat menjelaskan klaim sekitar 80%.
- `figures/G2_waveform_and_residual_comparison.png` punya risiko provenance: `generate_all_figures.py:109-160` beralih ke sinyal sintetis bila path gagal; path real hardcoded tidak ada saat audit. G4 berupa grafik energi band; G1/G5/G6 punya beberapa caption model yang salah.
- Demo `web_cek/webnya/app.py:69-143` juga memakai nama model yang berbeda dari definisi fitur pada kode training; gunakan `train_baseline.py:262-276` untuk menafsirkan ID.
- Isi langsung file `.joblib` tidak dideserialisasi; struktur yang diharapkan berasal dari `train_baseline.py:207-231`.
- Hindari klaim bahwa penelitian telah sepenuhnya memenuhi ketiga rumusan pada tingkat generalisasi. Yang pasti: ada hasil RM1, fitur/statistik RM2, dan perbandingan internal RM3; kekuatan inferensinya dibatasi oleh split, salah label, dan kontaminasi eksternal.

Ketika membantu menulis skripsi atau menjawab sidang, pakai frasa seperti “pada split segmen internal yang tersedia” dan “pada evaluasi 272 file yang tercatat”, cantumkan keterbatasan metodologis, dan jangan mengubah angka/label eksperimen agar cocok dengan narasi lama. Lihat `01_THESIS_OVERVIEW.md` sampai `08_VERIFICATION_AND_GAPS.md` untuk penjelasan serta peta file yang lebih rinci.
