import fs from "node:fs/promises";
import { SpreadsheetFile, Workbook } from "@oai/artifact-tool";

const inputDir = "C:/Users/alvin/Documents/Coolyeah/Skirpsi/Teknikal/fase_1/hasil_validasi";
const outputDir = "C:/Users/alvin/Documents/Coolyeah/Skirpsi/Teknikal/fase_1/outputs/validasi_external";
const font = "Arial";
const navy = "#1F4E78";
const blue = "#D9EAF7";
const light = "#F5F7FA";
const border = "#D9E2F3";

function parseCsv(text) {
  const rows = [];
  let row = [], cell = "", quoted = false;
  for (let i = 0; i < text.length; i++) {
    const ch = text[i];
    if (quoted) {
      if (ch === '"' && text[i + 1] === '"') { cell += '"'; i++; }
      else if (ch === '"') quoted = false;
      else cell += ch;
    } else if (ch === '"') quoted = true;
    else if (ch === ',') { row.push(cell); cell = ""; }
    else if (ch === '\n') { row.push(cell.replace(/\r$/, "")); rows.push(row); row = []; cell = ""; }
    else cell += ch;
  }
  if (cell.length || row.length) { row.push(cell); rows.push(row); }
  return rows;
}

function num(v) { return Number(v); }
function colName(n) {
  let s = ""; while (n > 0) { const r = (n - 1) % 26; s = String.fromCharCode(65 + r) + s; n = Math.floor((n - 1) / 26); } return s;
}
function writeRawSheet(sheet, title, subtitle, rows, tabColor) {
  sheet.showGridLines = false; sheet.tabColor = tabColor;
  const lastCol = colName(rows[0].length);
  sheet.getRange(`A1:${lastCol}1`).merge();
  sheet.getRange("A1").values = [[title]];
  sheet.getRange(`A2:${lastCol}2`).merge();
  sheet.getRange("A2").values = [[subtitle]];
  sheet.getRange(`A4:${lastCol}${rows.length + 3}`).values = rows;
  sheet.getRange("A1").format = { font: { name: font, size: 16, bold: true, color: navy } };
  sheet.getRange("A2").format = { font: { name: font, size: 10, italic: true, color: "#5B6573" } };
  sheet.getRange(`A4:${lastCol}4`).format = { fill: navy, font: { name: font, size: 10, bold: true, color: "#FFFFFF" }, wrapText: true, verticalAlignment: "center" };
  sheet.getRange(`A5:${lastCol}${rows.length + 3}`).format = { font: { name: font, size: 10, color: "#202124" }, verticalAlignment: "center" };
  sheet.getRange(`A4:${lastCol}${rows.length + 3}`).format.borders = { preset: "outside", style: "thin", color: border };
  sheet.getRange(`A4:${lastCol}${rows.length + 3}`).format.autofitColumns();
  sheet.getRange(`A4:${lastCol}${rows.length + 3}`).format.autofitRows();
  sheet.getRange(`A4:${lastCol}${rows.length + 3}`).format.rowHeight = 22;
  sheet.getRange(`A4:${lastCol}${rows.length + 3}`).format.wrapText = false;
  sheet.getRange("A4").format.rowHeight = 38;
  const widths = rows[0].map((h) => h.length > 24 ? 18 : Math.max(12, Math.min(30, h.length + 3)));
  widths.forEach((w, i) => sheet.getRange(`${colName(i + 1)}:${colName(i + 1)}`).format.columnWidth = w);
  sheet.freezePanes.freezeRows(4);
  const table = sheet.tables.add(`A4:${lastCol}${rows.length + 3}`, true, `${title.replace(/[^A-Za-z0-9]/g, "")}Table`);
  table.showFilterButton = true; table.showBandedRows = true;
  // Reapply header styling after table creation so header labels remain visible in Excel/rendered previews.
  sheet.getRange(`A4:${lastCol}4`).format = { fill: navy, font: { name: font, size: 9, bold: true, color: "#FFFFFF" }, wrapText: true, verticalAlignment: "center" };
  sheet.getRange(`A4:${lastCol}4`).format.rowHeight = 42;
  if (title === "Prediksi") {
    const groups = [
      ["G3:J3", "B0"], ["K3:N3", "B1"], ["O3:R3", "B2"], ["S3:V3", "B3"], ["W3:Z3", "B4"],
      ["AA3:AD3", "E4a"], ["AE3:AH3", "E4b"], ["AI3:AL3", "E4c"], ["AM3:AP3", "E4d"], ["AQ3:AT3", "E4e"]
    ];
    for (const [range, label] of groups) {
      sheet.getRange(range).merge(); sheet.getRange(range.split(":")[0]).values = [[label]];
      sheet.getRange(range).format = { fill: blue, font: { name: font, size: 9, bold: true, color: navy }, horizontalAlignment: "center", verticalAlignment: "center" };
    }
    sheet.getRange("A3:F3").merge(); sheet.getRange("A3").values = [["Identitas file dan label"]];
    sheet.getRange("A3:F3").format = { fill: blue, font: { name: font, size: 9, bold: true, color: navy }, horizontalAlignment: "center", verticalAlignment: "center" };
    sheet.getRange("A3:AT3").format.rowHeight = 22;
    sheet.getRange("A:A").format.columnWidth = 24; sheet.getRange("B:B").format.columnWidth = 38; sheet.getRange("C:F").format.columnWidth = 14;
    sheet.getRange("G:AT").format.columnWidth = 14;
  }
  if (title === "Prediksi Detail") {
    sheet.getRange("A:A").format.columnWidth = 24; sheet.getRange("B:B").format.columnWidth = 48;
    sheet.getRange("C:F").format.columnWidth = 14; sheet.getRange("G:K").format.columnWidth = 16;
  }
  return { lastCol, lastRow: rows.length + 3 };
}
function styleSection(sheet, range, fill = blue) { sheet.getRange(range).format = { fill, font: { name: font, size: 10, bold: true, color: navy }, verticalAlignment: "center" }; }

