import concurrent.futures
import os
import subprocess
from dataclasses import dataclass

from common import File, Sheet
from python_docx_replace import docx_replace
from reader import read_template
from settings import Settings, get_settings


def convert_to_pdf(settings: Settings, docx_names: list[str]):
    subprocess.run(
        [
            settings.libre_office_path,
            "--headless",
            "--invisible",
            "--nocrashreport",
            "--nologo",
            "--nofirststartwizard",
            "--convert-to",
            "pdf",
            "--outdir",
            settings.output_dir,
        ]
        + docx_names,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        check=True,
    )


@dataclass
class Worker:
    template_file: File
    settings: Settings
    filename: str = ""

    @staticmethod
    def get_filename(row: dict[str, str], template: str):
        for old, new in row.items():
            template = template.replace("{{" + old + "}}", new)
        return template

    def generate_docx(self, row: dict[str, str]):
        import time, random;time.sleep(random.randint(1, 5))
        self.filename = self.get_filename(
            row=row,
            template=self.settings.pdf_name_template,
        )
        doc = read_template(self.template_file)[1].doc
        docx_replace(doc, **row)
        docx_name = os.path.join(self.settings.docx_output_dir, self.filename + ".docx")
        doc.save(docx_name)
        return docx_name


def run_format_job(sheet: Sheet, template_file: File):
    worker = Worker(template_file, settings=get_settings())
    with concurrent.futures.ProcessPoolExecutor() as executor:
        filenames = list(executor.map(worker.generate_docx, sheet.rows))

    return True, filenames


def run_pdf_converter(filenames: list[str]):
    settings = get_settings()
    convert_to_pdf(settings, filenames)

    def get_pdf_name(path: str):
        filename = os.path.split(path)[-1]
        filename, _ = os.path.splitext(filename)
        return os.path.join(settings.output_dir, filename + ".pdf")

    return True, [get_pdf_name(f) for f in filenames]
