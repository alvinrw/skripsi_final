import { FileBlob, SpreadsheetFile } from "@oai/artifact-tool";
const p = "C:/Users/alvin/Documents/Coolyeah/Skirpsi/Teknikal/fase_1/outputs/validasi_external/hasil_validasi_profesional.xlsx";
const wb = await SpreadsheetFile.importXlsx(await FileBlob.load(p));
for (const [s,r] of [["Analisis Model","A1:I6"],["Analisis Kategori","A1:E6"],["Prediksi","A1:AT5"]]) {
  const sh = wb.worksheets.getItem(s);
  console.log(`---${s}---`);
  console.log(JSON.stringify(sh.getRange(r).values));
}