const files = {
  metrics: await fs.readFile(`${inputDir}/validation_external_metrics.csv`, "utf8"),
  category: await fs.readFile(`${inputDir}/validation_external_category_breakdown.csv`, "utf8"),
  predictions: await fs.readFile(`${inputDir}/validation_external_predictions.csv`, "utf8"),
};
const metrics = parseCsv(files.metrics), category = parseCsv(files.category), predictions = parseCsv(files.predictions);
const models = metrics.slice(1).map(r => r[0]);

const wb = Workbook.create();
const summary = wb.worksheets.add("Ringkasan");
const modelAnalysis = wb.worksheets.add("Analisis Model");
const categoryAnalysis = wb.worksheets.add("Analisis Kategori");
const metricsSheet = wb.worksheets.add("Metrik Model");
const categorySheet = wb.worksheets.add("Breakdown Kategori");
const detailSheet = wb.worksheets.add("Prediksi Detail");
const predictionSheet = wb.worksheets.add("Prediksi");

// Raw source tabs: values are written as strings exactly as found in the CSV files.
writeRawSheet(metricsSheet, "Metrik Model", "Sumber: validation_external_metrics.csv | Data sumber dipertahankan apa adanya.", metrics, "#5B9BD5");
writeRawSheet(categorySheet, "Breakdown Kategori", "Sumber: validation_external_category_breakdown.csv | Data sumber dipertahankan apa adanya.", category, "#70AD47");

// Readable long-format view: every source prediction is represented once per file/model.
const detailHeaders = ["file_name", "rel_path", "label", "label_str", "category", "n_segments", "model", "prob_fake", "pred_std", "pred_cal", "correct_cal"];
const detailRows = [detailHeaders];
for (const row of predictions.slice(1)) {
  for (let i = 0; i < models.length; i++) {
    const c = 6 + (i * 4);
    detailRows.push([row[0], row[1], row[2], row[3], row[4], row[5], models[i], row[c], row[c + 1], row[c + 2], row[c + 3]]);
  }
}
writeRawSheet(detailSheet, "Prediksi Detail", "Tampilan memanjang turunan dari validation_external_predictions.csv | 1 baris = 1 file dan 1 model.", detailRows, "#8064A2");
writeRawSheet(predictionSheet, "Prediksi", "Sumber: validation_external_predictions.csv | 170 baris prediksi dan 46 kolom dipertahankan apa adanya.", predictions, "#A5A5A5");

