# Verifikasi, batas inferensi, dan pertanyaan terbuka

## Empat kategori status

### 1. Kode dan artefak hasil tersedia

- Segmen internal 55.576 dan split 38.903/8.336/8.337 (`manifests/split_manifest_2s.csv`, `results/features_*.csv`).
- B0–B4 dan E4a–E4e, seed 42, metrik validation/test, skor, checkpoint (`src/train_baseline.py`, `results/metrics.csv`, `results/utterance_scores.csv`, `checkpoints/`).
- Residual LPC p16, modulasi tujuh fitur, statistik MWU/FDR/CI (`src/residual_features.py`, `src/modulation_features.py`, `results/statistical_tests.csv`).
- Konsistensi B2/E4c dan error case internal, bootstrap 45 pasang AUC (`results/evidence_consistency.csv`, `error_analysis.csv`, `bootstrap_comparisons.csv`).
- Validasi file 17 speaker/empat generator/272 file dengan 10 model (`hasil_validasi/validation_external_*.csv`).
- G1–G7 PNG tersedia (`skripsi_residual_modulasi/figures/`).

### 2. Implementasi tersedia, hasil eksekusi tidak ditemukan

- GroupShuffleSplit dan hash melalui `src/make_splits.py`/`build_manifest.py`; manifest final tidak menunjukkan penggunaannya.
- Ablasi orde LPC 12/20 (`src/residual_features.py:188-201`, opsi CLI), tanpa fitur/metrik/checkpoint orde tersebut.
- KNN/MLP ada di `make_pipeline` tetapi tidak dalam daftar eksperimen training, tanpa checkpoint/metrik B5.
- `aggregate_scores.py` ada, tetapi `segment_scores.csv` dan skor agregasi yang dihasilkan tidak ditemukan.
- Helper ASVspoof ada, tanpa manifest prediksi/metrik ASVspoof.

### 3. Disebut pada panduan/laporan, tanpa implementasi atau artefak yang cocok

- Evaluasi GroupKFold, speaker-independent final, tiga seed, dan cross-dataset ASVspoof sebagaimana tercantum di panduan paragraf 53/115 dan tabel 27/30; artefak final tidak ditemukan.
- Klaim label B0 residual, B1 modulasi, B3 MFCC-only, B4 chroma/spectral, E4a gabungan akustik+residual+modulasi dalam `penyelesaian_skripsi/laporan_penyelesaian_skripsi_bab4.md` serta ringkasan; bertentangan dengan `src/train_baseline.py:262-276` dan prefiks kolom fitur.
- Klaim 22/22 fitur signifikan pada catatan historis `hasil.md`; hasil final `statistical_tests.csv` menunjukkan 19/22.
- Klaim gambar G4 modulation spectrogram 2D; `generate_all_figures.py:195-221` membuat grafik batang empat pita.
- Nama model dalam demo `web_cek/webnya/app.py:69-143` juga mengulang atribusi fitur B0/E4a yang berbeda dari `train_baseline.py:262-276`.
- Klaim sekitar 80% akurasi menyeluruh pada eksperimen 17 speaker/empat generator; CSV 272-file tertinggi 67,647% B4. Nilai 80% lebih masuk akal sebagai hasil sebagian speaker/generator atau laporan tahap lama, tetapi tidak boleh ditegaskan tanpa artefak yang spesifik.

### 4. Tidak dapat diverifikasi dari file yang ada

- Proposal/praproposal resmi Bab 1–3 dan persetujuan dosen; yang tersedia adalah panduan pelaksanaan DOCX.
- Asal, lisensi, tanggal akses, dan generator tepat untuk **setiap** segmen internal; manifest hanya `CUSTOM_DATASET` dan tidak menyimpan generator/source file.
- Laju sampel/durasi audio asli dalam manifest akhir; hanya parameter keluaran 16 kHz/2 detik jelas.
- Riwayat penciptaan voice clone empat model, versi model, prompt, reference voice, dan kontrol proses synthesis; yang terlihat hanya file/folder keluaran.
- Cara angka ambang eksternal manual dipilih dan apakah set eksternal pernah dipakai tuning; konstanta ada, log penentuan tidak ada.
- Provenance pasti G2: path real hardcoded saat audit tidak ada, dan fungsi mempunyai fallback gelombang sintetis. Keberadaan PNG tidak membuktikan gambar berasal dari pasangan audio nyata.
- Isi metadata internal `.joblib` secara langsung: audit tidak melakukan deserialisasi; struktur dictionary disimpulkan dari kode pembuat checkpoint dan keberadaan 10 file.
- Akurasi ~80% yang disebut pemilik: tidak ada CSV evaluasi final yang menunjukkannya sebagai angka total; laporan historis menyebut tahap 170-file tanpa artefak prediksi tersendiri.

