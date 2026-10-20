"""
src/evaluate_validation_folder.py
===================================
Evaluasi komprehensif dataset eksternal Suara_untuk_validasi
terhadap seluruh 10 model yang telah dilatih (B0-B4 dan E4a-E4e).

Termasuk:
1. Standard Threshold (0.50)
2. Calibrated Threshold (Threshold Terkalibrasi Domain HP/WA Noise)

Output CSV:
- results/validation_external_predictions.csv
- results/validation_external_metrics.csv
- results/validation_external_category_breakdown.csv
"""

import os
import sys
from pathlib import Path
from concurrent.futures import ProcessPoolExecutor, as_completed
import joblib
import numpy as np
import pandas as pd
from tqdm import tqdm
from sklearn.metrics import (
    roc_auc_score, accuracy_score, precision_score, recall_score, f1_score
)

# Insert src to sys.path
SRC_DIR = Path(__file__).parent
sys.path.insert(0, str(SRC_DIR))

from reproducibility import load_config
from extract_features import extract_utterance_features
from metrics import compute_eer

CALIBRATED_THRESHOLDS = {
    "B0": 0.60,
    "B1": 0.60,
    "B2": 0.60,
    "B3": 0.50,
    "B4": 0.55,
    "E4a": 0.65,
    "E4b": 0.55,
    "E4c": 0.65,
    "E4d": 0.60,
    "E4e": 0.62,
}

def find_audio_files(base_dir: str):
    valid_exts = {".wav", ".mp3", ".flac", ".ogg", ".m4a", ".aac", ".mp4", ".webm"}
    files = []
    
    for root, dirs, filenames in os.walk(base_dir):
        # Ignore backup directories
        dirs[:] = [d for d in dirs if "backup" not in d.lower()]
        for fname in filenames:
            ext = os.path.splitext(fname)[1].lower()
            if ext in valid_exts:
                full_path = os.path.join(root, fname)
                rel_path = os.path.relpath(full_path, base_dir)
                parts = Path(rel_path).parts
                
                # Determine label & generator/category
                if "Data_real" in parts:
                    label = 0 # Real
                    label_str = "real"
                    category = parts[1] if len(parts) > 1 else "Data_real"
                elif "fake" in parts:
                    label = 1 # Fake
                    label_str = "fake"
                    category = parts[1] if len(parts) > 1 else "fake"
                else:
                    label = 0 if "real" in fname.lower() else 1
                    label_str = "real" if label == 0 else "fake"
                    category = "unknown"
                    
                files.append({
                    "file_name": fname,
                    "rel_path": rel_path,
                    "full_path": full_path,
                    "label": label,
                    "label_str": label_str,
                    "category": category
                })
                
    return files

def _worker_extract(item, cfg):
    full_path = item["full_path"]
    try:
        feat_dict = extract_utterance_features(full_path, cfg, lpc_order=16)
        if feat_dict is None:
            return None
        row = {
            "file_name": item["file_name"],
            "rel_path": item["rel_path"],
            "full_path": item["full_path"],
            "label": item["label"],
            "label_str": item["label_str"],
            "category": item["category"],
            "n_segments": feat_dict.get("n_segments", 1)
        }
        row.update(feat_dict)
        return row
    except Exception as e:
        print(f"Error extracting {full_path}: {e}")
        return None

