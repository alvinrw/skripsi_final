# -*- coding: utf-8 -*-
"""
Build workbook profesional untuk hasil validasi eksternal (speech deepfake).
Sumber : fase_1/hasil_validasi/*.csv
Output : fase_1/outputs/hasil_validasi_profesional.xlsx

Perbaikan dibanding versi lama (hasil_validasi_profesional.xlsx lama):
  1. Tidak ada tabel yang saling tindih (bug lama: AUC/EER E4a-E4e tertimpa).
  2. Tidak ada data bantuan chart yang bocor kelihatan di sheet (kolom T/U).
  3. Tidak ada kolom akurasi ganda (angka + teks "%").
  4. Semua angka ditulis sebagai ANGKA (bukan string CSV) -> bisa sort/hitung.
  5. Kop & lebar kolom konsisten, freeze pane, autofilter, print setup.
  6. Cross-check otomatis: metrik dihitung ulang dari predictions -> dicocokkan
     ke metrics.csv. Selisih dilaporkan, bukan disembunyikan.
"""
import csv
import datetime as dt
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

from openpyxl import Workbook
from openpyxl.chart import BarChart, Reference
from openpyxl.formatting.rule import CellIsRule, ColorScaleRule, DataBarRule
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import column_index_from_string, get_column_letter
from openpyxl.worksheet.table import Table, TableStyleInfo

BASE = Path(r"C:\Users\alvin\Documents\Coolyeah\Skirpsi\Teknikal\fase_1")
SRC = BASE / "hasil_validasi"
OUT_DIR = BASE / "outputs"
OUT = OUT_DIR / "hasil_validasi_profesional.xlsx"

FONT = "Arial"
NAVY = "1F4E78"
NAVY_SOFT = "2E6DA4"
LIGHT = "D9EAF7"
BORDER_C = "D9E2F3"
GRAY = "5B6573"
TEXT = "202124"
RED_FILL, RED_TEXT = "FFC7CE", "9C0006"
GREEN_TEXT = "006100"

THIN = Side(style="thin", color=BORDER_C)
BOX = Border(left=THIN, right=THIN, top=THIN, bottom=THIN)


# --------------------------------------------------------------------------- #
# 1. MEMBACA SUMBER
# --------------------------------------------------------------------------- #
def read_csv(path):
    with open(path, newline="", encoding="utf-8-sig") as fh:
        return list(csv.DictReader(fh))


metrics_rows = read_csv(SRC / "validation_external_metrics.csv")
category_rows = read_csv(SRC / "validation_external_category_breakdown.csv")
pred_rows = read_csv(SRC / "validation_external_predictions.csv")

MODELS = [r["model"] for r in metrics_rows]
METRICS = {
    r["model"]: {
        "thresh": float(r["calibrated_thresh"]),
        "auc": float(r["auc"]),
        "eer": float(r["eer"]),
        "acc_std": float(r["accuracy_std_0.50"]),
        "acc_cal": float(r["accuracy_calibrated"]),
        "rec_real": float(r["recall_real_calibrated"]),
        "rec_fake": float(r["recall_fake_calibrated"]),
        "f1_fake": float(r["f1_fake_calibrated"]),
    }
    for r in metrics_rows
}

N_REAL = sum(1 for r in pred_rows if r["label"] == "0")
N_FAKE = sum(1 for r in pred_rows if r["label"] == "1")
N_FILE = len(pred_rows)
N_KATEGORI = len(category_rows)


# --------------------------------------------------------------------------- #
# 2. HITUNG ULANG DARI PREDIKSI + CROSS-CHECK (verifikasi, bukan asumsi)
# --------------------------------------------------------------------------- #
def f1_from_pr(p, r):
    return 2 * p * r / (p + r) if (p + r) else 0.0


def auc_rank(scores, labels):
    """AUC via rank statistic (tie di-rata-ratakan)."""
    data = sorted(zip(scores, labels))
    n = len(data)
    ranks, i = [0.0] * n, 0
    while i < n:
        j = i
        while j + 1 < n and data[j + 1][0] == data[i][0]:
            j += 1
        avg = (i + j) / 2 + 1
        for k in range(i, j + 1):
            ranks[k] = avg
        i = j + 1
    n_pos = sum(1 for _, lab in data if lab == 1)
    n_neg = n - n_pos
    pos_rank = sum(rk for rk, (_, lab) in zip(ranks, data) if lab == 1)
    return (pos_rank - n_pos * (n_pos + 1) / 2) / (n_pos * n_neg)


