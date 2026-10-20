import os
import sys
import tarfile
import urllib.request
from pathlib import Path
from tqdm import tqdm

class DownloadProgressBar(tqdm):
    def update_to(self, b=1, bsize=1, tsize=None):
        if tsize is not None:
            self.total = tsize
        self.update(b * bsize - self.n)

def download_file(url, target_path):
    print(f"[download] Mengunduh: {url}")
    with DownloadProgressBar(unit='B', unit_scale=True, miniters=1, desc=Path(target_path).name) as t:
        urllib.request.urlretrieve(url, filename=target_path, reporthook=t.update_to)

def main():
    target_dir = Path("..") / "Folder_dataset" / "Suara_real" / "downloaded_real"
    target_dir.mkdir(parents=True, exist_ok=True)
    
    # 2 Subset LibriSpeech (dev-clean & test-clean) -> Total ~10.8 Jam audio real manusia
    urls = [
        "http://www.openslr.org/resources/12/dev-clean.tar.gz",
        "http://www.openslr.org/resources/12/test-clean.tar.gz"
    ]
    
    temp_dir = Path("scratch")
    temp_dir.mkdir(parents=True, exist_ok=True)
    
    for url in urls:
        filename = url.split("/")[-1]
        tar_path = temp_dir / filename
        
        # 1. Download
        if not tar_path.exists() or tar_path.stat().st_size < 100000000:
            download_file(url, tar_path)
        else:
            print(f"[skip] File {filename} sudah terunduh.")
            
        # 2. Extract
        print(f"[extract] Ekstraksi {filename} ke {target_dir}...")
        with tarfile.open(tar_path, "r:gz") as tar:
            tar.extractall(path=target_dir)
        print(f"[OK] Selesai ekstrak {filename}")
        
    print("\n[SUCCESS] Seluruh 10+ jam audio real manusia berhasil diunduh & diekstrak!")

if __name__ == "__main__":
    main()
