# Laporan Verifikasi Keterpisahan Data Evaluasi Eksternal

Tanggal pemeriksaan: 25 November 2026  
Ruang lingkup: Verifikasi keterpisahan antara 272 file audio evaluasi eksternal (136 Real, 136 Fake, 17 penutur) dengan dataset internal (data latih, validasi, dan uji).

---

## Ringkasan

- **File identik (hash):** 85 berkas pada dataset internal aktif (`split_manifest_2s.csv`), terdiri dari 59 pada split *train*, 14 pada split *validation*, dan 12 pada split *test*. Pada repositori segmen olahan internal (`skripsi_residual_modulasi/data/processed/2s`), ditemukan 136 berkas identik (100% dari seluruh 136 file audio Real evaluasi eksternal).
- **Penutur yang sama:** 17 dari 17 penutur eksternal (100%) muncul di dataset internal. Seluruh 17 penutur (100%) memiliki segmen audio yang masuk ke dalam split *train* (data latih internal). Selain itu, penulis sendiri (`alvin` / `alpin` / `apin`) dan penutur keluarga (`mama`) hadir sebagai target suara kloning maupun penutur dataset internal.
- **Tuturan yang sama:** Tidak dapat dihitung secara kuantitatif (transkrip teks tidak tersedia untuk berkas evaluasi eksternal dan berkas audio lokal/generator internal). Secara kualitatif teramati kesamaan naskah acuan ("Suaraindo", "Suarainggris", dan "dari apin").
- **Kesesuaian dengan daftar audit:** Cocok dan terkonfirmasi dengan bukti hash yang lebih kuat. Catatan audit repositori (`docs/thesis_handoff/03_DATASET_AND_PIPELINE.md` dan `08_VERIFICATION_AND_GAPS.md`) mencatat bahwa 170 berkas sumber validasi masuk dalam rekap pemindaian awal (`dataset_recap_raw.csv`), menghasilkan 163 sumber terpilih menjadi 460 potongan internal (321 train, 72 val, 67 test), dengan 34 file Real validasi salah label menjadi fake. Pemeriksaan hash ini mengonfirmasi temuan tersebut dan membuktikan bahwa 85 potongan di antarmuka manifest internal berstatus **byte-identik (SHA-256 identik)** dengan file evaluasi eksternal `Data_real` (59 di antaranya di data latih), serta seluruh 136 potongan real eksternal memiliki salinan identik di `data/processed/2s`.

---

## Detail temuan

### 1. Masukan dan Jalur Data yang Diperiksa

1. **Folder Evaluasi Eksternal (`[PATH_EKSTERNAL]`):** `Suara_untuk_validasi/`
   - `Data_real/`: 136 file WAV 16 kHz (2,0 detik per chunk; 17 penutur × 2 rekaman [Indo & Inggris] × 4 chunk).
   - `fake/`: 136 file audio (102 WAV, 34 MP3; 17 penutur × 2 rekaman × 4 generator: E2TTS_Base, F5TTS_Base, Open_voice, VoxCPM).
   - `Data_real_raw_backup/`: 34 file mentah (.ogg / .wav) sebelum pemotongan 2 detik.
   - Total file evaluasi eksternal aktif: **272 file** (136 Real, 136 Fake).
2. **Folder Dataset Internal (`[PATH_INTERNAL]`):**
   - Sumber audio mentah internal:
     - `Folder_dataset/Suara_real/`: 67 rekaman voice note WhatsApp lokal (.ogg/.mp3), 6 unduhan YouTube (.mp3), RAVDESS (2.880 file WAV), UserLibri (5.559 file FLAC).
     - `Folder_dataset/Training/`: 636 file WAV keluaran generator internal (E5TTS, F5TTS, Openvoice, Voxcpm).
     - `Folder_dataset/testing/`: 156 file WAV keluaran generator internal (E2TTS, F5TTS, OpenVoice, Voxcpm).
     - `skripsi_residual_modulasi/scratch/`: salinan/cache UserLibri (5.559 FLAC) dan RAVDESS (2.880 WAV).
   - Segmen audio olahan 2 detik internal: `skripsi_residual_modulasi/data/processed/2s/` (98.067 file WAV 16 kHz, 2 detik).
   - Manifest partisi internal aktif: `skripsi_residual_modulasi/manifests/split_manifest_2s.csv` (55.576 baris: 38.903 train, 8.336 validation, 8.337 test).
