import fs from "node:fs/promises";
import { fileURLToPath } from "node:url";
import { SpreadsheetFile, Workbook } from "@oai/artifact-tool";

const csvPath = new URL("../data/product_prices.csv", import.meta.url);
const outputDir = new URL("../outputs/project-2/", import.meta.url);
const csvText = await fs.readFile(csvPath, "utf8");
const lines = csvText.trim().split(/\r?\n/);
const names = [...new Set(lines.slice(1).map((line) => line.split(",")[1]))];
const rawLastRow = lines.length;
const summaryLastRow = 7 + names.length;

const workbook = await Workbook.fromCSV(csvText, { sheetName: "Raw Prices" });
const raw = workbook.worksheets.getItem("Raw Prices");
const summary = workbook.worksheets.add("Summary");

const navy = "#123047";
const teal = "#0F766E";
const paleTeal = "#E6F4F1";
const slate = "#4B6070";
const light = "#F4F7F8";

summary.showGridLines = false;
summary.mergeCells("A1:H1");
summary.getRange("A1").values = [["Market Research and Price Comparison"]];
summary.getRange("A1:H1").format = {
  fill: navy,
  font: { bold: true, color: "#FFFFFF", size: 18 },
  horizontalAlignment: "center",
  verticalAlignment: "center",
};
summary.getRange("A1:H1").format.rowHeight = 34;
summary.mergeCells("A2:H2");
summary.getRange("A2").values = [[
  "Educational sample dataset in INR | Capture date: 2026-05-20 | Not live market pricing",
]];
summary.getRange("A2:H2").format = {
  fill: paleTeal,
  font: { italic: true, color: slate, size: 10 },
  horizontalAlignment: "center",
};
summary.getRange("A2:H2").format.rowHeight = 24;

summary.getRange("A3:H3").values = [[
  "Products", "", "Observations", "", "Retailers", "", "Largest Saving", "",
]];
summary.getRange("A4:H4").values = [["", "", "", "", "", "", "", ""]];
summary.getRange("A4").formulas = [[`=COUNTA(A8:A${summaryLastRow})`]];
summary.getRange("C4").formulas = [[`=COUNTA('Raw Prices'!A2:A${rawLastRow})`]];
summary.getRange("E4").formulas = [[`=COUNTA(UNIQUE('Raw Prices'!F2:F${rawLastRow}))`]];
summary.getRange("G4").formulas = [[`=MAX(F8:F${summaryLastRow})`]];
summary.getRange("A3:H3").format = {
  fill: teal,
  font: { bold: true, color: "#FFFFFF", size: 10 },
  horizontalAlignment: "center",
};
summary.getRange("A4:H4").format = {
  fill: paleTeal,
  font: { bold: true, color: navy, size: 16 },
  horizontalAlignment: "center",
};
summary.getRange("G4").format.numberFormat = '"INR " #,##0.00';
summary.getRange("A3:H4").format.rowHeight = 25;

summary.getRange("A7:G7").values = [[
  "Product", "Category", "Offers", "Lowest Price", "Highest Price", "Possible Saving", "Cheapest Retailer",
]];
summary.getRange(`A8:A${summaryLastRow}`).values = names.map((name) => [name]);
for (let row = 8; row <= summaryLastRow; row += 1) {
  summary.getRange(`B${row}`).formulas = [[
    `=INDEX('Raw Prices'!$D$2:$D$${rawLastRow},MATCH(A${row},'Raw Prices'!$B$2:$B$${rawLastRow},0))`,
  ]];
  summary.getRange(`C${row}`).formulas = [[
    `=COUNTIF('Raw Prices'!$B$2:$B$${rawLastRow},A${row})`,
  ]];
  summary.getRange(`D${row}`).formulas = [[
    `=MINIFS('Raw Prices'!$H$2:$H$${rawLastRow},'Raw Prices'!$B$2:$B$${rawLastRow},A${row},'Raw Prices'!$L$2:$L$${rawLastRow},1)`,
  ]];
  summary.getRange(`E${row}`).formulas = [[
    `=MAXIFS('Raw Prices'!$H$2:$H$${rawLastRow},'Raw Prices'!$B$2:$B$${rawLastRow},A${row},'Raw Prices'!$L$2:$L$${rawLastRow},1)`,
  ]];
  summary.getRange(`F${row}`).formulas = [[`=E${row}-D${row}`]];
  summary.getRange(`G${row}`).formulas = [[
    `=INDEX('Raw Prices'!$F$2:$F$${rawLastRow},MATCH(D${row},'Raw Prices'!$H$2:$H$${rawLastRow},0))`,
  ]];
}

