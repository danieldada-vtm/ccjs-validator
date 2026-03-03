from __future__ import annotations

import re
from pathlib import Path

import fitz  # PyMuPDF


class PDFExtractionError(Exception):
    pass


class UCRManualExtractor:
    """Extracts and cleans text from the UCR Manual PDF."""

    def __init__(self, pdf_path: str | Path) -> None:
        self.pdf_path = Path(pdf_path)
        if not self.pdf_path.exists():
            raise PDFExtractionError(f"PDF not found: {self.pdf_path}")
        self._doc: fitz.Document | None = None

    def _open(self) -> fitz.Document:
        if self._doc is None:
            try:
                self._doc = fitz.open(str(self.pdf_path))
            except Exception as e:
                raise PDFExtractionError(f"Failed to open PDF: {e}") from e
        return self._doc

    def close(self) -> None:
        if self._doc is not None:
            self._doc.close()
            self._doc = None

    def __enter__(self) -> UCRManualExtractor:
        self._open()
        return self

    def __exit__(self, *_) -> None:
        self.close()

    @property
    def page_count(self) -> int:
        return len(self._open())

    def extract_page(self, page_number: int) -> str:
        """Extract and clean text from a single page (0-indexed)."""
        doc = self._open()
        if page_number < 0 or page_number >= len(doc):
            raise PDFExtractionError(
                f"Page {page_number} out of range (0–{len(doc) - 1})"
            )
        page = doc[page_number]
        return self._clean(page.get_text())

    def extract_pages(self, start: int = 0, end: int | None = None) -> str:
        """Extract and clean text from a page range (inclusive, 0-indexed).

        Args:
            start: First page to extract (0-indexed, default 0).
            end:   Last page to extract inclusive (0-indexed, default last page).
        """
        doc = self._open()
        total = len(doc)
        end = total - 1 if end is None else min(end, total - 1)
        if start < 0 or start > end:
            raise PDFExtractionError(
                f"Invalid page range {start}–{end} (document has {total} pages)"
            )
        parts: list[str] = []
        for i in range(start, end + 1):
            text = self._clean(doc[i].get_text())
            if text:
                parts.append(text)
        return "\n\n".join(parts)

    def extract_full(self) -> str:
        """Extract and clean the entire document."""
        return self.extract_pages()

    # ------------------------------------------------------------------
    # Text cleaning
    # ------------------------------------------------------------------

    @staticmethod
    def _clean(text: str) -> str:
        """Remove PDF artifacts and normalise whitespace."""
        # Drop form-feed characters inserted between pages
        text = text.replace("\f", "\n")

        # Collapse sequences of blank lines to at most two newlines
        text = re.sub(r"\n{3,}", "\n\n", text)

        # Strip trailing whitespace on each line
        lines = [line.rstrip() for line in text.split("\n")]

        # Drop lines that are purely page-number artifacts:
        # e.g. a line that is just a number or a lone dash
        cleaned: list[str] = []
        for line in lines:
            stripped = line.strip()
            if re.fullmatch(r"\d{1,4}", stripped):
                continue  # bare page number
            cleaned.append(line)

        return "\n".join(cleaned).strip()