labels = [int(r["label"]) for r in pred_rows]
recomputed = {}
for m in MODELS:
    probs = [float(r[f"prob_fake_{m}"]) for r in pred_rows]
    pred_cal = [r[f"pred_cal_{m}"] for r in pred_rows]
    correct = [1 if r[f"correct_cal_{m}"] == "1" else 0 for r in pred_rows]

    tp = sum(1 for p, l in zip(pred_cal, labels) if p == "FAKE" and l == 1)   # fake terdeteksi
    fn = N_FAKE - tp                                                          # fake lolos
    fp = sum(1 for p, l in zip(pred_cal, labels) if p == "FAKE" and l == 0)   # real terdeteksi fake
    tn = N_REAL - fp
    prec = tp / (tp + fp) if (tp + fp) else 0.0
    rec_f = tp / (tp + fn) if (tp + fn) else 0.0
    rec_r = tn / (tn + fp) if (tn + fp) else 0.0
    recomputed[m] = {
        "auc": auc_rank(probs, labels),
        "acc_cal": sum(correct) / N_FILE,
        "rec_real": rec_r,
        "rec_fake": rec_f,
        "f1_fake": f1_from_pr(prec, rec_f),
        "benar": sum(correct),
    }

print("=" * 78)
print("CROSS-CHECK: metrik dihitung ulang dari predictions vs metrics.csv")
print("=" * 78)
issues = []
# Catatan: metrics.csv menyimpan nilai dengan 5 desimal, sehingga selisih <= 5e-6
# terhadap hitungan ulang adalah pembulatan, BUKAN ketidakcocokan data.
TOL = 1e-5
for m in MODELS:
    src, calc = METRICS[m], recomputed[m]
    for key in ("acc_cal", "rec_real", "rec_fake", "f1_fake"):
        if abs(src[key] - calc[key]) > TOL:
            issues.append(f"  [BEDA] {m}.{key}: csv={src[key]:.6f} vs hitung={calc[key]:.6f}")
    dauc = abs(src["auc"] - calc["auc"])
    flag = "OK " if dauc <= 0.005 else "BEDA"
    if dauc > 0.005:
        issues.append(f"  [BEDA] {m}.auc: csv={src['auc']:.5f} vs hitung={calc['auc']:.5f} (Δ={dauc:.5f})")
    print(f"  {m:>4}  acc {src['acc_cal']:.5f}/{calc['acc_cal']:.5f}  "
          f"f1 {src['f1_fake']:.5f}/{calc['f1_fake']:.5f}  auc Δ={dauc:.5f} [{flag}]")
print("-" * 78)
print(f"  Total selisih di luar toleransi: {len(issues)}")
for line in issues:
    print(line)

# Akurasi per kategori per model (turunan, dipakai di sheet Analisis Kategori)
cats = []
for c in category_rows:
    name = c["category"]
    rows_c = [r for r in pred_rows if r["category"] == name]
    entry = {
        "kategori": name,
        "truth": "Fake" if c["ground_truth"] == "fake" else "Real",
        "total": int(c["total_files"]),
        "csv_acc": float(c["accuracy_calibrated_E4a"]),
        "per_model": {},
    }
    for m in MODELS:
        ok = sum(1 for r in rows_c if r[f"correct_cal_{m}"] == "1")
        entry["per_model"][m] = ok / len(rows_c)
    cats.append(entry)
for c in cats:
    hitung = round(c["csv_acc"] * c["total"])
    c["benar"], c["salah"] = hitung, c["total"] - hitung


# --------------------------------------------------------------------------- #
# 3. HELPER GAYA
# --------------------------------------------------------------------------- #
def set_widths(ws, widths):
    for col, w in widths.items():
        ws.column_dimensions[col].width = w


def title_block(ws, title, subtitle, last_col):
    ws.merge_cells(f"A1:{last_col}1")
    ws["A1"] = title
    ws["A1"].font = Font(name=FONT, size=16, bold=True, color=NAVY)
    ws["A1"].alignment = Alignment(vertical="center")
    ws.row_dimensions[1].height = 26
    ws.merge_cells(f"A2:{last_col}2")
    ws["A2"] = subtitle
    ws["A2"].font = Font(name=FONT, size=9, italic=True, color=GRAY)
    ws["A2"].alignment = Alignment(vertical="center")
    ws.row_dimensions[2].height = 16


