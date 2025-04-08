from dataclasses import dataclass
from typing import Any

from docx import Document


@dataclass
class File:
    name: str
    content: bytes


@dataclass
class Sheet:
    rows: list[dict[str, str]]


@dataclass
class Template:
    doc: Document
    name: str


@dataclass
class LoadFileArgument:
    google_doc_id: str | None = None
    path: str | None = None
