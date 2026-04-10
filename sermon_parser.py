"""
sermon_parser.py
----------------
Parses sermon documents (.docx or .pdf) and extracts scripture references
along with their verse text and translation labels.

Supported formats:
    .docx  — via python-docx
    .pdf   — via pdfplumber (clean, exported PDFs only — not scanned)
"""

import re
import os

from docx import Document
import pdfplumber

# ---------------------------------------------------------------------------
# Patterns
# ---------------------------------------------------------------------------

# Matches standard scripture references like:
# John 3:16, Psalm 23:1-3, 1 Corinthians 13:4-7
SCRIPTURE_REF_PATTERN = re.compile(
    r'\b(\d?\s?[A-Z][a-zA-Z]+(?:\s[A-Z][a-zA-Z]+)?)\s(\d+):(\d+(?:-\d+)?)\b'
)

# Matches translation labels like (NIV), (ESV), (KJV), (NKJV) etc.
TRANSLATION_PATTERN = re.compile(
    r'\(([A-Z]{2,5})\)'
)


# ---------------------------------------------------------------------------
# Text extraction
# ---------------------------------------------------------------------------

def extract_text_from_docx(filepath: str) -> list[str]:
    """Extract all paragraphs from a .docx file as a list of strings."""
    doc = Document(filepath)
    return [para.text.strip() for para in doc.paragraphs if para.text.strip()]


def extract_text_from_pdf(filepath: str) -> list[str]:
    """
    Extract text from a clean (exported) PDF as a list of paragraph strings.

    Strategy:
    - Extract text page by page using pdfplumber
    - Split on newlines to approximate paragraphs
    - Strip and filter empty lines
    - Collapse lines that look like they continue the same sentence
      (i.e. don't end with punctuation) to avoid splitting verse text
      across multiple 'paragraphs' due to PDF line wrapping
    """
    lines = []

    with pdfplumber.open(filepath) as pdf:
        for page in pdf.pages:
            text = page.extract_text(x_tolerance=2, y_tolerance=2)
            if not text:
                continue
            for line in text.split('\n'):
                stripped = line.strip()
                if stripped:
                    lines.append(stripped)

    if not lines:
        return []

    # Rejoin wrapped lines: if a line doesn't end with sentence-final
    # punctuation and the next line doesn't look like a new reference or
    # heading, merge them. This reconstructs verse text split by PDF line
    # wrapping into single paragraphs for find_scriptures to handle.
    _SENTENCE_END = re.compile(r'[.!?"\u201d]\s*$')
    _LOOKS_LIKE_REF = re.compile(
        r'^\d?\s?[A-Z][a-zA-Z]+(?:\s[A-Z][a-zA-Z]+)?\s\d+:\d+'
    )

    paragraphs = []
    buffer = ''

    for line in lines:
        if not buffer:
            buffer = line
            continue

        # Start a new paragraph if this line looks like a scripture reference
        # or if the previous line ended with sentence-final punctuation
        if _LOOKS_LIKE_REF.match(line) or _SENTENCE_END.search(buffer):
            paragraphs.append(buffer)
            buffer = line
        else:
            # Continuation of the previous line — join with a space
            buffer = buffer + ' ' + line

    if buffer:
        paragraphs.append(buffer)

    return [p.strip() for p in paragraphs if p.strip()]


def extract_paragraphs(filepath: str) -> list[str]:
    """
    Dispatch to the correct extractor based on file extension.
    Returns a list of paragraph strings.
    """
    ext = os.path.splitext(filepath)[1].lower()
    if ext == '.docx':
        return extract_text_from_docx(filepath)
    elif ext == '.pdf':
        return extract_text_from_pdf(filepath)
    else:
        raise ValueError(f'Unsupported file type: {ext!r}. Use .docx or .pdf')


# ---------------------------------------------------------------------------
# Scripture extraction
# ---------------------------------------------------------------------------

def find_scriptures(paragraphs: list[str]) -> list[dict]:
    """
    Scan paragraphs for scripture references and extract:
    - The reference (e.g. 'John 3:16')
    - The scripture text (the paragraph(s) that follow)
    - The translation (if mentioned)

    Returns a list of dicts with keys: ref, text, translation, screens.
    """
    scriptures = []
    i = 0

    while i < len(paragraphs):
        para = paragraphs[i]
        match = SCRIPTURE_REF_PATTERN.search(para)

        if match:
            # Build the full reference string
            book = match.group(1).strip()
            chapter = match.group(2)
            verse = match.group(3)
            ref = f'{book} {chapter}:{verse}'

            # Check for translation in the same paragraph
            translation_match = TRANSLATION_PATTERN.search(para)
            translation = translation_match.group(1) if translation_match else None

            # Scripture text may be:
            # (a) in the same paragraph after the reference, or
            # (b) in the next paragraph(s)

            # Try same paragraph first — strip the reference from the front
            inline_text = para[match.end():].strip()
            inline_text = TRANSLATION_PATTERN.sub('', inline_text).strip()
            inline_text = re.sub(r'^[\-–—:]+\s*', '', inline_text).strip()

            if inline_text and len(inline_text) > 10:
                scripture_text = inline_text
            else:
                # Look at the next paragraph(s)
                scripture_text = ''
                j = i + 1
                while j < len(paragraphs):
                    next_para = paragraphs[j]
                    # Stop if we hit another scripture reference
                    if SCRIPTURE_REF_PATTERN.search(next_para):
                        break
                    # Stop if the paragraph is very short (likely a heading)
                    if len(next_para) < 5:
                        break
                    scripture_text += (' ' + next_para).strip()
                    # Stop if this paragraph ends a sentence
                    if next_para.endswith(('.', '"', '\u201d')):
                        break
                    j += 1

                scripture_text = scripture_text.strip()

            if scripture_text:
                scriptures.append({
                    'ref': ref,
                    'text': scripture_text,
                    'translation': translation,
                    'screens': ['left_pillar', 'right_pillar'],  # sensible default
                })

        i += 1

    return scriptures


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def parse_sermon_doc(filepath: str) -> list[dict]:
    """
    Main entry point. Accepts a .docx or .pdf filepath.
    Returns a list of scripture entries ready for the formatter.
    """
    paragraphs = extract_paragraphs(filepath)
    return find_scriptures(paragraphs)