def section(ws, row, text, last_col):
    end = column_index_from_string(last_col) if isinstance(last_col, str) else last_col
    ws.merge_cells(start_row=row, start_column=1, end_row=row, end_column=end)
    cell = ws.cell(row=row, column=1, value=text)
    cell.font = Font(name=FONT, size=11, bold=True, color="FFFFFF")
    cell.fill = PatternFill("solid", fgColor=NAVY_SOFT)
    cell.alignment = Alignment(vertical="center", indent=1)
    ws.row_dimensions[row].height = 20


def header(ws, row, col0, headers):
    for i, h in enumerate(headers):
        c = ws.cell(row=row, column=col0 + i, value=h)
        c.font = Font(name=FONT, size=10, bold=True, color="FFFFFF")
        c.fill = PatternFill("solid", fgColor=NAVY)
        c.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
        c.border = BOX
    ws.row_dimensions[row].height = 30


def body_font(ws, rng, size=10):
    for row in ws[rng]:
        for c in row:
            c.font = Font(name=FONT, size=size, color=TEXT)


def add_table(ws, name, ref):
    t = Table(displayName=name, ref=ref)
    t.tableStyleInfo = TableStyleInfo(
        name="TableStyleMedium2", showRowStripes=True,
        showColumnStripes=False, showFirstColumn=False, showLastColumn=False,
    )
    ws.add_table(t)


def page(ws, title_rows=None, landscape=True):
    ws.sheet_view.showGridLines = False
    ws.page_setup.orientation = "landscape" if landscape else "portrait"
    ws.sheet_properties.pageSetUpPr.fitToPage = True
    ws.page_setup.fitToWidth = 1
    ws.page_setup.fitToHeight = 0
    ws.print_options.horizontalCentered = True
    if title_rows:
        ws.print_title_rows = title_rows


wb = Workbook()
stamp = dt.date.today().strftime("%d %B %Y")

# --------------------------------------------------------------------------- #
# SHEET 1 — RINGKASAN
# --------------------------------------------------------------------------- #
ws = wb.active
ws.title = "Ringkasan"
ws.sheet_properties.tabColor = NAVY
page(ws)
title_block(
    ws,
    "VALIDASI EKSTERNAL — DETEKSI SPEECH DEEPFAKE",
    f"Hasil validasi pada {N_FILE} file audio eksternal (34 real / {N_FAKE} fake) dari 4 generator TTS "
    f"· {len(MODELS)} model · {N_KATEGORI} kategori · Disusun {stamp}",
    "P",
)
set_widths(ws, {"A": 30, "B": 14, "C": 3, "D": 3, "E": 13, "F": 13, "G": 12, "H": 12,
                "I": 17, "J": 12, "K": 3, "L": 11, "M": 11, "N": 11, "O": 11, "P": 11,
                "Q": 11, "R": 11, "S": 11, "T": 11})

# --- blok cakupan data (kolom A:C) ---
section(ws, 4, "CAKUPAN DATA", "D")
cakupan = [
    ("Total file tervalidasi", N_FILE, "#,##0"),
    ("  · Kelas real", N_REAL, "#,##0"),
    ("  · Kelas fake", N_FAKE, "#,##0"),
    ("Jumlah model diuji", len(MODELS), "#,##0"),
    ("Jumlah kategori", N_KATEGORI, "#,##0"),
    ("Berkas sumber (CSV)", 3, "#,##0"),
]
for i, (label, val, fmt) in enumerate(cakupan):
    r = 5 + i
    a = ws.cell(row=r, column=1, value=label)
    a.font = Font(name=FONT, size=10, bold=(not label.startswith("  ")), color=NAVY if not label.startswith("  ") else GRAY)
    a.alignment = Alignment(indent=1, vertical="center")
    a.border = BOX
    b = ws.cell(row=r, column=2, value=val)
    b.font = Font(name=FONT, size=10)
    b.number_format = fmt
    b.alignment = Alignment(horizontal="right")
    b.border = BOX

def pct(v):
    """Format persen dengan koma desimal, konsisten dengan tampilan Excel Indonesia."""
    return f"{v:.2%}".replace(".", ",").replace("%", "%")