## Keterbatasan metodologis yang teramati

1. **Leakage internal.** Split pada level potongan setelah segmentasi menyebabkan 4.576 `speaker_id` melintasi split (`prepare_dataset.py:181-215`; audit `split_manifest_2s.csv`). Pemeriksa leakage hanya melihat `utterance_id`, sehingga klaim “bebas leakage” pada narasi tidak didukung (`check_leakage.py:41-61`).
2. **Duplikasi/salah label sumber.** Semua 8.439 path `scratch` mempunyai pasangan relatif sama di sumber real UserLibri/RAVDESS tetapi diberi label fake; sampel pasangan identik secara SHA-256, sedangkan verifikasi byte seluruhnya belum dilakukan. Sebanyak 11.152 potongan fake terpilih berasal dari scratch, 7.815 di train. Sumber: `dataset_recap_raw.csv`, `split_manifest_2s.csv`, `prepare_dataset.py:67-87`.
3. **Kontaminasi evaluasi eksternal.** Rekap sumber memuat 170 file dari folder validasi; 163 sumber menghasilkan 460 potongan terpilih (321 train). Sebagian data uji berasal dari sumber yang telah dipakai dalam training. Label 34 real di `Data_real` salah terbaca fake oleh aturan path; 33 sumber tersebut terpilih dan menghasilkan 117 segmen internal. Sumber: `dataset_recap_raw.csv`, `split_manifest_2s.csv`, `prepare_dataset.py:67-87,129-139`.
4. **Unit statistik.** Baris yang diuji adalah segmen 2 detik dari rekaman yang sama/penutur yang sama, bukan observasi independen. P-value sangat kecil dan CI bootstrap per baris dapat terlalu optimistis untuk inferensi speaker/source yang baru (`statistical_tests.py:77-176`, `bootstrap_difference.py:35-106`).
5. **Perbedaan ambang.** Metrik internal memakai threshold validation, analisis konsistensi memakai 0,5, validasi eksternal memakai konstanta per model yang lain (`train_baseline.py:169-184`, `evidence_consistency.py:46-88`, `evaluate_validation_folder.py:31-47`).
6. **Satuan eksternal campuran.** Real dipotong menjadi file 2 detik, fake file lebih panjang dan fitur rata-rata 3–7 segmen. Angka per file tidak setara dengan akurasi per segmen atau per speaker (`prepare_balanced_validation_real.py:25-104`, `validation_external_predictions.csv`).

## Pertanyaan faktual untuk diskusi lanjutan

- Apakah tersedia proposal resmi dan dokumen persetujuan perubahan dataset/split? Panduan yang tersedia tidak mengesahkan perbedaan itu.
- Apakah ada arsip log atau hasil terpisah untuk percobaan 170-file dan klaim ~80%, tiga seed, LPC p12/p20, atau ASVspoof?
- Kapan ambang eksternal dikalibrasi, menggunakan data apa, dan apakah 272 file ikut proses pemilihan?
- Dapatkah asal audio internal dipetakan ke rekaman unik, speaker sebenarnya, dan generator? Metadata saat ini tidak cukup untuk menyimpulkannya.

Tidak ada pekerjaan komputasi yang **secara otomatis wajib** dilakukan oleh audit ini. Jika tujuan penulisan adalah membatasi klaim sesuai artefak yang ada, pekerjaan terdekat adalah memperbaiki atribusi label/angka pada naskah, menjelaskan unit analisis serta kontaminasi, dan menanyakan penerimaan metodologisnya kepada dosen. Training ulang hanya menjadi keputusan penelitian setelah ruang lingkup dan protokol disepakati.