3. **Daftar Audit Repositori (`[PATH_DAFTAR_AUDIT]`):**
   - `docs/thesis_handoff/03_DATASET_AND_PIPELINE.md`
   - `docs/thesis_handoff/08_VERIFICATION_AND_GAPS.md`
   - `skripsi_residual_modulasi/results/dataset_recap_raw.csv`

---

### 2. Temuan Langkah 1: File Identik (Pencocokan Hash SHA-256)

Pemeriksaan hash SHA-256 dilakukan secara menyeluruh antara seluruh 272 berkas evaluasi eksternal terhadap seluruh direktori internal.

#### A. Ringkasan Pencocokan Hash

| Lokasi Dataset Internal yang Dibandingkan | Jumlah File Diperiksa | Jumlah File Eksternal yang Hash SHA-256 Identik | Keterangan |
|---|---|---|---|
| `split_manifest_2s.csv` (Dataset Internal Aktif) | 55.576 segmen | **85 berkas** (59 train, 14 val, 12 test) | Berasal dari `Data_real` eksternal, seluruhnya berlabel salah (`fake`) di manifest |
| `skripsi_residual_modulasi/data/processed/2s/` | 98.067 segmen | **136 berkas** (100% dari `Data_real`) | Seluruh potongan 2 detik `Data_real` identik dengan segmen olahan pemindai internal |
| `Folder_dataset/` | 9.578 berkas | **0 berkas** | Sumber mentah internal berada di folder terpisah dari folder validasi |
| `skripsi_residual_modulasi/scratch/` | 8.720 berkas | **0 berkas** | Khusus duplikasi UserLibri dan RAVDESS |

*Catatan untuk berkas Fake eksternal (136 file):* Berkas fake eksternal di `Suara_untuk_validasi/fake/` berdurasi utuh (6–14 detik), sedangkan dataset internal dipotong menjadi segmen 2,0 detik. Oleh karena itu, hash SHA-256 file utuh fake eksternal tidak identik langsung dengan file chunk 2 detik, meskipun berkas sumbernya sama-sama dipotong ke `data/processed/2s` (menghasilkan 343 potongan di `split_manifest_2s.csv`, 241 di antaranya di split *train*).

#### B. Sebaran 85 File Identik di Manifest Internal per Penutur

Sebanyak 85 file dari 136 file `Data_real` eksternal terbukti byte-identik dengan potongan yang aktif digunakan dalam model internal:

| Penutur | Total File Identik di Manifest | Masuk Data Latih (*Train*) | Masuk Validasi (*Validation*) | Masuk Uji Internal (*Test*) |
|---|---:|---:|---:|---:|
| **Farhan** | 7 | 4 | 2 | 1 |
| **Ilham** | 7 | 6 | 1 | 0 |
| **Erpan** | 6 | 3 | 2 | 1 |
| **fawwas** | 6 | 5 | 0 | 1 |
| **Ivang** | 6 | 3 | 2 | 1 |
| **mama** | 6 | 3 | 2 | 1 |
| **Wina** | 6 | 4 | 1 | 1 |
| **Diqqy** | 5 | 2 | 2 | 1 |
| **Furqon** | 5 | 5 | 0 | 0 |
| **Haikal** | 5 | 5 | 0 | 0 |
| **nida** | 5 | 3 | 0 | 2 |
| **Sheindy** | 5 | 4 | 1 | 0 |
| **abe** | 4 | 3 | 0 | 1 |
| **Selvi** | 4 | 4 | 0 | 0 |
| **Alyak** | 3 | 3 | 0 | 0 |
| **KakZiyyan** | 3 | 2 | 1 | 0 |
| **yasmin** | 2 | 0 | 0 | 2 |
| **TOTAL** | **85** | **59** | **14** | **12** |