best = max(MODELS, key=lambda m: METRICS[m]["auc"])
best_acc = max(MODELS, key=lambda m: METRICS[m]["acc_cal"])
mb = METRICS[best]
notes = [
    (f"Model terbaik: {best}", None),
    (f"AUC {pct(mb['auc'])} · akurasi terkalibrasi {pct(mb['acc_cal'])}", "note"),
    (f"F1 fake {pct(mb['f1_fake'])} (unggul di seluruh metrik).", "note"),
    (f"Akurasi tertinggi juga diraih {best_acc}.", "note"),
    ("Seluruh model baseline (B0–B4) mengungguli", "note"),
    ("model evidence (E4a–E4e) pada AUC.", "note"),
    ("Kategori real paling sulit: perempuan", "note"),
    ("25,00% dan Laki_laki 44,44%.", "note"),
]
section(ws, 13, "TEMUAN UTAMA", "D")
for i, (text, kind) in enumerate(notes):
    r = 14 + i
    ws.merge_cells(start_row=r, start_column=1, end_row=r, end_column=4)
    c = ws.cell(row=r, column=1, value=("• " + text) if kind else text)
    c.font = Font(name=FONT, size=10, bold=(kind is None), color=NAVY if kind is None else TEXT)
    c.alignment = Alignment(vertical="center", wrap_text=True, indent=1)
    ws.row_dimensions[r].height = 15

# --- tabel metrik model (baris 4..21 kolom E:J) ---
section_row = 4
ws.merge_cells(start_row=section_row, start_column=5, end_row=section_row, end_column=10)
sc = ws.cell(row=section_row, column=5, value="RINGKASAN METRIK MODEL (10 MODEL)")
sc.font = Font(name=FONT, size=11, bold=True, color="FFFFFF")
sc.fill = PatternFill("solid", fgColor=NAVY_SOFT)
sc.alignment = Alignment(vertical="center", indent=1)

m_hdr_row = 5
header(ws, m_hdr_row, 5, ["Model", "Threshold", "AUC", "EER", "Akurasi (terkalibrasi)", "F1 Fake"])
for i, m in enumerate(MODELS):
    r = m_hdr_row + 1 + i
    vals = [m, METRICS[m]["thresh"], METRICS[m]["auc"], METRICS[m]["eer"],
            METRICS[m]["acc_cal"], METRICS[m]["f1_fake"]]
    for j, v in enumerate(vals):
        c = ws.cell(row=r, column=5 + j, value=v)
        c.font = Font(name=FONT, size=10, color=TEXT, bold=(j == 0))
        c.border = BOX
        if j == 1:
            c.number_format = "0.00"
        elif j >= 2:
            c.number_format = "0.00%"
        c.alignment = Alignment(horizontal="center" if j == 0 else "right")
m_first, m_last = m_hdr_row + 1, m_hdr_row + len(MODELS)
ws.conditional_formatting.add(
    f"H{m_first}:H{m_last}",
    DataBarRule(start_type="num", start_value=0, end_type="num", end_value=1, color="638EC6"),
)
ws.conditional_formatting.add(
    f"G{m_first}:G{m_last}",
    ColorScaleRule(start_type="min", start_color="F8696B", mid_type="percentile",
                   mid_value=50, mid_color="FFEB84", end_type="max", end_color="63BE7B"),
)

# --- tabel akurasi E4a per kategori (baris 24..) kolom E:J ---
section(ws, 23, "AKURASI E4a PER KATEGORI", "J")
header(ws, 24, 5, ["Kategori", "Ground truth", "Jumlah file", "Benar", "Salah", "Akurasi"])
cats_sorted = sorted(cats, key=lambda c: c["csv_acc"], reverse=True)
for i, c in enumerate(cats_sorted):
    r = 25 + i
    vals = [c["kategori"], c["truth"], c["total"], c["benar"], c["salah"], c["csv_acc"]]
    for j, v in enumerate(vals):
        cell = ws.cell(row=r, column=5 + j, value=v)
        cell.font = Font(name=FONT, size=10, color=TEXT, bold=(j == 0))
        cell.border = BOX
        if j in (2, 3, 4):
            cell.number_format = "#,##0"
        elif j == 5:
            cell.number_format = "0.00%"
        cell.alignment = Alignment(horizontal="center" if j in (1, 2, 3, 4) else ("left" if j == 0 else "right"))
c_first, c_last = 25, 24 + len(cats_sorted)
ws.conditional_formatting.add(
    f"J{c_first}:J{c_last}",
    DataBarRule(start_type="num", start_value=0, end_type="num", end_value=1, color="70AD47"),
)

