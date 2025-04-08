import multiprocessing
import os
import tempfile

import pypandoc
import typer

from common import File, Sheet, Template
from log import error, log
from reader import read_template
from settings import settings


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

    return convert_to_pdf(
        template,
        pdf_file_name=get_pdf_file_name(row, template)
    )


def worker(
    queue: multiprocessing.Queue,
    rows: list[dict[str, str]],
    template_file: File,
):
    for row in rows:
        ok, template = read_template(template_file)
        if not ok:
            error(template)
            raise typer.Exit(1)

        pdf_path = create_pdf(
            row,
            template,
        )

        queue.put(pdf_path)


def run_format_job(sheet: Sheet, template_file: File):
    queue = multiprocessing.Queue()

    chunk_size = len(sheet.rows) // multiprocessing.cpu_count()
    split_rows = [
        sheet.rows[i : i + chunk_size] for i in range(0, len(sheet.rows), chunk_size)
    ]

    processes = []
    for rows in split_rows:
        p = multiprocessing.Process(target=worker, args=(queue, rows, template_file))
        processes.append(p)
        p.start()

    for p in processes:
        p.join()

    while not queue.empty():
        log(queue.get())
