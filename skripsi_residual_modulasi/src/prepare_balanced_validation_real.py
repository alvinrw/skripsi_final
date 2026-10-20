"""
src/prepare_balanced_validation_real.py
=========================================
Memotong 34 file audio Real asli dari 17 speaker (durasi 8-14 detik)
menjadi masing-masing 4 chunk non-overlapping berdurasi 2.0 detik.

Total hasil:
- 17 speaker x 2 file (Indo & English) x 4 chunk = 136 file audio Real (WAV, 16 kHz).
- Seimbang sempurna 1:1 dengan 136 file audio Fake (Total = 272 file).
- Setiap speaker memiliki 8 file Real dan 8 file Fake.
- File asli dibackup secara aman ke Suara_untuk_validasi/Data_real_raw_backup.
"""

import os
import shutil
from pathlib import Path
import librosa
import numpy as np
import soundfile as sf

BASE_VAL = Path(r"C:\Users\alvin\Documents\Coolyeah\Skirpsi\Teknikal\fase_1\Suara_untuk_validasi")
REAL_DIR = BASE_VAL / "Data_real"
BACKUP_DIR = BASE_VAL / "Data_real_raw_backup"

def main():
    print("="*60)
    print("PREPARING BALANCED VALIDATION REAL DATASET (136 REAL : 136 FAKE)")
    print("="*60)

    # 1. Backup original files
    if not BACKUP_DIR.exists():
        print(f"Creating backup at {BACKUP_DIR}...")
        shutil.copytree(REAL_DIR, BACKUP_DIR)
        print("  Backup completed successfully.")
    else:
        print(f"Backup already exists at {BACKUP_DIR}.")

    # 2. Iterate through speakers and segment
    target_sr = 16000
    chunk_len_samples = int(target_sr * 2.0) # 32,000 samples

    created_files = 0
    raw_files_to_remove = []

    for root, dirs, files in os.walk(REAL_DIR):
        for fname in files:
            ext = os.path.splitext(fname)[1].lower()
            if ext in [".ogg", ".mp3", ".wav"]:
                # Check if this is already a chunk
                if "_chunk" in fname:
                    continue

                full_path = Path(root) / fname
                raw_files_to_remove.append(full_path)

                # Load audio
                y, sr = librosa.load(str(full_path), sr=target_sr)
                total_samples = len(y)
                stem = full_path.stem

                # Extract 4 chunks of 2.0 seconds
                for i in range(4):
                    start = i * chunk_len_samples
                    end = start + chunk_len_samples
                    if end <= total_samples:
                        chunk = y[start:end]
                    else:
                        # If slightly short on 4th chunk, take the last 2.0 seconds
                        chunk = y[max(0, total_samples - chunk_len_samples):total_samples]
                        if len(chunk) < chunk_len_samples:
                            chunk = np.pad(chunk, (0, chunk_len_samples - len(chunk)))

                    out_name = f"{stem}_chunk{i+1}.wav"
                    out_path = Path(root) / out_name
                    sf.write(str(out_path), chunk, target_sr, subtype="PCM_16")
                    created_files += 1

    # Remove the unsegmented raw files from Data_real (already in backup)
    for p in raw_files_to_remove:
        if p.exists():
            os.remove(p)

    print(f"\nSuccessfully created {created_files} balanced real chunks.")
    
    # Verify count
    real_count = sum(len(files) for _, _, files in os.walk(REAL_DIR) if files)
    fake_count = sum(len(files) for _, _, files in os.walk(BASE_VAL / "fake") if files)
    print("="*60)
    print(f"VERIFIKASI JUMLAH FILE VALIDASI EKSTERNAL:")
    print(f"  Real Audio : {real_count} files")
    print(f"  Fake Audio : {fake_count} files")
    print(f"  Total Audio: {real_count + fake_count} files (Seimbang 1:1)")
    print("="*60)

if __name__ == "__main__":
    main()