// Derived model analysis.
modelAnalysis.showGridLines = false; modelAnalysis.tabColor = "#4472C4";
modelAnalysis.getRange("A1:I1").merge(); modelAnalysis.getRange("A1").values = [["Analisis Model"]];
modelAnalysis.getRange("A2:I2").merge(); modelAnalysis.getRange("A2").values = [["Tampilan analitis yang dihitung dari tab Metrik Model; tab sumber tetap tersedia untuk audit."]];
const modelHeaders = ["Model", "Threshold calibrated", "AUC", "EER", "Accuracy std 0.50", "Accuracy calibrated", "Recall real calibrated", "Recall fake calibrated", "F1 fake calibrated"];
const modelRows = metrics.slice(1).map(r => [r[0], num(r[1]), num(r[2]), num(r[3]), num(r[4]), num(r[5]), num(r[6]), num(r[7]), num(r[8])]);
modelAnalysis.getRange("A4:I4").values = [modelHeaders]; modelAnalysis.getRange(`A5:I${modelRows.length + 4}`).values = modelRows;
styleSection(modelAnalysis, "A4:I4", navy);
modelAnalysis.getRange(`A5:I${modelRows.length + 4}`).format = { font: { name: font, size: 10 }, verticalAlignment: "center" };
modelAnalysis.getRange(`B5:I${modelRows.length + 4}`).format.numberFormat = "0.00%";
modelAnalysis.getRange(`B5:B${modelRows.length + 4}`).format.numberFormat = "0.00";
modelAnalysis.getRange(`A4:I${modelRows.length + 4}`).format.borders = { preset: "outside", style: "thin", color: border };
modelAnalysis.getRange(`A4:I${modelRows.length + 4}`).format.autofitColumns();
modelAnalysis.getRange(`A:A`).format.columnWidth = 14;
modelAnalysis.getRange(`B:I`).format.columnWidth = 18;
modelAnalysis.freezePanes.freezeRows(4);
const mt = modelAnalysis.tables.add(`A4:I${modelRows.length + 4}`, true, "ModelAnalysisTable"); mt.showFilterButton = true; mt.showBandedRows = true;
modelAnalysis.getRange("A4:I4").format = { fill: navy, font: { name: font, size: 9, bold: true, color: "#FFFFFF" }, wrapText: true, verticalAlignment: "center" };
modelAnalysis.getRange("A4:I4").format.rowHeight = 38;
modelAnalysis.getRange(`F5:F${modelRows.length + 4}`).conditionalFormats.add("dataBar", { color: "#5B9BD5" });