*Catatan penting:* Penutur `yasmin` memiliki 2 segmen identik pada split test internal dari jalur Real, namun pada segmen jalur Fake internal, penutur `yasmin` memiliki **7 segmen pada data latih (train)**. Dengan demikian, seluruh 17 penutur tanpa terkecuali terpapar ke data latih model.

#### C. Daftar Sampel Pasangan Berkas Identik (SHA-256)

Berikut adalah sampel pasangan berkas evaluasi eksternal dengan berkas internal di `split_manifest_2s.csv` (seluruh 85 pasangan tersimpan lengkap pada berkas kerja verifikasi):

| No | Penutur | Berkas Evaluasi Eksternal (`Data_real`) | Berkas Dataset Internal (`manifest`) | Split | Label Manifest | Hash SHA-256 (16 Karakter Awal) |
|---:|---|---|---|---|---|---|
| 1 | abe | `Suaraindo_abe_chunk1.wav` | `fake_Suaraindo_abe_ef2d2b_chunk0.wav` | **train** | fake | `ad211b442a4e8641...` |
| 2 | abe | `Suaraindo_abe_chunk2.wav` | `fake_Suaraindo_abe_ef2d2b_chunk1.wav` | **train** | fake | `534ee722d3b0c0ec...` |
| 3 | abe | `Suarainggris_abe_chunk2.wav` | `fake_Suarainggris_abe_a04326_chunk1.wav` | **train** | fake | `1b807681b1e7f6e2...` |
| 4 | abe | `Suaraindo_abe_chunk3.wav` | `fake_Suaraindo_abe_ef2d2b_chunk2.wav` | **test** | fake | `6ae9f37d46f3b735...` |
| 5 | Diqqy | `Suaraindo_diqqy_chunk1.wav` | `fake_Suaraindo_diqqy_ef8767_chunk0.wav` | **train** | fake | `9f3c22e67a268a0c...` |
| 6 | Diqqy | `Suarainggris_diqqy_chunk4.wav` | `fake_Suarainggris_diqqy_4c2dcb_chunk3.wav` | **train** | fake | `52af986ef27cb099...` |
| 7 | Diqqy | `Suaraindo_diqqy_chunk3.wav` | `fake_Suaraindo_diqqy_ef8767_chunk2.wav` | **validation** | fake | `593c8e96b14bfa4a...` |
| 8 | Diqqy | `Suarainggris_diqqy_chunk2.wav` | `fake_Suarainggris_diqqy_4c2dcb_chunk1.wav` | **test** | fake | `db50765d81a4d1d9...` |
| 9 | Erpan | `Suaraindo_erpan_chunk1.wav` | `fake_Suaraindo_erpan_92aa24_chunk0.wav` | **train** | fake | `b41d507613ed6b84...` |
| 10 | Erpan | `Suarainggris_erpan_chunk1.wav` | `fake_Suarainggris_erpan_b499ca_chunk0.wav` | **train** | fake | `1e84a699a7872083...` |
| 11 | Farhan | `Suaraindo_farhan_chunk1.wav` | `fake_Suaraindo_farhan_8ebbe6_chunk0.wav` | **train** | fake | `72d5c897b0380e22...` |
| 12 | Furqon | `Suaraindo_furqon_chunk1.wav` | `fake_Suaraindo_furqon_e22ffc_chunk0.wav` | **train** | fake | `4d7fbbfc14868e8d...` |
| 13 | Haikal | `Suaraindo_Haikal_chunk1.wav` | `fake_Suaraindo_Haikal_0f356f_chunk0.wav` | **train** | fake | `4d7fd47ac14736f5...` |
| 14 | Ilham | `Suaraindo_ilham_chunk1.wav` | `fake_Suaraindo_ilham_cb8857_chunk0.wav` | **train** | fake | `f5d1c3dba75143a5...` |
| 15 | Ivang | `Suaraindo_ivang_chunk1.wav` | `fake_Suaraindo_ivang_61c809_chunk0.wav` | **train** | fake | `2801301164b77f98...` |
| 16 | Alyak | `Suaraindo_alyak_chunk2.wav` | `fake_Suaraindo_alyak_f7432d_chunk1.wav` | **train** | fake | `fa2aa4f078cd20f7...` |
| 17 | KakZiyyan | `Suaraindo_kakziyyan_chunk1.wav` | `fake_Suaraindo_kakziyyan_5a02a5_chunk0.wav` | **train** | fake | `28114523cedb28ad...` |
| 18 | mama | `Suaraindo_mama_chunk2.wav` | `fake_Suaraindo_mama_0758f5_chunk1.wav` | **train** | fake | `2db4eb4a0af16c14...` |
| 19 | nida | `Suaraindo_nida_chunk3.wav` | `fake_Suaraindo_nida_755fad_chunk2.wav` | **train** | fake | `ad9f2c4d7dab2ef2...` |
| 20 | Selvi | `Suaraindo_selvi_chunk1.wav` | `fake_Suaraindo_selvi_f60584_chunk0.wav` | **train** | fake | `26a5b1fd59e0f63b...` |
| 21 | Sheindy | `Suaraindo_sheindy_chunk2.wav` | `fake_Suaraindo_sheindy_9db962_chunk1.wav` | **train** | fake | `03a2ba08a9e1e127...` |
| 22 | Wina | `Suaraindo_wina_chunk2.wav` | `fake_Suaraindo_wina_d35f6e_chunk1.wav` | **train** | fake | `7f994f64bede012f...` |
| 23 | yasmin | `Suarainggris_yasmin_chunk2.wav` | `fake_Suarainggris_yasmin_f80ba5_chunk1.wav` | **test** | fake | `344b6cb56bc29505...` |

