import os
import sys
import glob
import hashlib
import librosa
import soundfile as sf
import pandas as pd
import numpy as np
import argparse
import shutil
import warnings
from pathlib import Path
from tqdm import tqdm
from sklearn.model_selection import train_test_split

warnings.filterwarnings("ignore")

def check_eligibility(filepath, min_duration=0.5):
    try:
        size = os.path.getsize(filepath)
        if size < 1000:
            return False, "Too small / corrupt"
        return True, "Eligible"
    except Exception as e:
        return False, f"Error: {e}"

def extract_speaker_id(filepath):
    stem = Path(filepath).stem.lower()
    if stem.startswith("whatsapp ptt") or stem.startswith("whatsapp"):
        return stem
    if stem.startswith("id") and "-" in stem:
        return stem.split("-")[0]
    if "_" in stem:
        return stem.split("_")[0]
    return stem

def process_dataset(root_dir=".", out_dir="data/processed", seed=42):
    print(f"\n[dataset_prep] Menjalankan pemrosesan dataset (Seed: {seed})...")
    np.random.seed(seed)
    
    out_path = Path(out_dir)
    manifests_dir = Path("manifests")
    results_dir = Path("results")
    
    out_path.mkdir(parents=True, exist_ok=True)
    manifests_dir.mkdir(parents=True, exist_ok=True)
    results_dir.mkdir(parents=True, exist_ok=True)
    
    audio_exts = {".wav", ".mp3", ".flac", ".ogg", ".m4a"}
    base_path = Path(root_dir).resolve()
    
    # Scan seluruh file audio yang ada di folder dataset (Folder_dataset, Suara_untuk_validasi, data/raw)
    all_found = []
    for p in base_path.rglob("*"):
        if p.is_file() and p.suffix.lower() in audio_exts:
            str_p = str(p).replace("\\", "/")
            # Abaikan folder internal
            if "skripsi_residual_modulasi/data/processed" in str_p or "web_cek" in str_p:
                continue
            all_found.append(p)
            
    print(f"[scan] Ditemukan total {len(all_found)} file audio mentah di workspace.")
    
    real_files = []
    fake_files = []
    
    for f in all_found:
        s = str(f).replace("\\", "/").lower()
        if "/real/" in s or "/suara_real/" in s or "suara_real" in s or "real_" in Path(f).name.lower():
            real_files.append(str(f))
        else:
            fake_files.append(str(f))
            
    print(f"  -> Real audio files : {len(real_files)}")
    print(f"  -> Fake audio files : {len(fake_files)} (Campuran E2TTS, E5TTS, F5TTS, OpenVoice, VoxCPM, dll)")
    
    all_files = []
    for f in real_files:
        all_files.append({"file_path": f, "label": "real", "label_idx": 0})
    for f in fake_files:
        all_files.append({"file_path": f, "label": "fake", "label_idx": 1})
        
    df = pd.DataFrame(all_files)
    if len(df) == 0:
        print("[FAIL] Tidak ada file audio ditemukan.")
        sys.exit(1)
        
    print("\n>> Tahap 1: Menjalankan Eligibility Check & QC...")
    eligibility = []
    for f in tqdm(df["file_path"], desc="QC Audio"):
        is_ok, reason = check_eligibility(f)
        eligibility.append((is_ok, reason))
        
    df["eligible"] = [e[0] for e in eligibility]
    df["reason"] = [e[1] for e in eligibility]
    df["speaker_id"] = df["file_path"].apply(lambda x: extract_speaker_id(Path(x).stem))
    
    df.to_csv(results_dir / "dataset_recap_raw.csv", index=False)
    
    eligible_count = df["eligible"].sum()
    print(f"  [Hasil QC] Eligible: {eligible_count} | Non-Eligible: {len(df) - eligible_count}")
    
    df_valid = df[df["eligible"]].copy()
    if len(df_valid) == 0:
        print("[FAIL] Tidak ada file audio yang valid.")
        sys.exit(1)
        
    print("\n>> Tahap 2: Pemotongan Audio 2 Detik (Chunking)...")
    dur = 2
    sr = 16000
    chunk_length = int(dur * sr)
    
    dur_out_dir = out_path / f"{dur}s"
    dur_out_dir.mkdir(parents=True, exist_ok=True)
    
    chunk_rows = []
    for _, row in tqdm(df_valid.iterrows(), total=len(df_valid), desc="Chunking 2s"):
        try:
            orig_stem = Path(row["file_path"]).stem
            
            # Cek jika semua chunk dari file ini sudah ada di disk
            # Untuk efisiensi, load audio dan potong
            y = None
            num_chunks = None
            file_hash = hashlib.md5(row["file_path"].encode()).hexdigest()[:6]
            chunk_idx = 0
            
            while True:
                chunk_name = f"{row['label']}_{orig_stem}_{file_hash}_chunk{chunk_idx}.wav"
                chunk_path = dur_out_dir / chunk_name
                
                if chunk_path.exists() and chunk_path.stat().st_size > 44:
                    chunk_rows.append({
                        "utterance_id": chunk_name.replace(".wav", ""),
                        "file_path": str(chunk_path).replace("\\", "/"),
                        "label": row["label"],
                        "label_idx": row["label_idx"],
                        "speaker_id": row["speaker_id"],
                        "dataset": "CUSTOM_DATASET"
                    })
                    chunk_idx += 1
                else:
                    if num_chunks is None:
                        try:
                            info = sf.info(row["file_path"])
                            num_chunks = int(info.duration // dur)
                        except Exception:
                            num_chunks = 0
                    
                    if chunk_idx >= num_chunks:
                        break
                        
                    if y is None:
                        y, _ = librosa.load(row["file_path"], sr=sr)
                        num_chunks = len(y) // chunk_length
                    
                    if chunk_idx >= num_chunks:
                        break
                        
                    chunk = y[chunk_idx*chunk_length:(chunk_idx+1)*chunk_length]
                    sf.write(str(chunk_path), chunk, sr)
                    
                    chunk_rows.append({
                        "utterance_id": chunk_name.replace(".wav", ""),
                        "file_path": str(chunk_path).replace("\\", "/"),
                        "label": row["label"],
                        "label_idx": row["label_idx"],
                        "speaker_id": row["speaker_id"],
                        "dataset": "CUSTOM_DATASET"
                    })
                    chunk_idx += 1
        except Exception as e:
            continue
            
    df_chunks = pd.DataFrame(chunk_rows)
    print(f"  -> Total hasil potongan 2s: {len(df_chunks)} chunks")
    
    real_df_sub = df_chunks[df_chunks["label"] == "real"]
    fake_df_sub = df_chunks[df_chunks["label"] == "fake"]
    
    n_min = min(len(real_df_sub), len(fake_df_sub))
    print(f"\n>> Tahap 3: Balancing Class (50% Real : 50% Fake) -> {n_min} chunks per kelas (Total {n_min * 2} chunks)")
    
    real_balanced = real_df_sub.sample(n=n_min, random_state=seed)
    fake_balanced = fake_df_sub.sample(n=n_min, random_state=seed)
    
    df_chunks = pd.concat([real_balanced, fake_balanced], ignore_index=True)
    
    print("\n>> Tahap 4: Shuffle & Stratified Split (Seed: 42, Tanpa Group Speaker)...")
    # Shuffle seluruh chunk dataset
    df_chunks = df_chunks.sample(frac=1.0, random_state=seed).reset_index(drop=True)
    
    # Stratified Split 70% Train, 15% Validation, 15% Test
    labels = df_chunks["label_idx"]
    train_df, temp_df = train_test_split(
        df_chunks, test_size=0.30, stratify=labels, random_state=seed
    )
    val_df, test_df = train_test_split(
        temp_df, test_size=0.50, stratify=temp_df["label_idx"], random_state=seed
    )
    
    df_chunks.loc[train_df.index, "split"] = "train"
    df_chunks.loc[val_df.index, "split"] = "validation"
    df_chunks.loc[test_df.index, "split"] = "test"
    
    # Simpan Manifest CSV
    manifest_2s_csv = manifests_dir / "split_manifest_2s.csv"
    manifest_main_csv = manifests_dir / "split_manifest.csv"
    source_manifest_csv = manifests_dir / "source_manifest.csv"
    
    df_chunks.to_csv(manifest_2s_csv, index=False)
    df_chunks.to_csv(manifest_main_csv, index=False)
    
    # Source manifest
    source_df = df_chunks.copy()
    source_df["sha256"] = "N/A"
    source_df.to_csv(source_manifest_csv, index=False)
    
    print("\n============================================================")
    print("Ringkasan Hasil Pembagian Dataset (Split 2s, Seed 42):")
    print("============================================================")
    for sp in ["train", "validation", "test"]:
        sub = df_chunks[df_chunks["split"] == sp]
        r_n = (sub["label"] == "real").sum()
        f_n = (sub["label"] == "fake").sum()
        print(f"  {sp.capitalize():12s}: {len(sub):5d} chunks | Real: {r_n} | Fake: {f_n}")
    print("============================================================")
    print(f"[SUCCESS] Manifest tersimpan di {manifest_main_csv}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--root_dir", type=str, default=".")
    parser.add_argument("--out_dir", type=str, default="data/processed")
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()
    process_dataset(args.root_dir, args.out_dir, args.seed)
