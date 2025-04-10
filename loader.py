import os

import httpx

from common import File, LoadFileArgument
from log import log


def load_google_sheet(doc_id: LoadFileArgument):
    url = f"https://docs.google.com/spreadsheets/d/{doc_id.id}/export"
    params = {
        "format": "xlsx",
    }

    response = httpx.get(url, params=params)
    if not response.ok:
        return False, f"Failed to download google spreadsheet {response.status_code}"

    return True, File(
        content=response.content,
    )


def load_local_file(path: str):
    try:
        with open(path, "rb") as f:
            return True, File(
                content=f.read(),
            )
    except FileNotFoundError:
        return False, f"File {path} not found"


def load_file(input: LoadFileArgument) -> tuple[False, str] | tuple[True, File]:
    if input.google_doc_id:
        return load_google_sheet(input.google_doc_id)
    elif input.path:
        return load_local_file(input.path)

    return False, f"Bad input {input}"
