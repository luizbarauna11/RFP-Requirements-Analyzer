"""Carregadores de documento. Formatos binários usam extras opcionais (pdf, docx)."""

from __future__ import annotations

import io
from pathlib import Path

SUPPORTED_EXTENSIONS = {".txt", ".md", ".pdf", ".docx"}


class UnsupportedDocumentError(ValueError):
    pass


def load_bytes(content: bytes, filename: str) -> str:
    ext = Path(filename).suffix.lower()
    if ext not in SUPPORTED_EXTENSIONS:
        raise UnsupportedDocumentError(f"Extensão '{ext}' não suportada. Use: {sorted(SUPPORTED_EXTENSIONS)}")
    if ext in {".txt", ".md"}:
        for encoding in ("utf-8-sig", "cp1252", "latin-1"):
            try:
                return content.decode(encoding)
            except UnicodeDecodeError:
                continue
    if ext == ".pdf":
        try:
            from pypdf import PdfReader
        except ImportError as exc:  # pragma: no cover
            raise UnsupportedDocumentError("Instale o extra: pip install 'rfp-analyzer[pdf]'") from exc
        reader = PdfReader(io.BytesIO(content))
        return "\n".join(page.extract_text() or "" for page in reader.pages)
    if ext == ".docx":
        try:
            import docx
        except ImportError as exc:  # pragma: no cover
            raise UnsupportedDocumentError("Instale o extra: pip install 'rfp-analyzer[docx]'") from exc
        document = docx.Document(io.BytesIO(content))
        return "\n".join(p.text for p in document.paragraphs)
    raise UnsupportedDocumentError(ext)  # pragma: no cover


def load_path(path: Path) -> str:
    return load_bytes(path.read_bytes(), path.name)