// Derived category analysis.
categoryAnalysis.showGridLines = false; categoryAnalysis.tabColor = "#70AD47";
categoryAnalysis.getRange("A1:E1").merge(); categoryAnalysis.getRange("A1").values = [["Analisis Kategori"]];
categoryAnalysis.getRange("A2:E2").merge(); categoryAnalysis.getRange("A2").values = [["Tampilan analitis yang dihitung dari tab Breakdown Kategori; tab sumber tetap tersedia untuk audit."]];
const catHeaders = ["Category", "Ground truth", "Total files", "Accuracy calibrated E4a", "Accuracy calibrated %"];
const catRows = category.slice(1).map(r => [r[0], r[1], num(r[2]), num(r[3]), r[4]]);
categoryAnalysis.getRange("A4:E4").values = [catHeaders]; categoryAnalysis.getRange(`A5:E${catRows.length + 4}`).values = catRows;
styleSection(categoryAnalysis, "A4:E4", navy);
categoryAnalysis.getRange(`A5:E${catRows.length + 4}`).format = { font: { name: font, size: 10 }, verticalAlignment: "center" };
categoryAnalysis.getRange(`C5:C${catRows.length + 4}`).format.numberFormat = "#,##0";
categoryAnalysis.getRange(`D5:D${catRows.length + 4}`).format.numberFormat = "0.00%";
categoryAnalysis.getRange(`A4:E${catRows.length + 4}`).format.borders = { preset: "outside", style: "thin", color: border };
categoryAnalysis.getRange(`A4:E${catRows.length + 4}`).format.autofitColumns();
categoryAnalysis.getRange("A:A").format.columnWidth = 20; categoryAnalysis.getRange("B:B").format.columnWidth = 14; categoryAnalysis.getRange("C:E").format.columnWidth = 20;
categoryAnalysis.freezePanes.freezeRows(4);
const ct = categoryAnalysis.tables.add(`A4:E${catRows.length + 4}`, true, "CategoryAnalysisTable"); ct.showFilterButton = true; ct.showBandedRows = true;
categoryAnalysis.getRange("A4:E4").format = { fill: navy, font: { name: font, size: 9, bold: true, color: "#FFFFFF" }, wrapText: true, verticalAlignment: "center" };
categoryAnalysis.getRange("A4:E4").format.rowHeight = 38;
categoryAnalysis.getRange(`D5:D${catRows.length + 4}`).conditionalFormats.add("dataBar", { color: "#70AD47" });

// Reader-facing summary.
summary.showGridLines = false; summary.tabColor = navy;
summary.getRange("A1:H1").merge(); summary.getRange("A1").values = [["Validasi Eksternal"]];
summary.getRange("A2:H2").merge(); summary.getRange("A2").values = [["Ringkasan hasil validasi model dari tiga berkas CSV pada folder hasil_validasi"]];
summary.getRange("A4:B4").merge(); summary.getRange("A4").values = [["Cakupan data"]]; styleSection(summary, "A4:B4", blue);
summary.getRange("A5:B8").values = [["Total file prediksi", predictions.length - 1], ["Jumlah model", models.length], ["Jumlah kategori", category.length - 1], ["Sumber data", "3 CSV"]];
summary.getRange("A5:A8").format.font = { name: font, size: 10, bold: true, color: navy }; summary.getRange("B5:B8").format.font = { name: font, size: 10 };
summary.getRange("B5:B7").format.numberFormat = "#,##0";
summary.getRange("D4:I4").merge(); summary.getRange("D4").values = [["Ringkasan metrik model"]]; styleSection(summary, "D4:I4", blue);
summary.getRange("D5:I5").values = [["Model", "AUC", "EER", "Accuracy calibrated", "Recall real", "F1 fake"]]; styleSection(summary, "D5:I5", navy);
summary.getRange(`D6:I${models.length + 5}`).values = modelRows.map(r => [r[0], r[2], r[3], r[5], r[6], r[8]]);
summary.getRange(`E6:I${models.length + 5}`).format.numberFormat = "0.00%";
summary.getRange(`D5:I${models.length + 5}`).format.borders = { preset: "outside", style: "thin", color: border };
summary.getRange(`D5:I${models.length + 5}`).format.font = { name: font, size: 10 };
summary.getRange("D5:I5").format.font = { name: font, size: 10, bold: true, color: "#FFFFFF" };
summary.getRange(`G6:G${models.length + 5}`).conditionalFormats.add("dataBar", { color: "#5B9BD5" });

