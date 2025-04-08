import multiprocessing
import os
import tempfile

import pypandoc

from common import Error, File, ReportResult, Sheet, Template
from reader import read_template


def replace_text_in_docx(template: Template, old: str, new: str):
    old = "{{" + old + "}}"

    def replace_in_paragraphs(paragraphs):
        for p in paragraphs:
            if old in p.text:
                for run in p.runs:
                    run.text = run.text.replace(old, new)

    replace_in_paragraphs(template.doc.paragraphs)

    for table in template.doc.tables:
        for row in table.rows:
            for cell in row.cells:
                replace_in_paragraphs(cell.paragraphs)

    for section in template.doc.sections:
        replace_in_paragraphs(section.header.paragraphs)
        replace_in_paragraphs(section.footer.paragraphs)

    return template


def convert_to_pdf(template: Template, pdf_file_name: str):
    with tempfile.NamedTemporaryFile(suffix=".docx") as docx_file:
        template.doc.save(docx_file.name)
        with open(f"pdf/{pdf_file_name}", "w") as pdf_file:
            pdf_file.write(
                pypandoc.convert_file(
                    source_file=docx_file.name,
                    to="pdf",
                    outputfile=pdf_file.name,
                )
            )
    return pdf_file.name


def get_pdf_file_name(row: dict[str, str], template: Template):
    name = template.name
    for old, new in row.items():
        name = name.replace("{{" + old + "}}", new)

    name, _ = os.path.splitext(name)
    return f"{name}.pdf"


def create_pdf(row: dict[str, str], template: Template):
    for old, new in row.items():
        template = replace_text_in_docx(template, old, new)

    return convert_to_pdf(template, pdf_file_name=get_pdf_file_name(row, template))


def worker(
    queue: multiprocessing.Queue,
    rows: list[dict[str, str]],
    template_file: File,
):

    ok, template = read_template(template_file)
    if not ok:
        queue.put(Error(msg=template))
        return

    for row in rows:
        try:
            pdf_name = create_pdf(
                row,
                template,
            )
            queue.put(pdf_name)
        except Exception as e:
            queue.put(Error(msg=str(e)))


def distribute_rows(rows):
    cpu_count = multiprocessing.cpu_count()
    avg_chunk_size = len(rows) // cpu_count
    remainder = len(rows) % cpu_count

    split_rows = []
    index = 0

    for i in range(cpu_count):
        chunk_size = avg_chunk_size + (1 if i < remainder else 0)
        split_rows.append(rows[index : index + chunk_size])
        index += chunk_size

    return split_rows


def run_format_job(sheet: Sheet, template_file: File):
    queue = multiprocessing.Queue()

    split_rows = distribute_rows(sheet.rows)

    processes = []
    for rows in split_rows:
        if not rows:
            continue
        p = multiprocessing.Process(target=worker, args=(queue, rows, template_file))
        processes.append(p)
        p.start()

    for p in processes:
        p.join()

    results: list[str] = []
    errors: list[str] = []
    while not queue.empty():
        res = queue.get()
        if isinstance(res, Error):
            errors.append(res)
        else:
            results.append(res)

    return not len(errors), ReportResult(
        errors=errors,
        reports=results,
    )
