import os
import sys
import numpy as np

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SKRIPSI_DIR = os.path.abspath(os.path.join(BASE_DIR, "..", "skripsi_residual_modulasi"))
SRC_DIR = os.path.join(SKRIPSI_DIR, "src")
sys.path.append(SRC_DIR)

from reproducibility import load_config
try:
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    print("Matplotlib available.")
except Exception as e:
    print("Matplotlib failed:", e)

cfg = load_config(os.path.join(SKRIPSI_DIR, "configs", "baseline.yaml"))

def test_plot():
    # Buat dummy audio (sine wave 1000 Hz, 2 detik @ 16kHz)
    sr = cfg["sample_rate"]
    t = np.linspace(0, 2, 2 * sr, endpoint=False)
    y = np.sin(2 * np.pi * 1000 * t).astype(np.float32)
    
    from residual_features import residual_from_frame
    import io, base64
    try:
        frame_len = int(sr * 25.0 / 1000)
        
        # Cari frame dengan energi tertinggi
        if len(y) < frame_len:
            frame = y
        else:
            energies = [np.sum(y[i:i+frame_len]**2) for i in range(0, len(y) - frame_len, frame_len)]
            best_idx = np.argmax(energies) * frame_len
            frame = y[best_idx:best_idx+frame_len]
            
        res = residual_from_frame(frame, order=16)
        if res is None: 
            print("res is none")
            return None

        plt.figure(figsize=(4, 2), facecolor='none')
        plt.plot(res, color='#60a5fa', linewidth=1.2)
        plt.axis('off')
        plt.margins(0)
        buf = io.BytesIO()
        plt.savefig(buf, format='png', transparent=True, bbox_inches='tight', pad_inches=0)
        plt.close()
        b64 = base64.b64encode(buf.getvalue()).decode('utf-8')
        print("B64 size:", len(b64))
        return b64
    except Exception as e:
        print(f"Error plot residual: {e}")
        return None

test_plot()