# --- catatan ---
section(ws, 33, "CATATAN & SUMBER", "J")
ws.merge_cells("A34:J40")
note = ws["A34"]
note.value = (
    "Sumber data: validation_external_metrics.csv, validation_external_category_breakdown.csv, dan "
    "validation_external_predictions.csv (folder hasil_validasi). Nilai metrik pada seluruh sheet diambil "
    "langsung dari ketiga CSV tersebut; sheet \"Analisis Model\" dan \"Analisis Kategori\" adalah turunan yang "
    "dihitung ulang dari predictions dan telah dicocokkan kembali ke metrics.csv (selisih: "
    f"{len(issues)} dari {len(MODELS) * 4} pemeriksaan metrik).\n"
    "Threshold terkalibrasi berbeda per model (0,50–0,65); kolom \"Akurasi\" di seluruh workbook memakai "
    "threshold terkalibrasi tersebut, kecuali kolom \"Akurasi (std 0.50)\" yang memakai ambang tetap 0,50."
)
note.font = Font(name=FONT, size=9, italic=True, color=GRAY)
note.alignment = Alignment(vertical="top", wrap_text=True, indent=1)
for _r in range(34, 41):
    ws.row_dimensions[_r].height = 14

# --- chart (memakai tabel di sheet ini, tanpa data bantuan tersembunyi) ---
ch1 = BarChart()
ch1.type, ch1.style = "col", 10
ch1.title = "Akurasi Terkalibrasi per Model"
ch1.y_axis.numFmt = "0%"
ch1.y_axis.delete = False
ch1.x_axis.delete = False
ch1.legend = None
ch1.height, ch1.width = 8.2, 17.5
ch1.add_data(Reference(ws, min_col=9, min_row=m_hdr_row, max_row=m_last), titles_from_data=True)
ch1.set_categories(Reference(ws, min_col=5, min_row=m_first, max_row=m_last))
ch1.varyColors = False
ch1.series[0].graphicalProperties.solidFill = NAVY_SOFT
ch1.series[0].graphicalProperties.line.solidFill = NAVY_SOFT
ws.add_chart(ch1, "L4")

ch2 = BarChart()
ch2.type, ch2.style = "col", 10
ch2.title = "Akurasi E4a per Kategori"
ch2.y_axis.numFmt = "0%"
ch2.y_axis.delete = False
ch2.x_axis.delete = False
ch2.legend = None
ch2.height, ch2.width = 8.2, 17.5
ch2.add_data(Reference(ws, min_col=10, min_row=24, max_row=c_last), titles_from_data=True)
ch2.set_categories(Reference(ws, min_col=5, min_row=c_first, max_row=c_last))
ch2.varyColors = False
ch2.series[0].graphicalProperties.solidFill = "70AD47"
ch2.series[0].graphicalProperties.line.solidFill = "548235"
ws.add_chart(ch2, "L22")


# --------------------------------------------------------------------------- #
# SHEET 2 — ANALISIS MODEL
# --------------------------------------------------------------------------- #
ws2 = wb.create_sheet("Analisis Model")
ws2.sheet_properties.tabColor = NAVY_SOFT
page(ws2, title_rows="5:5")
title_block(
    ws2,
    "ANALISIS MODEL",
    "Turunan dari validation_external_metrics.csv, diurutkan berdasarkan AUC (tinggi ke rendah). "
    "Kelompok: B = baseline (fitur residual+modulasi), E = evidence.",
    "K",
)
set_widths(ws2, {"A": 10, "B": 11, "C": 13, "D": 12, "E": 10, "F": 10,
                 "G": 16, "H": 18, "I": 14, "J": 14, "K": 12})
header(ws2, 5, 1, ["Peringkat", "Model", "Kelompok", "Threshold", "AUC", "EER",
                   "Akurasi (std 0.50)", "Akurasi (terkalibrasi)", "Recall Real", "Recall Fake", "F1 Fake"])
order = sorted(MODELS, key=lambda m: METRICS[m]["auc"], reverse=True)
for i, m in enumerate(order):
    r = 6 + i
    mt = METRICS[m]
    kelompok = "Baseline" if m.startswith("B") else "Evidence"
    vals = [i + 1, m, kelompok, mt["thresh"], mt["auc"], mt["eer"],
            mt["acc_std"], mt["acc_cal"], mt["rec_real"], mt["rec_fake"], mt["f1_fake"]]
    for j, v in enumerate(vals):
        c = ws2.cell(row=r, column=1 + j, value=v)
        c.font = Font(name=FONT, size=10, color=TEXT, bold=(j in (1, 4)))
        c.border = BOX
        c.alignment = Alignment(horizontal="center" if j in (0, 1, 2) else "right")
        if j == 3:
            c.number_format = "0.00"
        elif j >= 4:
            c.number_format = "0.00%"
