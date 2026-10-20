# Ikhtisar penelitian dan status bukti

## Cara membaca audit ini

Dokumen ini memotret repository pada 18 Oktober 2026. **Terverifikasi** berarti ada kode dan/atau artefak yang dapat dibaca; **rencana** berasal dari `Panduan_Skripsi_Alvin_Residual_Modulasi_Speech_Deepfake.docx`; **klaim naratif** berasal dari README/laporan dan harus diuji terhadap artefak primer. Angka internal di sini mengacu pada CSV dalam `skripsi_residual_modulasi/results/`. Tidak ada pelatihan atau perubahan data selama audit.

## Masalah, tujuan, dan dua jalur

Judul penelitian: *Analisis Forensik Bukti melalui Residual dan Modulasi pada Deteksi Speech Deepfake Berbasis Produksi Sinyal Wicara*. Pertanyaannya: (1) performa ML dengan MFCC/LFCC; (2) perbedaan karakteristik residual prediksi linear dan modulasi antara real/fake; (3) kesesuaian skor/keputusan deteksi dengan bukti forensik. Rumusan ini tertulis pada paragraf 20 dan 27–29 dokumen panduan. Berkas proposal/praproposal formal Bab 1–3 tidak ditemukan; panduan pelaksanaan adalah acuan tertulis yang tersedia.

Arsitektur konseptual mempunyai dua jalur. Jalur klasifikasi: audio → MFCC/LFCC → SVM/Random Forest/XGBoost → skor fake. Jalur forensik: audio yang sama → residual LPC dan spektrum modulasi → distribusi/uji statistik dan model bukti terpisah → perbandingan skor/keputusan. Model E4a–E4e memang dilatih walaupun fitur forensik tidak harus digabung dengan MFCC/LFCC untuk menjawab tiga fokus penelitian. Implementasi model tersebut merupakan eksperimen tambahan yang tersedia, bukan syarat logis dari deskripsi dua jalur pengguna. Sumber: `skripsi_residual_modulasi/src/train_baseline.py:55-77,235-291`, `src/statistical_tests.py:77-180`, `src/evidence_consistency.py:46-162`.

## Alur aktual yang menghasilkan artefak utama

`src/prepare_dataset.py:37-225` memindai audio di workspace, membuat potongan WAV 2 detik pada 16 kHz, menyeimbangkan kelas dengan sampling acak, lalu melakukan `train_test_split` terstratifikasi **per potongan** pada rasio 70/15/15, seed 42. `src/extract_features.py:56-187,218-307` mengekstraksi MFCC (240 kolom), LFCC (40), residual (15), dan modulasi (7) pada tiap baris manifest. Semua baris fitur internal mempunyai `n_segments=1`; maka unit pengujian internal yang diberi nama `utterance` pada kode adalah potongan 2 detik, bukan rekaman sumber utuh. `src/train_baseline.py:130-232` memasang imputer median, StandardScaler, model, ambang EER dari validation, lalu menyimpan CSV skor/metrik dan checkpoint.

Artefak utama: `manifests/split_manifest_2s.csv` berisi 55.576 baris (27.788 real, 27.788 fake); train 38.903, validation 8.336, test 8.337. `results/metrics.csv` mempunyai 20 baris untuk 10 model × dua split, seed 42. Pada test internal, nilai AUC tertinggi adalah E4a 0,79619; accuracy 0,71357, EER 0,28667. **Interpretasi performa harus disertai catatan data**: 4.576 `speaker_id` melintasi split. Selain itu, 8.439 audio `scratch` mempunyai pasangan path relatif sama di sumber real UserLibri/RAVDESS tetapi diberi label fake; 11.152 potongan fake terpilih berasal dari `scratch`. Sumber: manifest, `dataset_recap_raw.csv`, `results/metrics.csv`, dan `src/prepare_dataset.py:67-87,181-215`; rincian di `03_DATASET_AND_PIPELINE.md`.

## Bukti forensik dan evaluasi eksternal

Residual benar-benar dihitung dengan `librosa.lpc` pada frame Hamming 25 ms/hop 10 ms, orde 16, lalu `scipy.signal.lfilter` menghasilkan residual prediksi; ini adalah **proxy Wiener–Hopf melalui LPC/autokorelasi**, bukan rekonstruksi glotal langsung (`src/residual_features.py:57-170`). Modulasi benar-benar dihitung dari envelope Hilbert, low-pass 40 Hz, resampling 100 Hz, dan FFT daya pada frekuensi modulasi 0–20 Hz (`src/modulation_features.py:68-145`). `results/statistical_tests.csv` memuat 22 fitur, 19 signifikan pada FDR < 0,05; arah dan effect size dibahas di `05_FORENSIC_ANALYSIS.md`.

`hasil_validasi/validation_external_predictions.csv` memuat 272 file: 136 real dari 17 folder speaker dan 136 fake (34 untuk masing-masing E2TTS_Base, F5TTS_Base, Open_voice, VoxCPM). Evaluasi terjadi **per file input**. File real pada set ini berupa potongan 2 detik; file fake rata-rata meliputi beberapa segmen yang fiturnya dirata-rata. `results/validation_external_metrics.csv` mencatat accuracy terkalibrasi terbaik B4 0,67647; AUC tertinggi B2 0,77200. Tidak ditemukan artefak yang mendukung accuracy keseluruhan sekitar 80% untuk evaluasi 272 file. Sumber dan batasnya dijelaskan di `06_RESULTS_AND_EVALUATION.md`.

## Kesimpulan audit yang aman

Implementasi, training, prediksi, statistik, dan grafik **ada**. Rumusan 1 mempunyai keluaran kuantitatif; rumusan 2 mempunyai ekstraksi dan statistik; rumusan 3 mempunyai perbandingan B2/E4c dan empat kategori kasus. Namun, klaim evaluasi speaker-independent, blind external, generalisasi lintas dataset, atau kesimpulan fisik tentang pita suara belum ditopang secara kuat oleh artefak utama: split internal berbasis potongan, salinan audio real di `scratch` berlabel fake, audio validasi ikut pemindaian data, dan sejumlah real validasi juga berlabel fake. Catatan ini adalah informasi metodologis untuk pembahasan dengan dosen; audit ini tidak mengubah desain atau meminta pelatihan ulang.

Lanjutkan ke `09_CHATGPT_HANDOFF.md` untuk paket konteks yang dapat diunggah ke ChatGPT lain.
