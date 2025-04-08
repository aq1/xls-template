import io

from docx import Document
from openpyxl import load_workbook

from common import File, Sheet, Template


def _do_read_rows(file: File):
    wb = load_workbook(io.BytesIO(file.content))
    sheet = wb.active
    headers = [cell.value for cell in sheet[1]]
    rows = []
    for row in sheet.iter_rows(min_row=2, values_only=True):
        if not any(row):
            continue
        rows.append({str(headers[i]): str(row[i]) for i in range(len(headers))})
    return Sheet(rows=rows)


def _do_read_template(file: File):
    return Template(
        doc=Document(io.BytesIO(file.content)),
        name=file.name,
    )


def read_rows(file: File):
    try:
        return True, _do_read_rows(file)
    except Exception as e:
        return False, f"Failed to read rows {e}"


def read_template(file: File):
    try:
        return True, _do_read_template(file)
    except Exception as e:
        return False, f"Failed to read template {e}"