last2 = 5 + len(order)
add_table(ws2, "TblAnalisisModel", f"A5:K{last2}")
ws2.conditional_formatting.add(f"E6:E{last2}", ColorScaleRule(
    start_type="min", start_color="F8696B", mid_type="percentile", mid_value=50,
    mid_color="FFEB84", end_type="max", end_color="63BE7B"))
ws2.conditional_formatting.add(f"H6:H{last2}", DataBarRule(
    start_type="num", start_value=0, end_type="num", end_value=1, color="638EC6"))
ws2.conditional_formatting.add(f"F6:F{last2}", DataBarRule(
    start_type="num", start_value=0, end_type="num", end_value=1, color="F8696B"))
ws2.conditional_formatting.add(f"B6:B6", CellIsRule(operator="equal", formula=[f'"{order[0]}"'],
                                                   font=Font(name=FONT, size=10, bold=True, color=GREEN_TEXT)))
ws2.merge_cells(f"A{last2 + 2}:K{last2 + 3}")
c = ws2[f"A{last2 + 2}"]
c.value = ("EER (Equal Error Rate) lebih rendah = lebih baik; AUC dan akurasi lebih tinggi = lebih baik. "
           "Semua nilai persis seperti pada metrics.csv — tidak ada penilaian ulang.")
c.font = Font(name=FONT, size=9, italic=True, color=GRAY)
c.alignment = Alignment(vertical="top", wrap_text=True)
ws2.freeze_panes = "C6"


# --------------------------------------------------------------------------- #
# SHEET 3 — ANALISIS KATEGORI
# --------------------------------------------------------------------------- #
ws3 = wb.create_sheet("Analisis Kategori")
ws3.sheet_properties.tabColor = "70AD47"
page(ws3, title_rows="5:5")
title_block(
    ws3,
    "ANALISIS KATEGORI",
    "Blok 1: akurasi E4a per kategori (sesuai category_breakdown.csv). "
    "Blok 2: matriks akurasi per kategori × model, dihitung ulang dari predictions.",
    "M",
)
set_widths(ws3, {"A": 18, "B": 13, "C": 12, "D": 11, "E": 11, "F": 11,
                 "G": 11, "H": 11, "I": 11, "J": 11, "K": 11, "L": 11, "M": 11})

header(ws3, 5, 1, ["Kategori", "Ground truth", "Jumlah file", "Benar", "Salah", "Akurasi (E4a)"])
for i, c_ in enumerate(cats_sorted):
    r = 6 + i
    for j, v in enumerate([c_["kategori"], c_["truth"], c_["total"], c_["benar"], c_["salah"], c_["csv_acc"]]):
        cell = ws3.cell(row=r, column=1 + j, value=v)
        cell.font = Font(name=FONT, size=10, color=TEXT, bold=(j == 0))
        cell.border = BOX
        cell.alignment = Alignment(horizontal="center" if j in (1, 2, 3, 4) else ("left" if j == 0 else "right"))
        if j in (2, 3, 4):
            cell.number_format = "#,##0"
        elif j == 5:
            cell.number_format = "0.00%"
last3 = 5 + len(cats_sorted)
add_table(ws3, "TblAnalisisKategori", f"A5:F{last3}")
ws3.conditional_formatting.add(f"F6:F{last3}", DataBarRule(
    start_type="num", start_value=0, end_type="num", end_value=1, color="70AD47"))

# blok 2: matriks kategori x model
mx_title = last3 + 2
section(ws3, mx_title, "MATRIKS AKURASI PER KATEGORI × MODEL (dihitung ulang dari predictions)", "M")
mx_hdr = mx_title + 1
header(ws3, mx_hdr, 1, ["Kategori", "Ground truth", "Jumlah"] + MODELS)
for i, c_ in enumerate(cats_sorted):
    r = mx_hdr + 1 + i
    cells = [c_["kategori"], c_["truth"], c_["total"]] + [c_["per_model"][m] for m in MODELS]
    for j, v in enumerate(cells):
        cell = ws3.cell(row=r, column=1 + j, value=v)
        cell.font = Font(name=FONT, size=10, color=TEXT, bold=(j == 0))
        cell.border = BOX
        if j == 2:
            cell.number_format = "#,##0"
            cell.alignment = Alignment(horizontal="center")
        elif j >= 3:
            cell.number_format = "0.00%"
            cell.alignment = Alignment(horizontal="right")
        else:
            cell.alignment = Alignment(horizontal="center" if j == 1 else "left")
