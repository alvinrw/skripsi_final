# What I Have to Do Right Now

**Roadmap Skripsi — Deteksi Speech Deepfake dengan Residual dan Modulation Spectrum**  
**Fokus:** Setelah training selesai, beralih dari metrik model menuju analisis bukti forensik dan penulisan Bab 4.

> **Prioritas:** Analisis → Konsistensi → Pembahasan. Tidak perlu mengulang training yang sudah selesai.

## 1. Posisi Penelitian Saat Ini

Berdasarkan progres yang sudah dilaporkan:

- [x] Training model baseline dan rangkaian eksperimen B0 dan seterusnya sudah dilakukan.
- [x] Akurasi dan metrik evaluasi model sudah tersedia.
- [x] Pengujian audio baru dari **17 sumber suara**, mencakup suara asli dan hasil cloning dari **4 generator**, sudah dilakukan.
- [x] Akurasi terbaik yang dilaporkan pada pengujian tersebut sekitar **80%**.
- [ ] Verifikasi artefak eksperimen residual-only dan modulation-only: jangan mengasumsikan belum atau sudah tersedia tanpa memeriksa file hasil.

## 2. Audit Artefak Eksperimen

Sebelum membuat eksperimen baru, periksa apakah setiap hasil sudah punya bukti yang bisa dianalisis:

- [ ] **Residual LPC:** CSV fitur, quality control (QC), grafik distribusi, dan definisi fitur.
- [ ] **Modulation spectrum:** CSV fitur dan grafik spektrum rata-rata real vs fake.
- [ ] **Statistik bukti:** p-value, effect size, koreksi FDR, dan confidence interval.
- [ ] **Skor per audio:** skor baseline dan evidence pada **audio yang sama**.
- [ ] **Error cases:** daftar file yang benar/salah menurut masing-masing jalur.

Jika artefaknya sudah ada, **audit dan gunakan**; tidak perlu menghitung atau melatih ulang tanpa alasan.

## 3. Cek Bukti Residual dan Modulasi

### A. Residual LPC

Pastikan tersedia fitur berikut:

1. Residual energy.
2. Residual entropy.
3. Prediction error.
4. Excitation irregularity.
5. Kurtosis.

Periksa kualitas sinyal dan, jika eksperimennya dilakukan, sensitivitas terhadap orde LPC **12, 16, dan 20**.

### B. Modulation Spectrum

Pastikan tersedia amplitude envelope dan fitur energi relatif pada pita:

- 0,5–2 Hz
- 2–4 Hz
- 4–8 Hz
- 8–20 Hz

Bandingkan spektrum antara audio **real** dan **fake**.

**Output minimum:** tabel fitur per audio, visualisasi distribusi/spektrum, dan catatan QC.

## 4. Buktikan Perbedaan Secara Statistik

Jangan hanya menyimpulkan bahwa grafik tampak berbeda.

