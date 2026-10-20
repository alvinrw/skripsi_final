"""
src/generate_confusion_matrices.py
====================================
Menghasilkan Matriks Konfusi (Confusion Matrix) untuk:
1. Skenario 1: Data Uji Internal (Test Set, N = 8.337 sampel)
2. Skenario 2: Validasi Eksternal (N = 272 sampel, 136 Real : 136 Fake)

Output:
- Tabel CSV ringkasan metrik TP, TN, FP, FN, Akurasi, Sensitivity, Specificity, Precision, F1
- Gambar Heatmap Publikasi 300 DPI:
  * G8_confusion_matrix_internal_test.png (Komparasi Model Utama di Data Internal)
  * G9_confusion_matrix_external_validation.png (Komparasi Model Utama di Validasi Eksternal)
  * CM_E4a_Internal_Test.png (Fokus Model Terbaik E4a)
  * CM_B4_External_Validation.png (Fokus Model Terbaik Eksternal B4)
  * CM_B2_External_Validation.png (Fokus Fusi Spektral Eksternal B2)
"""

import os
import sys
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import confusion_matrix

BASE_DIR = Path(r"C:\Users\alvin\Documents\Coolyeah\Skirpsi\Teknikal\fase_1")
SKRIPSI_DIR = BASE_DIR / "skripsi_residual_modulasi"
RESULTS_DIR = SKRIPSI_DIR / "results"
HASIL_VAL_DIR = BASE_DIR / "hasil_validasi"

OUT_FIG_DIRS = [
    SKRIPSI_DIR / "figures",
    BASE_DIR / "penyelesaian_skripsi" / "figures",
    BASE_DIR / "ringkasan_hasil_skripsi" / "figures"
]

OUT_TBL_DIRS = [
    BASE_DIR / "penyelesaian_skripsi" / "tables",
    BASE_DIR / "ringkasan_hasil_skripsi" / "tables"
]

for d in OUT_FIG_DIRS + OUT_TBL_DIRS:
    d.mkdir(parents=True, exist_ok=True)

plt.rcParams.update({
    "font.sans-serif": "Arial",
    "font.family": "sans-serif",
    "figure.autolayout": True,
    "figure.dpi": 300,
    "savefig.dpi": 300,
})

def save_fig_all(fig, filename):
    for d in OUT_FIG_DIRS:
        out_path = d / filename
        fig.savefig(str(out_path), dpi=300, bbox_inches="tight")
    print(f"  [SAVED FIG] {filename}")
    plt.close(fig)

def save_csv_all(df, filename):
    for d in OUT_TBL_DIRS:
        out_path = d / filename
        df.to_csv(out_path, index=False)
    print(f"  [SAVED CSV] {filename}")

def plot_cm_single(cm, title, filename, labels=["Real", "Fake"]):
    fig, ax = plt.subplots(figsize=(5, 4.2))
    
    # Format annotated text with count and percentage
    total = np.sum(cm)
    group_counts = [f"{v:,}" for v in cm.flatten()]
    group_pcts = [f"({v/total*100:.1f}%)" for v in cm.flatten()]
    box_labels = np.asarray([f"{c}\n{p}" for c, p in zip(group_counts, group_pcts)]).reshape(2, 2)
    
    sns.heatmap(cm, annot=box_labels, fmt="", cmap="Blues", cbar=True,
                xticklabels=labels, yticklabels=labels, ax=ax,
                annot_kws={"size": 12, "fontweight": "bold"},
                linewidths=1.5, linecolor="#cbd5e1")
    
    ax.set_title(title, fontsize=12, fontweight="bold", pad=12, color="#1e293b")
    ax.set_xlabel("Prediksi Model (Predicted Label)", fontsize=10, fontweight="bold", labelpad=8)
    ax.set_ylabel("Kelas Aktual (Actual Ground Truth)", fontsize=10, fontweight="bold", labelpad=8)
    save_fig_all(fig, filename)