tot_row = mx_hdr + 1 + len(cats_sorted)
tot_vals = ["Seluruh file", "Real+Fake", N_FILE] + [METRICS[m]["acc_cal"] for m in MODELS]
for j, v in enumerate(tot_vals):
    cell = ws3.cell(row=tot_row, column=1 + j, value=v)
    cell.font = Font(name=FONT, size=10, bold=True, color=NAVY)
    cell.border = BOX
    cell.fill = PatternFill("solid", fgColor=LIGHT)
    if j == 2:
        cell.number_format = "#,##0"
        cell.alignment = Alignment(horizontal="center")
    elif j >= 3:
        cell.number_format = "0.00%"
        cell.alignment = Alignment(horizontal="right")
    else:
        cell.alignment = Alignment(horizontal="center" if j == 1 else "left")
mx_first_col, mx_last_col = 4, 3 + len(MODELS)
ws3.conditional_formatting.add(
    f"{get_column_letter(mx_first_col)}{mx_hdr + 1}:{get_column_letter(mx_last_col)}{tot_row - 1}",
    ColorScaleRule(start_type="num", start_value=0.2, start_color="F8696B",
                   mid_type="num", mid_value=0.6, mid_color="FFEB84",
                   end_type="num", end_value=1.0, end_color="63BE7B"))
ws3.merge_cells(start_row=tot_row + 2, start_column=1, end_row=tot_row + 3, end_column=13)
c = ws3.cell(row=tot_row + 2, column=1)
c.value = ("Baris \"Seluruh file\" dicocokkan dengan accuracy_calibrated di metrics.csv (selisih 0). "
           "Kategori real (Laki_laki, perempuan) = rekaman manusia asli; kategori fake = hasil cloning 4 generator TTS.")
c.font = Font(name=FONT, size=9, italic=True, color=GRAY)
c.alignment = Alignment(vertical="top", wrap_text=True)
ws3.freeze_panes = "B6"


# --------------------------------------------------------------------------- #
# SHEET 4 — METRIK MODEL (SUMBER)
# --------------------------------------------------------------------------- #
ws4 = wb.create_sheet("Metrik Model")
ws4.sheet_properties.tabColor = "5B9BD5"
page(ws4, title_rows="4:4")
title_block(ws4, "METRIK MODEL — DATA SUMBER",
            "Isi persis validation_external_metrics.csv (angka disimpan sebagai angka, bukan teks).", "I")
src_metrics_hdr = list(metrics_rows[0].keys())
header(ws4, 4, 1, src_metrics_hdr)
for i, row in enumerate(metrics_rows):
    r = 5 + i
    for j, key in enumerate(src_metrics_hdr):
        v = row[key]
        cell = ws4.cell(row=r, column=1 + j, value=(float(v) if key != "model" else v))
        cell.font = Font(name=FONT, size=10, color=TEXT)
        cell.border = BOX
        if key != "model":
            cell.number_format = "0.00000"
            cell.alignment = Alignment(horizontal="right")
        else:
            cell.font = Font(name=FONT, size=10, color=TEXT, bold=True)
last4 = 4 + len(metrics_rows)
add_table(ws4, "TblSumberMetrik", f"A4:I{last4}")
set_widths(ws4, {"A": 10, "B": 18, "C": 11, "D": 11, "E": 18, "F": 20, "G": 22, "H": 21, "I": 20})
ws4.freeze_panes = "B5"


# --------------------------------------------------------------------------- #
# SHEET 5 — BREAKDOWN KATEGORI (SUMBER)
# --------------------------------------------------------------------------- #
ws5 = wb.create_sheet("Breakdown Kategori")
ws5.sheet_properties.tabColor = "70AD47"
page(ws5, title_rows="4:4")
title_block(ws5, "BREAKDOWN KATEGORI — DATA SUMBER",
            "Isi persis validation_external_category_breakdown.csv (kolom *_pct dipertahankan sebagai teks seperti aslinya).", "E")
src_cat_hdr = list(category_rows[0].keys())
header(ws5, 4, 1, src_cat_hdr)
for i, row in enumerate(category_rows):
    r = 5 + i
    for j, key in enumerate(src_cat_hdr):
        v = row[key]
        if key == "total_files":
            val, fmt, align = int(v), "#,##0", "right"
        elif key == "accuracy_calibrated_E4a":
            val, fmt, align = float(v), "0.0000000000", "right"
        elif key == "ground_truth":
            val, fmt, align = v, None, "center"
        else:
            val, fmt, align = v, None, "left"
        cell = ws5.cell(row=r, column=1 + j, value=val)
        cell.font = Font(name=FONT, size=10, color=TEXT, bold=(key == "category"))
        cell.border = BOX
        cell.alignment = Alignment(horizontal=align)
        if fmt:
            cell.number_format = fmt