summary.getRange("A11:E11").merge(); summary.getRange("A11").values = [["Akurasi E4a berdasarkan kategori"]]; styleSection(summary, "A11:E11", blue);
summary.getRange("A12:E12").values = [["Category", "Ground truth", "Total files", "Accuracy", "Accuracy %"]]; styleSection(summary, "A12:E12", navy);
summary.getRange(`A13:E${catRows.length + 12}`).values = catRows;
summary.getRange(`C13:C${catRows.length + 12}`).format.numberFormat = "#,##0";
summary.getRange(`D13:D${catRows.length + 12}`).format.numberFormat = "0.00%";
summary.getRange(`A12:E${catRows.length + 12}`).format.borders = { preset: "outside", style: "thin", color: border };
summary.getRange(`A12:E${catRows.length + 12}`).format.font = { name: font, size: 10 };
summary.getRange("A12:E12").format.font = { name: font, size: 10, bold: true, color: "#FFFFFF" };
summary.getRange(`D13:D${catRows.length + 12}`).conditionalFormats.add("dataBar", { color: "#70AD47" });
summary.getRange("A21:H21").merge(); summary.getRange("A21").values = [["Catatan sumber"]]; styleSection(summary, "A21:H21", blue);
summary.getRange("A22:H23").merge(); summary.getRange("A22").values = [["Tab Metrik Model, Breakdown Kategori, dan Prediksi berisi data sumber dari CSV tanpa perubahan isi. Tab Analisis Model dan Analisis Kategori adalah tampilan turunan untuk memudahkan pembacaan."]];
summary.getRange("A22:H23").format = { font: { name: font, size: 10, italic: true, color: "#5B6573" }, wrapText: true, verticalAlignment: "top" };
summary.getRange("A1:H23").format.font.name = font;
summary.getRange("A1").format.font = { name: font, size: 16, bold: true, color: navy };
summary.getRange("A2").format.font = { name: font, size: 10, italic: true, color: "#5B6573" };
summary.getRange("A:A").format.columnWidth = 24; summary.getRange("B:B").format.columnWidth = 18; summary.getRange("C:C").format.columnWidth = 4; summary.getRange("D:I").format.columnWidth = 18;

// Small helper ranges keep the chart bindings contiguous and unambiguous.
summary.getRange(`T1:U${models.length + 1}`).values = [["Model", "Accuracy calibrated"], ...modelRows.map(r => [r[0], r[5]])];
summary.getRange(`T13:U${catRows.length + 13}`).values = [["Category", "Accuracy"], ...catRows.map(r => [r[0], r[3]])];

// Charts on the right side of the summary.
const modelChart = summary.charts.add("bar", summary.getRange(`T1:U${models.length + 1}`));
modelChart.title = "Accuracy calibrated per model"; modelChart.titleTextStyle.typeface = font; modelChart.titleTextStyle.fontSize = 12; modelChart.hasLegend = false; modelChart.setPosition("K4", "R17");
modelChart.xAxis = { axisType: "textAxis", textStyle: { typeface: font, fontSize: 10 } }; modelChart.yAxis = { numberFormatCode: "0%", numberFormatSourceLinked: false, textStyle: { typeface: font, fontSize: 10 } };
const catChart = summary.charts.add("bar", summary.getRange(`T13:U${catRows.length + 13}`));
catChart.title = "Accuracy E4a per category"; catChart.titleTextStyle.typeface = font; catChart.titleTextStyle.fontSize = 12; catChart.hasLegend = false; catChart.setPosition("K19", "R32");
catChart.xAxis = { axisType: "textAxis", textStyle: { typeface: font, fontSize: 10 } }; catChart.yAxis = { numberFormatCode: "0%", numberFormatSourceLinked: false, textStyle: { typeface: font, fontSize: 10 } };

await fs.mkdir(outputDir, { recursive: true });
const preview = await wb.render({ sheetName: "Ringkasan", range: "A1:R32", scale: 1, format: "png" });
await fs.writeFile(`${outputDir}/ringkasan.png`, new Uint8Array(await preview.arrayBuffer()));
const xlsx = await SpreadsheetFile.exportXlsx(wb);
await xlsx.save(`${outputDir}/hasil_validasi_profesional.xlsx`);

const inspect = await wb.inspect({ kind: "table", range: "Ringkasan!A1:R32", include: "values,formulas", tableMaxRows: 32, tableMaxCols: 18, maxChars: 12000 });
console.log(inspect.ndjson);
const errors = await wb.inspect({ kind: "match", searchTerm: "#REF!|#DIV/0!|#VALUE!|#NAME\\?|#N/A|#NUM!|#NULL!|#SPILL!|#CALC!", options: { useRegex: true, maxResults: 300 }, summary: "final formula error scan" });
console.log(errors.ndjson);
console.log(`SAVED ${outputDir}/hasil_validasi_profesional.xlsx`);