def main():
    print("="*70)
    print("GENERATING CONFUSION MATRICES (INTERNAL TEST & EXTERNAL VALIDATION)")
    print("="*70)

    # -------------------------------------------------------------
    # 1. SKENARIO 1: DATA UJI INTERNAL (N = 8,337)
    # -------------------------------------------------------------
    df_utt = pd.read_csv(RESULTS_DIR / "utterance_scores.csv")
    df_test = df_utt[df_utt["split"] == "test"].copy()
    
    metrics_df = pd.read_csv(RESULTS_DIR / "metrics.csv")
    test_metrics = metrics_df[metrics_df["split"] == "test"].set_index("model")
    
    all_models = ["B0", "B1", "B2", "B3", "B4", "E4a", "E4b", "E4c", "E4d", "E4e"]
    
    cm_dict_internal = {}
    rows_internal = []
    
    for m in all_models:
        th = test_metrics.loc[m, "used_threshold"]
        y_true = df_test["label"].values
        y_pred = (df_test[f"score_{m}"].values >= th).astype(int)
        
        cm = confusion_matrix(y_true, y_pred)
        tn, fp, fn, tp = cm.ravel()
        cm_dict_internal[m] = cm
        
        total = len(y_true)
        acc = (tp + tn) / total
        rec_real = tn / (tn + fp) # Specificity
        rec_fake = tp / (tp + fn) # Sensitivity / Recall
        prec_real = tn / (tn + fn) if (tn + fn) > 0 else 0
        prec_fake = tp / (tp + fp) if (tp + fp) > 0 else 0
        f1_fake = 2 * prec_fake * rec_fake / (prec_fake + rec_fake) if (prec_fake + rec_fake) > 0 else 0
        
        rows_internal.append({
            "Model": m,
            "Threshold": round(th, 4),
            "Total Sample": total,
            "TN (Real->Real)": tn,
            "FP (Real->Fake)": fp,
            "FN (Fake->Real)": fn,
            "TP (Fake->Fake)": tp,
            "Akurasi (%)": round(acc * 100, 2),
            "Sensitivitas / Recall Fake (%)": round(rec_fake * 100, 2),
            "Spesifisitas / Recall Real (%)": round(rec_real * 100, 2),
            "Presisi Fake (%)": round(prec_fake * 100, 2),
            "F1-Score Fake": round(f1_fake, 4)
        })
    
    df_cm_internal = pd.DataFrame(rows_internal)
    save_csv_all(df_cm_internal, "Tabel_Confusion_Matrix_Internal_Test.csv")
    
    # Plot Single Fokus E4a (Internal)
    plot_cm_single(cm_dict_internal["E4a"], 
                   "Confusion Matrix E4a (All Acoustic + ResMod)\nData Uji Internal (N = 8,337 | Akurasi: 71.36%)",
                   "CM_E4a_Internal_Test.png")

    # Plot Multi-Grid Skenario 1 (G8: 6 Model Kunci: E4a, B4, B2, B3, E4c, E4e)
    fig, axes = plt.subplots(2, 3, figsize=(14, 9))
    models_g8 = [
        ("E4a", "E4a (Usulan ResMod - Terbaik)", cm_dict_internal["E4a"]),
        ("E4c", "E4c (Acoustic + Residual Stats)", cm_dict_internal["E4c"]),
        ("E4e", "E4e (All LPC Res + Modulation)", cm_dict_internal["E4e"]),
        ("B4", "B4 (Acoustic Base XGBoost)", cm_dict_internal["B4"]),
        ("B2", "B2 (Mel + LFCC SVM)", cm_dict_internal["B2"]),
        ("B3", "B3 (Baseline MFCC RF)", cm_dict_internal["B3"]),
    ]
    
    for ax, (m_id, m_name, cm) in zip(axes.flatten(), models_g8):
        total = np.sum(cm)
        counts = [f"{v:,}" for v in cm.flatten()]
        pcts = [f"({v/total*100:.1f}%)" for v in cm.flatten()]
        annot = np.asarray([f"{c}\n{p}" for c, p in zip(counts, pcts)]).reshape(2, 2)
        
        acc = (cm[0, 0] + cm[1, 1]) / total * 100
        sns.heatmap(cm, annot=annot, fmt="", cmap="Blues", cbar=False,
                    xticklabels=["Real", "Fake"], yticklabels=["Real", "Fake"],
                    annot_kws={"size": 11, "fontweight": "bold"},
                    linewidths=1.2, linecolor="#cbd5e1", ax=ax)
        ax.set_title(f"{m_name}\nAkurasi: {acc:.2f}%", fontsize=11, fontweight="bold", pad=8)
        ax.set_xlabel("Prediksi", fontsize=9, fontweight="bold")
        ax.set_ylabel("Aktual", fontsize=9, fontweight="bold")
    
    fig.suptitle("G8: Perbandingan Matriks Konfusi Model pada Data Uji Internal (N = 8.337)",
                 fontsize=14, fontweight="bold", y=1.02, color="#0f172a")
    save_fig_all(fig, "G8_confusion_matrix_internal_test.png")

    # -------------------------------------------------------------
    # 2. SKENARIO 2: VALIDASI EKSTERNAL (N = 272)
    # -------------------------------------------------------------
    df_ext = pd.read_csv(HASIL_VAL_DIR / "validation_external_predictions.csv")
    cm_dict_external = {}
    rows_external = []
    
    for m in all_models:
        y_true = df_ext["label"].values # 0=real, 1=fake
        y_pred = (df_ext[f"pred_cal_{m}"] == "FAKE").astype(int)
        
        cm = confusion_matrix(y_true, y_pred)
        tn, fp, fn, tp = cm.ravel()
        cm_dict_external[m] = cm
        
        total = len(y_true)
        acc = (tp + tn) / total
        rec_real = tn / (tn + fp)
        rec_fake = tp / (tp + fn)
        prec_real = tn / (tn + fn) if (tn + fn) > 0 else 0
        prec_fake = tp / (tp + fp) if (tp + fp) > 0 else 0
        f1_fake = 2 * prec_fake * rec_fake / (prec_fake + rec_fake) if (prec_fake + rec_fake) > 0 else 0
        
        rows_external.append({
            "Model": m,
            "Total Sample": total,
            "TN (Real->Real)": tn,
            "FP (Real->Fake)": fp,
            "FN (Fake->Real)": fn,
            "TP (Fake->Fake)": tp,
            "Akurasi (%)": round(acc * 100, 2),
            "Recall Fake / Sensitivitas (%)": round(rec_fake * 100, 2),
            "Recall Real / Spesifisitas (%)": round(rec_real * 100, 2),
            "Presisi Fake (%)": round(prec_fake * 100, 2),
            "F1-Score Fake": round(f1_fake, 4)
        })
    
    df_cm_external = pd.DataFrame(rows_external)
    save_csv_all(df_cm_external, "Tabel_Confusion_Matrix_Validasi_Eksternal.csv")

    # Plot Single Fokus B4 (Model Terbaik Eksternal) & B2
    plot_cm_single(cm_dict_external["B4"],
                   "Confusion Matrix B4 (Acoustic Base XGBoost)\nValidasi Eksternal (N = 272 | Akurasi: 67.65%)",
                   "CM_B4_External_Validation.png")
    plot_cm_single(cm_dict_external["B2"],
                   "Confusion Matrix B2 (Mel + LFCC SVM)\nValidasi Eksternal (N = 272 | AUC: 77.20% | Akurasi: 65.07%)",
                   "CM_B2_External_Validation.png")
    plot_cm_single(cm_dict_external["E4a"],
                   "Confusion Matrix E4a (All Acoustic + ResMod)\nValidasi Eksternal (N = 272 | Akurasi: 62.50%)",
                   "CM_E4a_External_Validation.png")

    # Plot Multi-Grid Skenario 2 (G9: 6 Model Kunci: B4, B2, E4e, B0, E4a, B3)
    fig, axes = plt.subplots(2, 3, figsize=(14, 9))
    models_g9 = [
        ("B4", "B4 (Acoustic Base XGBoost - Top Acc)", cm_dict_external["B4"]),
        ("B2", "B2 (Mel + LFCC SVM - Top AUC 77.2%)", cm_dict_external["B2"]),
        ("E4e", "E4e (All LPC Res + Mod - Top Robust)", cm_dict_external["E4e"]),
        ("B0", "B0 (LFCC SVM)", cm_dict_external["B0"]),
        ("E4a", "E4a (Usulan ResMod SVM)", cm_dict_external["E4a"]),
        ("B3", "B3 (Baseline MFCC RF)", cm_dict_external["B3"]),
    ]
    
    for ax, (m_id, m_name, cm) in zip(axes.flatten(), models_g9):
        total = np.sum(cm)
        counts = [f"{v:,}" for v in cm.flatten()]
        pcts = [f"({v/total*100:.1f}%)" for v in cm.flatten()]
        annot = np.asarray([f"{c}\n{p}" for c, p in zip(counts, pcts)]).reshape(2, 2)
        
        acc = (cm[0, 0] + cm[1, 1]) / total * 100
        sns.heatmap(cm, annot=annot, fmt="", cmap="Purples", cbar=False,
                    xticklabels=["Real", "Fake"], yticklabels=["Real", "Fake"],
                    annot_kws={"size": 11, "fontweight": "bold"},
                    linewidths=1.2, linecolor="#cbd5e1", ax=ax)
        ax.set_title(f"{m_name}\nAkurasi: {acc:.2f}%", fontsize=11, fontweight="bold", pad=8)
        ax.set_xlabel("Prediksi", fontsize=9, fontweight="bold")
        ax.set_ylabel("Aktual", fontsize=9, fontweight="bold")
        
    fig.suptitle("G9: Perbandingan Matriks Konfusi pada Validasi Eksternal (N = 272 Seimbang 1:1)",
                 fontsize=14, fontweight="bold", y=1.02, color="#0f172a")
    save_fig_all(fig, "G9_confusion_matrix_external_validation.png")

    print("\n" + "="*70)
    print("SELURUH CONFUSION MATRIX SELESAI DIGENERATE DENGAN SUKSES!")
    print("="*70)

if __name__ == "__main__":
    main()