const summaryTable = summary.tables.add(`A7:G${summaryLastRow}`, true, "PriceComparisonSummary");
summaryTable.style = "TableStyleMedium2";
summary.getRange(`D8:F${summaryLastRow}`).format.numberFormat = '"INR " #,##0.00';
summary.getRange(`F8:F${summaryLastRow}`).conditionalFormats.add("dataBar", {
  color: "#0F766E",
  gradient: true,
});
summary.freezePanes.freezeRows(7);
summary.getRange("A:A").format.columnWidth = 34;
summary.getRange("B:B").format.columnWidth = 21;
summary.getRange("C:C").format.columnWidth = 11;
summary.getRange("D:F").format.columnWidth = 17;
summary.getRange("G:G").format.columnWidth = 20;
summary.getRange("H:H").format.columnWidth = 3;

summary.getRange("I7:J7").values = [["Product", "Saving INR"]];
for (let row = 8; row <= summaryLastRow; row += 1) {
  summary.getRange(`I${row}:J${row}`).formulas = [[`=A${row}`, `=F${row}`]];
}
summary.getRange("I7:J7").format = {
  fill: teal,
  font: { bold: true, color: "#FFFFFF" },
};
summary.getRange(`J8:J${summaryLastRow}`).format.numberFormat = '"INR " #,##0';
summary.getRange("I:I").format.columnWidth = 32;
summary.getRange("J:J").format.columnWidth = 14;
const chart = summary.charts.add("bar", summary.getRange(`I7:J${summaryLastRow}`));
chart.title = "Saving Opportunity by Product (INR)";
chart.hasLegend = false;
chart.xAxis = { numberFormatCode: '"INR " #,##0' };
chart.setPosition("L3", "T20");

raw.showGridLines = false;
const rawTable = raw.tables.add(`A1:M${rawLastRow}`, true, "RawPriceObservations");
rawTable.style = "TableStyleMedium2";
raw.getRange("A1:M1").format = {
  fill: navy,
  font: { bold: true, color: "#FFFFFF" },
  wrapText: true,
};
raw.getRange(`H2:I${rawLastRow}`).format.numberFormat = '"INR " #,##0.00';
raw.getRange(`J2:J${rawLastRow}`).format.numberFormat = "0.0";
raw.getRange("A:A").format.columnWidth = 18;
raw.getRange("B:B").format.columnWidth = 34;
raw.getRange("C:D").format.columnWidth = 20;
raw.getRange("E:E").format.columnWidth = 18;
raw.getRange("F:G").format.columnWidth = 20;
raw.getRange("H:I").format.columnWidth = 18;
raw.getRange("J:L").format.columnWidth = 14;
raw.getRange("M:M").format.columnWidth = 16;
raw.freezePanes.freezeRows(1);
raw.getRange(`L2:L${rawLastRow}`).conditionalFormats.add("cellIs", {
  operator: "equal",
  formula: 0,
  format: { fill: "#FDE8E8", font: { color: "#9B1C1C", bold: true } },
});

const keyRange = await workbook.inspect({
  kind: "table",
  range: `Summary!A3:J${summaryLastRow}`,
  include: "values,formulas",
  tableMaxRows: 18,
  tableMaxCols: 10,
});
console.log(keyRange.ndjson);
const errors = await workbook.inspect({
  kind: "match",
  searchTerm: "#REF!|#DIV/0!|#VALUE!|#NAME\\?|#N/A",
  options: { useRegex: true, maxResults: 100 },
  summary: "final formula error scan",
});
console.log(errors.ndjson);

await fs.mkdir(outputDir, { recursive: true });
const summaryPng = await workbook.render({
  sheetName: "Summary",
  autoCrop: "all",
  scale: 1,
  format: "png",
});
await fs.writeFile(
  new URL("summary_preview.png", outputDir),
  new Uint8Array(await summaryPng.arrayBuffer()),
);
const rawPng = await workbook.render({
  sheetName: "Raw Prices",
  autoCrop: "all",
  scale: 1,
  format: "png",
});
await fs.writeFile(
  new URL("raw_prices_preview.png", outputDir),
  new Uint8Array(await rawPng.arrayBuffer()),
);

const xlsx = await SpreadsheetFile.exportXlsx(workbook);
const xlsxPath = fileURLToPath(new URL("market_research_dataset.xlsx", outputDir));
await xlsx.save(xlsxPath);
console.log(xlsxPath);
