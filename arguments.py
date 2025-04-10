import subprocess
from urllib.parse import urlparse

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
        from settings import get_settings

        settings = get_settings()
    except Exception as e:
        ok = False
        error(e)
        error("\nCreate settings.txt from settings_example.txt and fill with value")
        return

    try:
        result = subprocess.run(
            [settings.libre_office_path, "--version"], capture_output=True, text=True
        )
        if result.returncode:
            ok = False
    except FileNotFoundError:
        ok = False
        error("Libre Office not found in path")

    return ok
