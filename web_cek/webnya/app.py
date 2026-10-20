import os
import sys
import tempfile
import joblib
import numpy as np
from flask import Flask, request, jsonify, render_template
from pathlib import Path
import io
import base64

try:
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False

# Injeksi Path agar bisa baca library skripsi
# app.py berada di web_cek/webnya
# target: skripsi_residual_modulasi/src
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) # web_cek
SKRIPSI_DIR = os.path.abspath(os.path.join(BASE_DIR, "..", "skripsi_residual_modulasi"))
SRC_DIR = os.path.join(SKRIPSI_DIR, "src")
sys.path.append(SRC_DIR)

from reproducibility import load_config
from extract_features import extract_utterance_features
from residual_features import residual_feature_names
from modulation_features import modulation_feature_names

app = Flask(__name__)

# Konfigurasi sama persis dengan yang dipakai di notebook/skripsi
CONFIG_PATH = os.path.join(SKRIPSI_DIR, "configs", "baseline.yaml")
if os.path.exists(CONFIG_PATH):
    CFG = load_config(CONFIG_PATH)
else:
    CFG = {
        "sample_rate": 16000,
        "segment_seconds": 2.0,
        "hop_seconds": 1.0,
        "mfcc_n": 40,
        "lfcc_n": 40,
        "lpc_frame_ms": 25,
        "lpc_hop_ms": 10,
        "lpc_min_energy": -80.0,
        "envelope_sr": 200,
        "modulation_lowpass_hz": 20,
        "modulation_max_hz": 20,
        "mfcc_n_fft": 512,
        "mfcc_hop_length": 160,
        "mfcc_win_length": 400,
        "lfcc_n_filters": 40,
        "lfcc_fmax": 8000.0,
    }

MODEL_DIR = os.path.join(BASE_DIR, "model")
MODEL_DIR_CHECKPOINTS = os.path.join(SKRIPSI_DIR, "checkpoints")

def resolve_model_path(filename):
    p1 = os.path.join(MODEL_DIR, filename)
    if os.path.exists(p1):
        return p1
    p2 = os.path.join(MODEL_DIR_CHECKPOINTS, filename)
    return p2

AVAILABLE_MODELS = {
    # ─── Model Usulan (Evidence & Fusion) ───
    "e4a": {
        "id": "e4a",
        "name": "🥇 E4a — All Acoustic + Residual Modulation (Terbaik - AUC 79.62%)",
        "path": resolve_model_path("E4a_seed42.joblib"),
        "group": "Model Usulan (Evidence & Fusion)",
        "calibrated_threshold": 0.65,
    },
    "e4c": {
        "id": "e4c",
        "name": "E4c — Acoustic + Residual Stats (AUC 78.96%)",
        "path": resolve_model_path("E4c_seed42.joblib"),
        "group": "Model Usulan (Evidence & Fusion)",
        "calibrated_threshold": 0.65,
    },
    "e4e": {
        "id": "e4e",
        "name": "E4e — All LPC Residual + Modulation (AUC 77.38%)",
        "path": resolve_model_path("E4e_seed42.joblib"),
        "group": "Model Usulan (Evidence & Fusion)",
        "calibrated_threshold": 0.62,
    },
    "e4b": {
        "id": "e4b",
        "name": "E4b — Modulation Features Only (AUC 60.41%)",
        "path": resolve_model_path("E4b_seed42.joblib"),
        "group": "Model Usulan (Evidence & Fusion)",
        "calibrated_threshold": 0.55,
    },
    "e4d": {
        "id": "e4d",
        "name": "E4d — Residual Stats Only (AUC 60.48%)",
        "path": resolve_model_path("E4d_seed42.joblib"),
        "group": "Model Usulan (Evidence & Fusion)",
        "calibrated_threshold": 0.60,
    },
    # ─── Model Baseline ───
    "b4": {
        "id": "b4",
        "name": "B4 — Acoustic Base: MFCC + Chroma + Spectral (AUC 78.93%)",
        "path": resolve_model_path("B4_seed42.joblib"),
        "group": "Model Baseline",
        "calibrated_threshold": 0.55,
    },
    "b1": {
        "id": "b1",
        "name": "B1 — Residual Modulation Spectrum (AUC 76.00%)",
        "path": resolve_model_path("B1_seed42.joblib"),
        "group": "Model Baseline",
        "calibrated_threshold": 0.60,
    },
    "b2": {
        "id": "b2",
        "name": "B2 — LPC Residual + Modulation (AUC 72.85%)",
        "path": resolve_model_path("B2_seed42.joblib"),
        "group": "Model Baseline",
        "calibrated_threshold": 0.60,
    },
    "b0": {
        "id": "b0",
        "name": "B0 — LPC Residual Stats (AUC 72.49%)",
        "path": resolve_model_path("B0_seed42.joblib"),
        "group": "Model Baseline",
        "calibrated_threshold": 0.60,
    },
    "b3": {
        "id": "b3",
        "name": "B3 — Baseline MFCC Standard (AUC 68.95%)",
        "path": resolve_model_path("B3_seed42.joblib"),
        "group": "Model Baseline",
        "calibrated_threshold": 0.50,
    },
}

