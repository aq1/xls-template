from dataclasses import dataclass
from typing import Any

from docx import Document


@dataclass
class File:
    content: bytes


@dataclass
class Sheet:
    rows: list[dict[str, str]]


@dataclass
class Template:
    doc: Document


@dataclass
class LoadFileArgument:
    google_doc_id: str | None = None
    path: str | None = None


@dataclass
class ReportResult:
    errors: list[str]
    reports: list[str]


@dataclass
class Error:
    msg: str
