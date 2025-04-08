from typing import Annotated

import typer

from arguments import parse_xlxs_path_argument, validate_setup
from common import LoadFileArgument
from loader import load_file
from log import error, log
from reader import read_rows, read_template
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

    log("Formatting documents")
    run_format_job(
        sheet=sheet,
        template_file=template_file,
    )


if __name__ == "__main__":
    app()
