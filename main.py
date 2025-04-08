import os
from typing import Annotated

import typer

from arguments import parse_xlxs_path_argument, validate_setup
from common import LoadFileArgument
from loader import load_file
from log import error, log
from reader import read_rows, read_template
from settings import get_settings
from uploader import upload_reports
from worker import run_format_job

app = typer.Typer()


@app.command()
def run(
    xlsx: Annotated[LoadFileArgument, typer.Argument(parser=parse_xlxs_path_argument)],
    template: str,
):
    if not validate_setup():
        raise typer.Exit(1)

    log("Opening Template docx File")
    ok, template_file = load_file(LoadFileArgument(path=template))
    if not ok:
        error(template_file)
        raise typer.Exit(1)

    ok, read_template_res = read_template(template_file)
    if not ok:
        error(read_template_res)
        raise typer.Exit(1)

    log("Opening xlsx file")
    ok, res = load_file(xlsx)
    if not ok:
        error(res)
        raise typer.Exit(1)

    log("Reading rows")
    ok, sheet = read_rows(res)
    if not ok:
        error(sheet)
        raise typer.Exit(1)

    log(f"Found {len(sheet.rows)} rows")

    settings = get_settings()
    os.makedirs(settings.output_dir, exist_ok=True)

    log(f"Generating PDFs. Output dir: \"{settings.output_dir}\"")
    ok, report_results = run_format_job(
        sheet=sheet,
        template_file=template_file,
    )
    if not ok:
        error(f"Failed to generate reports. Got {len(report_results.errors)} errors")
        for each in report_results.errors:
            error(f"\t{each.msg}")
        
        if not report_results.reports:
            raise typer.Exit(1)

    log("Uploading PDFs to Yandex Disk.")
    ok, upload_results = upload_reports(report_results)
    if not ok:
        error("Failed to upload reports")
        for each in upload_results:
            error(f"\t {each.msg}")
    
    log("[green]Done[/green]")


if __name__ == "__main__":
    app()
