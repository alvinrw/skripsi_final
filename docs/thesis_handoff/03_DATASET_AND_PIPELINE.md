# Dataset, preprocessing, dan pembagian data

## Dua kumpulan yang perlu dibedakan

**Internal.** `skripsi_residual_modulasi/results/dataset_recap_raw.csv` memuat 17.908 path sumber: 8.507 berlabel real dan 9.401 fake menurut aturan kode. Rekap path menunjukkan 8.507 real dari `Folder_dataset/Suara_real/`, 792 fake dari `Folder_dataset/Training/` dan `Folder_dataset/testing/`, 8.439 fake dari `skripsi_residual_modulasi/scratch/`, serta 170 dari `Suara_untuk_validasi/` yang seluruhnya diberi label fake. **Seluruh 8.439 path scratch (5.559 UserLibri FLAC dan 2.880 RAVDESS WAV) mempunyai pasangan bernama relatif sama di `Folder_dataset/Suara_real/` berlabel real.** Sampel tiga pasangan tiap korpus mempunyai ukuran dan SHA-256 identik; hash untuk semua 8.439 pasangan belum dihitung. Pencocokan nama sumber ke manifest menunjukkan 6.136 sumber `scratch` terpilih menjadi 11.152 potongan fake (7.815 train). Ini risiko duplikasi lintas kelas/salah label yang perlu dinyatakan ketika menafsirkan metrik. Sumber: `src/prepare_dataset.py:46-104`, `results/dataset_recap_raw.csv`, `manifests/split_manifest_2s.csv`.

**Eksternal yang dilaporkan.** `hasil_validasi/validation_external_predictions.csv` mempunyai 272 file: 136 real (72 laki-laki, 64 perempuan) dari 17 folder speaker dan 136 fake (34 E2TTS_Base, 34 F5TTS_Base, 34 Open_voice, 34 VoxCPM). Masing-masing speaker mempunyai 8 file real dan 8 fake; dua file fake per generator. Real 136 dibuat dari 34 rekaman asli (17 × dua bahasa) menjadi empat potongan 2 detik per rekaman oleh `src/prepare_balanced_validation_real.py:25-104`. Fake tetap pada panjang file masukan; `n_segments` pada CSV menunjukkan 136 baris bernilai 1 dan 136 lain bernilai 3–7. Ini **evaluasi per file** dengan panjang/tingkat agregasi berbeda antarkelas, bukan 272 segmen homogen. Sumber: `src/evaluate_validation_folder.py:50-108,110-239`.

## Alur internal aktual

1. `process_dataset` memindai semua audio berekstensi WAV/MP3/FLAC/OGG/M4A di root workspace, kecuali path `skripsi_residual_modulasi/data/processed` dan `web_cek` (`src/prepare_dataset.py:37-63`). Kelayakan hanya ukuran file ≥1.000 byte; `min_duration` pada tanda tangan fungsi tidak dipakai (`:18-25`).
2. Label real diberikan bila path memuat `/real/`, `/suara_real/`, `suara_real`, atau nama file memuat `real_`; sisanya fake (`:67-87`). Ini menjelaskan salah label 34 rekaman `Suara_untuk_validasi/Data_real/...`: direktori `Data_real` tidak cocok dengan pola tersebut. `source_manifest.csv` menyimpan `label`, `label_idx`, `dataset=CUSTOM_DATASET`, `sha256=N/A`; tidak ada `generator_id`, durasi asli, atau sampling rate sumber.
3. Audio dibaca dengan `librosa.load(..., sr=16000)` sehingga mono/resampling 16 kHz, dipotong menjadi WAV 32.000 sampel tanpa overlap; hanya potongan penuh yang dipakai. Penulisan dilakukan `soundfile.write` (`:115-178`). `audio_io.load_audio` kemudian membaca tiap potongan dengan peak normalization per file dan `segment_audio` mengembalikan satu segmen 2 detik (`audio_io.py:19-108`).
4. Dua kelas disamakan ke 27.788 potongan masing-masing dengan `DataFrame.sample(random_state=42)`, digabung lalu diacak. Dua `train_test_split` terstratifikasi menghasilkan 70% train, 15% validation, 15% test pada **level potongan** (`prepare_dataset.py:181-215`).