LOADED_MODELS = {}

def get_model(model_id):
    if model_id not in AVAILABLE_MODELS:
        model_id = "e4a"
        
    if model_id not in LOADED_MODELS:
        path = AVAILABLE_MODELS[model_id]["path"]
        print(f"[MODEL] Loading {model_id} from {path}...")
        if not os.path.exists(path):
            raise FileNotFoundError(f"Model file tidak ditemukan: {path}")
        ckpt = joblib.load(path)
        LOADED_MODELS[model_id] = ckpt
        print(f"[MODEL] Berhasil meload model {model_id}!")
        
    return LOADED_MODELS[model_id], AVAILABLE_MODELS[model_id]

def generate_residual_plot_base64(target_path, cfg):
    if not MATPLOTLIB_AVAILABLE: return None
    import librosa
    from residual_features import residual_from_frame
    try:
        y, sr = librosa.load(target_path, sr=cfg["sample_rate"])
        frame_len = int(sr * 25.0 / 1000)
        
        # Cari frame dengan energi tertinggi (paling tidak senyap)
        if len(y) < frame_len:
            frame = y
        else:
            energies = [np.sum(y[i:i+frame_len]**2) for i in range(0, len(y) - frame_len, frame_len)]
            best_idx = np.argmax(energies) * frame_len
            frame = y[best_idx:best_idx+frame_len]
            
        res = residual_from_frame(frame, order=16)
        if res is None: 
            print("Residual plot: Frame was silent, cannot plot.")
            return None

        plt.figure(figsize=(4, 2), facecolor='none')
        plt.plot(res, color='#60a5fa', linewidth=1.2)
        plt.axis('off')
        plt.margins(0)
        buf = io.BytesIO()
        plt.savefig(buf, format='png', transparent=True, bbox_inches='tight', pad_inches=0)
        plt.close()
        return base64.b64encode(buf.getvalue()).decode('utf-8')
    except Exception as e:
        print(f"Error plot residual: {e}")
        return None