- [ ] Bandingkan median dan arah perbedaan tiap fitur antara real dan fake.
- [ ] Gunakan **Mann–Whitney U** bila sesuai dengan desain dan karakter data.
- [ ] Laporkan **effect size** (misalnya Cliff's delta atau rank-biserial).
- [ ] Terapkan koreksi **Benjamini–Hochberg FDR** untuk pengujian berganda.
- [ ] Hitung **bootstrap 95% confidence interval** bila relevan.
- [ ] Utamakan analisis pada **tingkat utterance/audio sumber**, bukan memperlakukan potongan 2 detik yang berkorelasi sebagai observasi independen.

**Output:** `statistical_tests.csv` dan 2–3 grafik fitur paling informatif.

## 5. Analisis Konsistensi: Baseline ML vs Bukti Forensik

Bandingkan dua jalur pada audio yang sama:

| Jalur | Dasar analisis |
|---|---|
| Baseline ML | MFCC/LFCC dan model klasifikasi yang sudah dilatih |
| Evidence-only | Fitur residual, modulasi, atau gabungannya **jika hasil eksperimennya tersedia** |

Pemeriksaan utama:

- [ ] **Spearman ρ:** korelasi skor prediksi kedua jalur.
- [ ] **Cohen's κ:** tingkat kesepakatan label prediksi.
- [ ] **Empat kategori hasil:** kedua jalur benar; kedua jalur salah; hanya baseline benar; hanya evidence benar.
- [ ] Gunakan threshold yang ditetapkan dari validasi, bukan dioptimalkan ulang menggunakan data test.

**Pertanyaan inti:** Apakah bukti residual/modulasi mendukung, melengkapi, atau justru bertentangan dengan keputusan model baseline?

## 6. Bedah Pengujian 17 Orang × 4 Generator

Akurasi sekitar 80% adalah titik awal, bukan akhir pembahasan.

- [ ] **Per speaker:** apakah hasil stabil di antara 17 sumber suara?
- [ ] **Per generator:** generator mana yang paling sering menghasilkan audio fake yang terdeteksi sebagai real?
- [ ] **Per kelas:** pisahkan *false positive* (real diprediksi fake) dan *false negative* (fake diprediksi real).
- [ ] **Per kasus salah:** cek apakah fitur residual dan modulasi memberikan petunjuk mengenai kesalahan tersebut.
- [ ] Laporkan jumlah file audio real/fake yang benar-benar diuji; **17 orang bukan berarti hanya 17 file uji**.

Metadata minimum per file:

```text
utterance_id, speaker_id, generator_id, label_asli,
model_name, skor_fake, prediksi, split, durasi
```

Jika ada beberapa potongan dari audio yang sama, pertahankan relasi ke `utterance_id` dan gunakan agregasi yang konsisten untuk evaluasi tingkat utterance.

## 7. Susun Hasil Menjadi Bab 4

Struktur kerja yang disarankan:

- **4.1 Dataset dan skenario pengujian:** sumber audio, preprocessing, pembagian data, 17 speaker, dan 4 generator.
- **4.2 Hasil model baseline:** metrik, tabel perbandingan, ROC/AUC/EER jika tersedia.
- **4.3 Hasil residual dan modulasi:** karakteristik sinyal, distribusi fitur, dan spektrum.
- **4.4 Analisis statistik bukti forensik:** signifikansi, effect size, dan confidence interval.
- **4.5 Konsistensi dua jalur:** korelasi skor, kesepakatan prediksi, dan kategori kesalahan.
- **4.6 Analisis pengujian eksternal:** per speaker, per generator, dan studi kasus kesalahan.

## 8. Rencana Kerja 7 Hari

| Hari | Pekerjaan | Hasil yang diharapkan |
|---|---|---|
| 1 | Inventaris semua hasil B0–B5, E2–E7, dan file prediksi yang benar-benar tersedia | Daftar artefak dan gap |
| 2 | Cek CSV residual/modulasi, grafik QC, dan spektrum | Bukti forensik siap dianalisis |
| 3 | Jalankan atau rapikan tabel statistik | `statistical_tests.csv` |
| 4 | Gabungkan skor baseline dan evidence per utterance | Tabel prediksi gabungan |
| 5 | Hitung Spearman, Kappa, dan empat kategori error | Tabel/grafik konsistensi |
| 6 | Analisis per speaker/generator dan pilih contoh audio | Studi kasus kesalahan |
| 7 | Rakit tabel, grafik, dan draft pembahasan | Kerangka Bab 4 |

> Jadwal ini fleksibel. Bila suatu artefak belum tersedia, catat sebagai gap; jangan menandainya selesai hanya karena model training sudah selesai.

## 9. Target Akhir

Penelitian tidak berhenti pada pernyataan **“model terbaik mencapai akurasi sekitar 80%”**. Hasil akhirnya perlu menjawab:

1. **Fitur akustik apa** yang membedakan real dan fake?
2. **Seberapa kuat dan konsisten** perbedaan itu secara statistik?
3. **Apakah bukti forensik sejalan** dengan prediksi model MFCC/LFCC?
4. **Mengapa model berhasil atau gagal** pada suara dari 17 orang dan empat generator?

**Langkah pertama sekarang:** buka folder hasil eksperimen, inventaris CSV fitur dan skor prediksi, lalu tentukan analisis mana yang belum mempunyai artefak. **Jangan mulai training ulang sebelum audit selesai.**