| Split | Real | Fake | Jumlah |
|---|---:|---:|---:|
| Train | 19.451 | 19.452 | 38.903 |
| Validation | 4.168 | 4.168 | 8.336 |
| Test | 4.169 | 4.168 | 8.337 |

Sumber tabel: `manifests/split_manifest_2s.csv` dan `results/features_{train,validation,test}.csv`. Ketiga CSV fitur berisi tepat 38.903/8.336/8.337 baris dengan `n_segments=1`, sehingga jumlah berhasil diekstraksi cocok dengan manifest. Jumlah sumber *real/fake asli yang benar secara semantik* tidak sepenuhnya terverifikasi karena salah label di atas dan salinan sumber.

## Speaker, sumber, duplikasi, dan kebocoran

`extract_speaker_id` memakai stem file: WhatsApp memakai seluruh stem, `id...-` memakai prefiks, nama dengan underscore memakai bagian sebelum underscore, sisanya seluruh stem (`prepare_dataset.py:27-35`). Karena penamaan file heterogen, `speaker_id` tidak selalu identitas orang; manifest mempunyai 6.982 nilai unik. **Sebanyak 4.576 nilai `speaker_id` teramati di lebih dari satu split.** `check_leakage.py:41-61` hanya memeriksa `utterance_id`, walaupun docstring menyebut speaker dan SHA-256. UUID potongan memang unik, namun potongan dari sumber yang sama dapat tersebar antar split. Tidak ada hash audio efektif pada manifest akhir (`sha256=N/A` pada semua 55.576 baris).

Rute `build_manifest.py` + `make_splits.py` memiliki SHA-256 dan GroupShuffleSplit (`build_manifest.py:37-196`, `make_splits.py:28-113`), tetapi format dan isi manifest tersimpan menunjukkan rute `prepare_dataset.py`, bukan rute group split itu. Karena itu pernyataan “speaker-independent internal test” dalam README/laporan tidak terkonfirmasi dan bertentangan dengan manifest final.

Keterkaitan set eksternal lebih langsung: 170 file dari `Suara_untuk_validasi` muncul dalam rekap sumber sebelum training (34 real asli + 136 fake). Pencocokan gabungan stem dan hash enam digit dari path sumber yang dipakai untuk nama potongan (`prepare_dataset.py:129-139`) ke manifest menemukan 163 file sumber terpilih dan 460 potongan internal: 321 train, 72 validation, 67 test. Dari 34 file real sumber eksternal, 33 terpilih menjadi 117 potongan **dengan label fake**. Dari 136 fake, 130 terpilih menjadi 343 potongan. Ini bukti tumpang tindih sumber/pembicara dengan set evaluasi eksternal; tidak menyatakan file WAV 2 detik final semuanya byte-identik dengan potongan train. Pada 17 speaker, rekaman asal atau hasil cloning yang terkait tampak dalam data training; klaim “audio/speaker eksternal belum pernah muncul di training” tidak dapat dipertahankan dari artefak ini.

## Asal generator dan batas verifikasi

Empat generator **eksternal** terverifikasi dari folder dan CSV prediksi. Dataset internal `Folder_dataset/Training/` memiliki folder `E5TTS`, `F5TTS`, `Openvoice`, `Voxcpm`, tetapi manifest tidak menyimpan `generator_id`; baris fitur internal berisi `generator_id=unknown` (`extract_features.py:190-214`). Karena pemindai juga menyertakan `scratch` dan validasi, komposisi generator dari 27.788 potongan fake internal tidak dapat dihitung langsung dari manifest. README menyebut DEEP-VOICE dan ASVspoof 2021 sebagai rencana; manifest final seluruhnya `CUSTOM_DATASET`, tanpa bukti evaluasi ASVspoof.

## Durasi dan sample rate

Segmen internal ditulis 2,0 detik pada 16 kHz (`prepare_dataset.py:115-178`). Nilai laju sampel audio sumber dan rentang durasi sumber tidak disimpan dalam rekap/manifest akhir. Evaluasi eksternal menggunakan fungsi ekstraksi yang melakukan resampling ke 16 kHz, peak normalization, dan rata-rata vektor fitur atas segmen penuh 2 detik (`audio_io.py:19-108`, `extract_features.py:56-187`). Tidak ada agregasi skor segment-to-utterance yang dipakai dalam jalur utama: `aggregate_scores.py` tersedia sebagai helper, tetapi `segment_scores.csv` tidak ditemukan.