def generate_modulation_plot_base64(target_path, cfg):
    if not MATPLOTLIB_AVAILABLE: return None
    import librosa
    from scipy.signal import hilbert, butter, sosfiltfilt, resample_poly
    from math import gcd
    try:
        y, sr = librosa.load(target_path, sr=cfg["sample_rate"])
        if len(y) < sr * 0.1: # Terlalu pendek
            return None
            
        env = np.abs(hilbert(y.astype(np.float64)))
        sos = butter(4, 40.0, btype="lowpass", fs=sr, output="sos")
        env = sosfiltfilt(sos, env)
        
        envelope_sr = 100
        g = gcd(envelope_sr, sr)
        env = resample_poly(env, up=envelope_sr // g, down=sr // g)
        env = env - env.mean()
        
        win = np.hanning(len(env))
        spec = np.abs(np.fft.rfft(env * win)) ** 2
        freq = np.fft.rfftfreq(len(env), d=1.0 / envelope_sr)
        
        keep = (freq > 0) & (freq <= 20.0)
        freq = freq[keep]
        spec = spec[keep]
        
        if np.sum(spec) == 0:
            return None

        plt.figure(figsize=(4, 2), facecolor='none')
        plt.plot(freq, spec, color='#a78bfa', linewidth=1.5)
        plt.fill_between(freq, spec, color='#a78bfa', alpha=0.3)
        plt.axis('off')
        plt.margins(0)
        buf = io.BytesIO()
        plt.savefig(buf, format='png', transparent=True, bbox_inches='tight', pad_inches=0)
        plt.close()
        return base64.b64encode(buf.getvalue()).decode('utf-8')
    except Exception as e:
        print(f"Error plot modulation: {e}")
        return None

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/models", methods=["GET"])
def get_models():
    models_list = list(AVAILABLE_MODELS.values())
    return jsonify({"status": "success", "models": models_list})

@app.route("/predict", methods=["POST"])
def predict():
    if "file" not in request.files:
        return jsonify({"status": "error", "message": "No file uploaded"}), 400
        
    file = request.files["file"]
    if file.filename == "":
        return jsonify({"status": "error", "message": "Empty filename"}), 400
        
    model_id = request.form.get("model", "b4")
    
    try:
        ckpt, model_info = get_model(model_id)
        pipeline = ckpt["model"]
        feature_cols = ckpt["features"]
        
        temp_dir = os.path.join(os.getcwd(), "temp_uploads")
        os.makedirs(temp_dir, exist_ok=True)
        _, ext = os.path.splitext(file.filename)
        
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=ext, dir=temp_dir)
        temp_file_path = temp_file.name
        temp_file.close()
        file.save(temp_file_path)
        
        VIDEO_EXTENSIONS = {".mp4", ".mov", ".avi", ".mkv", ".webm", ".flv"}
        is_video = ext.lower() in VIDEO_EXTENSIONS
        
        target_path = temp_file_path
        if is_video or ext.lower() == ".mp3":
            from moviepy import AudioFileClip
            temp_wav_path = temp_file_path + ".wav"
            try:
                audio_clip = AudioFileClip(temp_file_path)
                audio_clip.write_audiofile(
                    temp_wav_path, fps=CFG["sample_rate"], nbytes=2, codec="pcm_s16le", logger=None
                )
                audio_clip.close()
                target_path = temp_wav_path
            except Exception as e:
                pass 

        try:
            feat_dict = extract_utterance_features(target_path, CFG, lpc_order=16)
            
            if feat_dict is None:
                raise ValueError("Gagal membaca atau mengekstrak fitur dari audio.")
            
            X = []
            for col in feature_cols:
                if col in feat_dict:
                    X.append(feat_dict[col])
                else:
                    X.append(np.nan)
                    
            X = np.array(X).reshape(1, -1)
            
            probs = pipeline.predict_proba(X)[0]
            p_real = float(probs[0])
            p_fake = float(probs[1])
            
            threshold = model_info.get("calibrated_threshold", 0.50)
            if p_fake >= threshold:
                prediction = "FAKE"
                confidence = p_fake
            else:
                prediction = "REAL"
                confidence = p_real
                
            res_keys = residual_feature_names("16")
            mod_keys = modulation_feature_names()
            
            residual_data = {k: feat_dict[k] for k in res_keys if k in feat_dict}
            modulation_data = {k: feat_dict[k] for k in mod_keys if k in feat_dict}

            # Generate Base64 Images (tanpa menyimpan file ke disk!)
            res_img_b64 = generate_residual_plot_base64(target_path, CFG)
            mod_img_b64 = generate_modulation_plot_base64(target_path, CFG)

            return jsonify({
                "status": "success",
                "prediction": prediction,
                "confidence": confidence,
                "proba_real": p_real,
                "proba_fake": p_fake,
                "model_used": model_info["name"],
                "model_id": model_info["id"],
                "residual_features": residual_data,
                "modulation_features": modulation_data,
                "segments_analyzed": feat_dict.get("n_segments", 1),
                "residual_failure_rate": feat_dict.get("residual_failure_rate", 0.0),
                "residual_image": res_img_b64,
                "modulation_image": mod_img_b64
            })

        finally:
            if os.path.exists(temp_file_path):
                os.remove(temp_file_path)
            if target_path != temp_file_path and os.path.exists(target_path):
                os.remove(target_path)
                
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True, port=5000)