*(Daftar lengkap seluruh 85 pasangan tersedia pada berkas sementara `scratch/table_matches.md`).*

---

### 3. Temuan Langkah 2: Penutur yang Sama (Speaker Overlap)

Pemeriksaan metadata penutur mengevaluasi 17 penutur evaluasi eksternal terhadap seluruh sumber internal.

#### A. Tumpang Tindih 17 Penutur Eksternal di Dataset Internal

| Penutur Eksternal | Gender | Jumlah Segmen di `split_manifest_2s.csv` | Segmen di Train | Segmen di Validation | Segmen di Test | Keberadaan di Data Latih (*Train*) |
|---|---|---:|---:|---:|---:|:---:|
| **abe** | Laki-laki | 9 | 5 | 2 | 2 | **YA** |
| **Diqqy** | Laki-laki | 8 | 6 | 2 | 0 | **YA** |
| **Erpan** | Laki-laki | 9 | 4 | 2 | 3 | **YA** |
| **Farhan** | Laki-laki | 11 | 9 | 1 | 1 | **YA** |
| **fawwas** | Laki-laki | 5 | 3 | 0 | 2 | **YA** |
| **Furqon** | Laki-laki | 8 | 5 | 2 | 1 | **YA** |
| **Haikal** | Laki-laki | 11 | 9 | 1 | 1 | **YA** |
| **Ilham** | Laki-laki | 12 | 11 | 0 | 1 | **YA** |
| **Ivang** | Laki-laki | 7 | 3 | 2 | 2 | **YA** |
| **Alyak** | Perempuan | 14 | 12 | 1 | 1 | **YA** |
| **KakZiyyan** | Perempuan | 12 | 9 | 1 | 2 | **YA** |
| **mama** | Perempuan | 12 | 7 | 2 | 3 | **YA** |
| **nida** | Perempuan | 7 | 5 | 1 | 1 | **YA** |
| **Selvi** | Perempuan | 7 | 5 | 2 | 0 | **YA** |
| **Sheindy** | Perempuan | 8 | 6 | 1 | 1 | **YA** |
| **Wina** | Perempuan | 8 | 6 | 0 | 2 | **YA** |
| **yasmin** | Perempuan | 11 | 7 | 4 | 0 | **YA** |
| **TOTAL** | **9L, 8P** | **159 segmen** | **112 train** | **23 val** | **24 test** | **17/17 (100%)** |

*Keterangan tabel:* 159 segmen di atas mencakup segmen dengan `speaker_id` yang dinormalisasi langsung ke nama penutur. Jika digabungkan dengan segmen yang menggunakan prefiks `apin`/`apininggris`/`suaraindo`/`suarainggris` dari berkas sumber validasi, total segmen mencapai **460 segmen** (321 train, 72 val, 67 test).

