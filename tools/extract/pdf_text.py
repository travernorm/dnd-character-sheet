#!/usr/bin/env python3
"""Pull the text out of a book PDF, one file per page, for building a content pack.

Writes packs/.text/<book-id>/p0001.txt ... The packs/ folder is git-ignored: book text
never goes in the repo. Needs pypdf (pip3 install --user pypdf).

Usage: python3 tools/extract/pdf_text.py <book.pdf> <book-id>
"""
import os, sys
from pypdf import PdfReader

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def main(pdf, book):
    out = os.path.join(ROOT, "packs", ".text", book)
    os.makedirs(out, exist_ok=True)
    r = PdfReader(pdf)
    empty = 0
    for i, page in enumerate(r.pages, 1):
        try:
            t = page.extract_text() or ""
        except Exception:
            t = ""
        empty += not t.strip()
        with open(os.path.join(out, "p%04d.txt" % i), "w", encoding="utf-8") as f:
            f.write(t)
    print("%s: %d pages, %d without text -> %s" % (book, len(r.pages), empty, os.path.relpath(out, ROOT)))


if __name__ == "__main__":
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    main(sys.argv[1], sys.argv[2])
