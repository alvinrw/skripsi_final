import fs from "node:fs/promises";
import { FileBlob, SpreadsheetFile } from "@oai/artifact-tool";

const path = "C:/Users/alvin/Documents/Coolyeah/Skirpsi/Teknikal/fase_1/outputs/validasi_external/hasil_validasi_profesional.xlsx";
const out = "C:/Users/alvin/Documents/Coolyeah/Skirpsi/Teknikal/fase_1/outputs/validasi_external/review";
await fs.mkdir(out, { recursive: true });
const wb = await SpreadsheetFile.importXlsx(await FileBlob.load(path));
console.log((await wb.inspect({ kind: "sheet", include: "id,name" })).ndjson);
for (const s of wb.worksheets.items) {
  const used = s.getUsedRange();
  console.log(`${s.name}: ${used ? used.address : "no used range"}`);
  const range = s.name === "Prediksi Detail" ? "A1:K25" : (s.name === "Prediksi" ? "A1:AT20" : undefined);
  const blob = await wb.render(range ? { sheetName: s.name, range, scale: 1, format: "png" } : { sheetName: s.name, autoCrop: "all", scale: 1, format: "png" });
  await fs.writeFile(`${out}/${s.name.replace(/[^A-Za-z0-9_-]/g, "_")}.png`, new Uint8Array(await blob.arrayBuffer()));
}