#### B. Keterkaitan Penulis Sendiri dan Keluarga

1. **Penulis Sendiri (`Alvin` / `alpin` / `apin`):**
   - Nama penulis adalah Alvin Rifky Wahyudi.
   - Pada folder evaluasi eksternal `Suara_untuk_validasi/fake/`, seluruh **136 berkas kloning suara palsu** dinamai `apin.wav` dan `apininggris.wav` di bawah folder masing-masing dari 17 penutur.
   - Pada dataset internal `Folder_dataset/Training/`, suara `alpin` digunakan sebagai data latih kloning di bawah 4 subdirektori generator:
     - `Training/E5TTS/Male/alpin/`
     - `Training/F5TTS/Male/alpin/`
     - `Training/Openvoice/male/alpin/`
     - `Training/Voxcpm/Male/alpin/`
2. **Keluarga Penulis (`mama`):**
   - Penutur `mama` merupakan salah satu dari 17 penutur evaluasi eksternal (`Suara_untuk_validasi/Data_real/perempuan/mama`).
   - Penutur `mama` juga merupakan penutur di dataset internal: `Folder_dataset/Training/` memuat **33 berkas audio** dari `Suara_mama` pada 4 generator:
     - `Training/E5TTS/Female/Suara_mama/`
     - `Training/F5TTS/Female/Suara_mama/`
     - `Training/Openvoice/female/Suara_mama/`
     - `Training/Voxcpm/Female/Suara_mama/`
3. **Keluarga Lain (`Suara_ayah` dan `Suara_inut`):**
   - Di `Folder_dataset/Suara_real/` terdapat rekaman `Suara_ayah.ogg` dan `Suara_inut.ogg`. Keduanya juga digunakan pada folder `Folder_dataset/Training/` di seluruh 4 generator sintesis.

#### C. Keterkaitan dengan Aktor RAVDESS dan UserLibri

- **Aktor RAVDESS:** RAVDESS internal menggunakan 24 aktor profesional berbahasa Inggris (`Actor_01` s.d. `Actor_24`). Tidak ada aktor RAVDESS yang tumpang tindih dengan 17 penutur evaluasi eksternal.
- **Speaker UserLibri:** UserLibri internal menggunakan ID numerik pembaca buku audio LibriSpeech berbahasa Inggris (misalnya `speaker-1089`, `speaker-1188`, `speaker-121`, dst.). Tidak ada speaker UserLibri yang tumpang tindih dengan 17 penutur evaluasi eksternal.

---

### 4. Temuan Langkah 3: Isi Tuturan yang Sama

- **Transkrip Teks:** Berkas transkripsi teks resmi (`.txt` atau sejenisnya) **tidak tersedia** pada direktori `Suara_untuk_validasi`, `Folder_dataset/Suara_real` (voice note), maupun pada folder `Folder_dataset/Training`. Transkrip teks hanya tersedia pada subset korpus UserLibri (`.trans.txt`).
- **Sesuai Aturan Pemeriksaan:** Karena transkrip teks tidak tersedia secara tertulis, jumlah pasangan tuturan yang sama **tidak dapat diisi dengan angka pasti** dan dicatat sebagai keterbatasan metodologis.
- **Keterkaitan Kualitatif yang Teramati:**
  - File evaluasi Real terdiri atas rekaman membaca naskah Indonesia (`Suaraindo_*`) dan naskah Inggris (`Suarainggris_*`) yang seragam di antara ke-17 penutur.
  - File evaluasi Fake disintesis dari naskah teks target yang sama (`apin.wav` dan `apininggris.wav`). Pada `Folder_dataset/Training/Openvoice/female/Suara_mama/`, nama berkas secara eksplisit mencatat `Suara_mama_text_dariapin*.wav`, yang mengonfirmasi bahwa naskah acuan yang dibacakan/disintesis saling berkaitan langsung.

---

### 5. Temuan Langkah 4: Pencocokan dengan Daftar Catatan Audit Repositori

Catatan audit pada `docs/thesis_handoff/03_DATASET_AND_PIPELINE.md` dan `08_VERIFICATION_AND_GAPS.md` mencatat hal-hal berikut:

