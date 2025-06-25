import pandas as pd
import json
import glob
from openpyxl import load_workbook

# Find all typhoon JSON files
json_files = glob.glob("typhoon_predict_*.json")

for json_file in json_files:
    # Load JSON data
    with open(json_file, "r") as f:
        data = json.load(f)
    # Convert to DataFrame
    df = pd.DataFrame(data)
    # Export to Excel (same name, .xlsx extension)
    xlsx_file = json_file.replace(".json", ".xlsx")
    df.to_excel(xlsx_file, index=False)

    # Auto-adjust column widths
    wb = load_workbook(xlsx_file)
    ws = wb.active
    for column_cells in ws.columns:
        length = max(len(str(cell.value)) if cell.value is not None else 0 for cell in column_cells)
        ws.column_dimensions[column_cells[0].column_letter].width = length + 2
    wb.save(xlsx_file)

    print(f"Exported {json_file} to {xlsx_file} (auto-width columns)")