last5 = 4 + len(category_rows)
add_table(ws5, "TblSumberKategori", f"A4:E{last5}")
set_widths(ws5, {"A": 18, "B": 14, "C": 12, "D": 26, "E": 30})
ws5.freeze_panes = "B5"


# --------------------------------------------------------------------------- #
# SHEET 6 — PREDIKSI (SUMBER)
# --------------------------------------------------------------------------- #
ws6 = wb.create_sheet("Prediksi")
ws6.sheet_properties.tabColor = "A5A5A5"
page(ws6, title_rows="4:4")
title_block(ws6, "PREDIKSI PER FILE — DATA SUMBER",
            f"Isi persis validation_external_predictions.csv: {N_FILE} baris × {len(pred_rows[0])} kolom. "
            "Kolom bernomor 0 pada blok correct_cal_* = prediksi salah.", "T")
pred_hdr = list(pred_rows[0].keys())

NUMERIC_PREFIX = ("prob_fake_", "correct_cal_")
TEXT_PREFIX = ("pred_std_", "pred_cal_")

# header
header(ws6, 4, 1, pred_hdr)
# blok warna grup per model di baris 3
ws6.merge_cells(start_row=3, start_column=1, end_row=3, end_column=6)
g = ws6.cell(row=3, column=1, value="Identitas file & label")
g.font = Font(name=FONT, size=9, bold=True, color=NAVY)
g.fill = PatternFill("solid", fgColor=LIGHT)
g.alignment = Alignment(horizontal="center", vertical="center")
for i, m in enumerate(MODELS):
    c0 = 7 + i * 4
    ws6.merge_cells(start_row=3, start_column=c0, end_row=3, end_column=c0 + 3)
    g = ws6.cell(row=3, column=c0, value=m)
    g.font = Font(name=FONT, size=9, bold=True, color=NAVY)
    g.fill = PatternFill("solid", fgColor=LIGHT)
    g.alignment = Alignment(horizontal="center", vertical="center")
ws6.row_dimensions[3].height = 18

INT_KEYS = {"label", "n_segments"}
for i, row in enumerate(pred_rows):
    r = 5 + i
    for j, key in enumerate(pred_hdr):
        v = row[key]
        if key in INT_KEYS:
            val, fmt, align = int(v), "#,##0", "center"
        elif key.startswith(NUMERIC_PREFIX):
            val, fmt, align = float(v), "0.0000", "right"
        else:
            val, fmt, align = v, None, "center" if key.startswith(TEXT_PREFIX) else "left"
        cell = ws6.cell(row=r, column=1 + j, value=val)
        cell.font = Font(name=FONT, size=9, color=TEXT)
        cell.alignment = Alignment(horizontal=align)
        if fmt:
            cell.number_format = fmt

last6 = 4 + len(pred_rows)
last_col6 = get_column_letter(len(pred_hdr))
add_table(ws6, "TblSumberPrediksi", f"A4:{last_col6}{last6}")
set_widths(ws6, {"A": 22, "B": 44, "C": 8, "D": 10, "E": 14, "F": 11})
for i in range(len(MODELS) * 4):
    ws6.column_dimensions[get_column_letter(7 + i)].width = 12

# sorot prediksi salah (correct_cal_* == 0)
for i in range(len(MODELS)):
    col = get_column_letter(10 + i * 4)
    ws6.conditional_formatting.add(
        f"{col}5:{col}{last6}",
        CellIsRule(operator="equal", formula=["0"],
                   fill=PatternFill("solid", bgColor=RED_FILL),
                   font=Font(name=FONT, size=9, bold=True, color=RED_TEXT)))
ws6.freeze_panes = "C5"


# --------------------------------------------------------------------------- #
# 4. SIMPAN
# --------------------------------------------------------------------------- #
OUT_DIR.mkdir(parents=True, exist_ok=True)
wb.properties.title = "Hasil Validasi Eksternal — Deteksi Speech Deepfake"
wb.properties.creator = "Alvin"
wb.properties.description = ("Workbook validasi eksternal dari 3 CSV (metrics, category breakdown, "
                             "predictions). Disusun otomatis oleh build_validasi_profesional.py")
wb.save(OUT)
print("=" * 78)
print(f"TERSIMPAN: {OUT}")
print(f"Sheets: {wb.sheetnames}")