def main():
    val_dir = r"C:\Users\alvin\Documents\Coolyeah\Skirpsi\Teknikal\fase_1\Suara_untuk_validasi"
    skripsi_dir = Path(__file__).parent.parent
    cfg_path = skripsi_dir / "configs" / "baseline.yaml"
    ckpt_dir = skripsi_dir / "checkpoints"
    results_dir = skripsi_dir / "results"
    results_dir.mkdir(exist_ok=True)
    
    cfg = load_config(str(cfg_path))
    
    print(f"[1/4] Scanning validation directory: {val_dir}")
    file_list = find_audio_files(val_dir)
    print(f"      Total audio files found: {len(file_list)}")
    
    if len(file_list) == 0:
        print("ERROR: No audio files found!")
        return

    # Load trained models
    model_ids = ["B0", "B1", "B2", "B3", "B4", "E4a", "E4b", "E4c", "E4d", "E4e"]
    models = {}
    print(f"[2/4] Loading trained models from {ckpt_dir}...")
    for m_id in model_ids:
        ckpt_path = ckpt_dir / f"{m_id}_seed42.joblib"
        if not ckpt_path.exists():
            print(f"  [WARN] Checkpoint not found: {ckpt_path}")
            continue
        ckpt = joblib.load(ckpt_path)
        models[m_id] = {
            "pipeline": ckpt["model"],
            "features": ckpt["features"]
        }
        print(f"  [LOADED] Model {m_id} ({len(ckpt['features'])} features)")

    # Extract features for all validation files using multiprocessing
    num_workers = min(12, max(1, os.cpu_count() or 4))
    print(f"[3/4] Extracting features from {len(file_list)} files using {num_workers} parallel workers...")
    extracted_data = []
    
    with ProcessPoolExecutor(max_workers=num_workers) as executor:
        futures = {executor.submit(_worker_extract, item, cfg): item for item in file_list}
        for future in tqdm(as_completed(futures), total=len(futures), desc="Extracting features (Parallel)"):
            res = future.result()
            if res is not None:
                extracted_data.append(res)

    df_feats = pd.DataFrame(extracted_data)
    print(f"      Successfully extracted features for {len(df_feats)} / {len(file_list)} files.")

    if len(df_feats) == 0:
        print("ERROR: Feature extraction failed for all files.")
        return

    # Predict with all models
    print(f"[4/4] Evaluating models and generating predictions...")
    df_preds = df_feats[["file_name", "rel_path", "label", "label_str", "category", "n_segments"]].copy()

    metrics_list = []

    for m_id, m_dict in models.items():
        pipeline = m_dict["pipeline"]
        feature_cols = m_dict["features"]
        cal_thresh = CALIBRATED_THRESHOLDS.get(m_id, 0.50)
        
        # Prepare feature matrix X
        X = df_feats[feature_cols].values
        
        # Predict probabilities (col 0 = Real, col 1 = Fake)
        probs = pipeline.predict_proba(X)[:, 1]
        
        # Standard threshold (0.50)
        preds_std = (probs >= 0.50).astype(int)
        
        # Calibrated threshold
        preds_cal = (probs >= cal_thresh).astype(int)
        
        df_preds[f"prob_fake_{m_id}"] = probs.round(4)
        df_preds[f"pred_std_{m_id}"] = np.where(preds_std == 1, "FAKE", "REAL")
        df_preds[f"pred_cal_{m_id}"] = np.where(preds_cal == 1, "FAKE", "REAL")
        df_preds[f"correct_cal_{m_id}"] = (preds_cal == df_preds["label"]).astype(int)
        
        # Calculate summary metrics (Calibrated vs Standard)
        y_true = df_preds["label"].values
        try:
            auc = roc_auc_score(y_true, probs)
        except Exception:
            auc = np.nan
            
        eer, eer_thresh = compute_eer(y_true, probs)
        
        acc_std = accuracy_score(y_true, preds_std)
        acc_cal = accuracy_score(y_true, preds_cal)
        
        rec_real_cal = recall_score(y_true, preds_cal, pos_label=0, zero_division=0)
        rec_fake_cal = recall_score(y_true, preds_cal, pos_label=1, zero_division=0)
        f1_cal = f1_score(y_true, preds_cal, zero_division=0)
        
        metrics_list.append({
            "model": m_id,
            "calibrated_thresh": cal_thresh,
            "auc": round(float(auc), 5),
            "eer": round(float(eer), 5),
            "accuracy_std_0.50": round(float(acc_std), 5),
            "accuracy_calibrated": round(float(acc_cal), 5),
            "recall_real_calibrated": round(float(rec_real_cal), 5),
            "recall_fake_calibrated": round(float(rec_fake_cal), 5),
            "f1_fake_calibrated": round(float(f1_cal), 5)
        })

    # Save outputs to both results/ and C:\Users\alvin\Documents\Coolyeah\Skirpsi\Teknikal\fase_1\hasil_validasi
    hasil_val_dir = Path(r"C:\Users\alvin\Documents\Coolyeah\Skirpsi\Teknikal\fase_1\hasil_validasi")
    hasil_val_dir.mkdir(exist_ok=True, parents=True)
    
    preds_csv1 = results_dir / "validation_external_predictions.csv"
    metrics_csv1 = results_dir / "validation_external_metrics.csv"
    cat_csv1 = results_dir / "validation_external_category_breakdown.csv"

    preds_csv2 = hasil_val_dir / "validation_external_predictions.csv"
    metrics_csv2 = hasil_val_dir / "validation_external_metrics.csv"
    cat_csv2 = hasil_val_dir / "validation_external_category_breakdown.csv"
    
    df_preds.to_csv(preds_csv1, index=False)
    df_preds.to_csv(preds_csv2, index=False)
    
    df_metrics = pd.DataFrame(metrics_list)
    df_metrics.to_csv(metrics_csv1, index=False)
    df_metrics.to_csv(metrics_csv2, index=False)
    
    print("\n" + "="*70)
    print("EVALUASI VALIDASI EKSTERNAL (CALIBRATED THRESHOLD) SELESAI!")
    print("="*70)
    print(f"File Prediksi Per-Utterance : {preds_csv2}")
    print(f"File Metrik Komprehensif    : {metrics_csv2}")
    print("\n--- RINGKASAN METRIK PER-MODEL (SETELAH KALIBRASI THRESHOLD) ---")
    print(df_metrics[["model", "calibrated_thresh", "auc", "accuracy_std_0.50", "accuracy_calibrated", "recall_real_calibrated", "recall_fake_calibrated"]].to_string(index=False))

    # Breakdown per kategori (Calibrated E4a)
    print("\n--- BREAKDOWN AKURASI E4a (CALIBRATED THRESHOLD 0.65) PER KATEGORI ---")
    if "pred_cal_E4a" in df_preds.columns:
        cat_acc = df_preds.groupby(["category", "label_str"])["correct_cal_E4a"].agg(["count", "mean"]).reset_index()
        cat_acc.columns = ["category", "ground_truth", "total_files", "accuracy_calibrated_E4a"]
        cat_acc["accuracy_calibrated_E4a_pct"] = (cat_acc["accuracy_calibrated_E4a"] * 100).round(2).astype(str) + "%"
        print(cat_acc.to_string(index=False))
        
        cat_acc.to_csv(cat_csv1, index=False)
        cat_acc.to_csv(cat_csv2, index=False)
        print(f"\nFile Breakdown Kategori : {cat_csv2}")

if __name__ == "__main__":
    main()
