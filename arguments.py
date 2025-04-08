import subprocess
from urllib.parse import urlparse
import importlib.util

import typer

from common import LoadFileArgument
from log import error


def parse_xlxs_path_argument(value: str):
    url = urlparse(value)
    if not (url.scheme and url.netloc):
        return LoadFileArgument(
            path=value,
        )

    if "docs.google" not in url.netloc:
        raise typer.BadParameter("Expected google docs url")

    if "/spreadsheets/d/" not in url.path:
        raise typer.BadParameter("Expected google docs spreadsheets url")

    try:
        return LoadFileArgument(google_doc_id=url.path.split("/")[3])
    except IndexError:
        raise typer.BadParameter(f"Could not extract file id from {url.path}")


def validate_setup():
    ok = True
    try:
        result = subprocess.run(["pandoc", "--version"], capture_output=True, text=True)
        if result.returncode:
            ok = False
    except FileNotFoundError:
        ok = False
        error(
            "Pandoc not found in path. Install it from here https://pandoc.org/installing.html"
        )

    try:
        result = subprocess.run(["pdflatex", "--version"], capture_output=True, text=True)
        if result.returncode:
            ok = False
    except FileNotFoundError:
        ok = False
        error(
            "pdflatex not found in path. Read instruction how to install it (MiKTeX) here https://pandoc.org/installing.html"
        )

    try:
        from settings import settings
    except Exception as e:
        ok = False
        error(e)
        error("Create settings.txt from settings_example.txt and fill with value")

    # return ok
    return ok