| Poin Audit Repositori | Temuan Pemeriksaan Ini | Status Kesesuaian |
|---|---|:---:|
| 170 berkas dari `Suara_untuk_validasi` masuk dalam `dataset_recap_raw.csv` | Dikonfirmasi: tepat 170 berkas (34 `Data_real` mentah + 136 `fake`) tercatat di rekap pemindaian awal | **Cocok Sempurna** |
| 163 sumber validasi terpilih menjadi 460 potongan di `split_manifest_2s.csv` (321 train, 72 val, 67 test) | Dikonfirmasi: tepat 163 sumber unik menghasilkan 460 potongan (321 train, 72 val, 67 test) | **Cocok Sempurna** |
| 34 file Real validasi salah diberi label `fake` di manifest | Dikonfirmasi: 33 file Real terpilih menghasilkan 117 potongan di manifest, semuanya salah label (`label=fake`) | **Cocok Sempurna** |
| 7 file validasi tidak terpilih ke manifest | Dikonfirmasi: 1 file Real (`Suaraindo_yasmin.ogg`) dan 6 file Fake tidak terpilih saat sampling penyeimbangan kelas | **Cocok Sempurna** |
| Audit menyatakan: *"tidak menyatakan file WAV 2 detik final semuanya byte-identik dengan potongan train"* | **Temuan Baru Pemeriksaan Ini:** Pemeriksaan hash membuktikan bahwa **85 berkas potongan 2 detik** dari 136 file `Data_real` evaluasi eksternal berstatus **byte-identik (SHA-256 identik)** dengan potongan di `split_manifest_2s.csv` (59 berkas di train, 14 di val, 12 di test). Pada level olahan segmen disk (`data/processed/2s`), seluruh **136 berkas Real eksternal (100%)** memiliki berkas identik hasil pemotongan `prepare_dataset.py`. | **Terkonfirmasi Lebih Kuat dari Dugaan Awal Audit** |

---

## Keterbatasan

1. **Ketiadaan Transkrip Tekstual:** Transkrip teks penuturan tidak disertakan dalam artefak repositori untuk berkas audio rekaman WhatsApp lokal (`Suara_untuk_validasi` dan `Folder_dataset/Suara_real`) maupun berkas sintetis keluaran generator. Oleh karena itu, perbandingan isi tuturan tidak dapat dilakukan melalui pencocokan teks terotomatisasi (*exact string match*), melainkan hanya disimpulkan dari pola penamaan berkas dan naskah acuan.
2. **Perbedaan Satuan Berkas Antarkelas pada Evaluasi Eksternal:** Berkas Real pada evaluasi eksternal telah dipotong menjadi file 2,0 detik (WAV 16 kHz), sedangkan berkas Fake dibiarkan dalam durasi asli (6–14 detik). Hal ini menyebabkan pencocokan hash SHA-256 untuk Fake eksternal terhadap chunk 2 detik internal bernilai nol pada tingkat berkas utuh, meskipun potongan segmen dari berkas yang sama terbukti secara langsung mengisi 343 baris di manifest internal.
3. **Metadata Generator Internal Terbatas:** Pada manifest internal `split_manifest_2s.csv`, kolom `generator_id` tidak disimpan (seluruh baris berlabel `dataset=CUSTOM_DATASET`), sehingga penelusuran proporsi masing-masing generator fake internal harus dianalisis melalui struktur nama berkas dan direktori sumber mentah (`Folder_dataset/Training/` dan `dataset_recap_raw.csv`).

---

## Kesimpulan

Ditemukan keterkaitan sebanyak 85 file identik pada pemeriksaan hash di manifest internal (136 file di direktori segmen internal), 17 penutur pada aspek penutur (seluruhnya terdapat pada data latih), serta keterkaitan sumber pada 163 dari 170 berkas validasi.

Dengan demikian, data evaluasi eksternal **TIDAK TERPISAH** dari dataset internal (data latih, validasi, dan uji). Klaim bahwa pengujian eksternal 272 berkas merupakan pengujian independen (*blind external evaluation*) atau *speaker-independent* tidak didukung oleh bukti artefak repositori.
