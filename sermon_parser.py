import re
from docx import Document

# Matches standard scripture references like:
# John 3:16, Psalm 23:1-3, 1 Corinthians 13:4-7
SCRIPTURE_REF_PATTERN = re.compile(
    r'\b(\d?\s?[A-Z][a-zA-Z]+(?:\s[A-Z][a-zA-Z]+)?)\s(\d+):(\d+(?:-\d+)?)\b'
)

# Matches translation labels like (NIV), (ESV), (KJV), (NKJV) etc
TRANSLATION_PATTERN = re.compile(
    r'\(([A-Z]{2,5})\)'
)

def extract_text_from_docx(filepath):
    """Extract all paragraphs from a .docx file as a list of strings."""
    doc = Document(filepath)
    return [para.text.strip() for para in doc.paragraphs if para.text.strip()]

def find_scriptures(paragraphs):
    """
    Scan paragraphs for scripture references and extract:
    - The reference (e.g. John 3:16)
    - The scripture text (the paragraph(s) that follow)
    - The translation (if mentioned)

    Returns a list of dicts.
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
            ref = f"{book} {chapter}:{verse}"

            # Check for translation in the same paragraph
            translation_match = TRANSLATION_PATTERN.search(para)
            translation = translation_match.group(1) if translation_match else None

            # The scripture text might be:
            # (a) in the same paragraph after the reference, or
            # (b) in the next paragraph(s)

            # Try same paragraph first — strip the reference from the front
            inline_text = para[match.end():].strip()
            # Remove any translation label from inline text
            inline_text = TRANSLATION_PATTERN.sub('', inline_text).strip()
            # Remove leading punctuation/dashes
            inline_text = re.sub(r'^[\-–—:]+\s*', '', inline_text).strip()

            if inline_text and len(inline_text) > 10:
                # Scripture text is in the same paragraph
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
                    # If this paragraph looks like a full sentence, stop here
                    if next_para.endswith(('.', '"', '\u201d')):
                        break
                    j += 1

                scripture_text = scripture_text.strip()

            if scripture_text:
                entry = {
                    'ref': ref,
                    'text': scripture_text,
                    'translation': translation,
                    'screens': ['left_pillar', 'right_pillar']  # sensible default
                }
                scriptures.append(entry)

        i += 1

    return scriptures


def parse_sermon_doc(filepath):
    """
    Main entry point. Takes a .docx filepath,
    returns a list of scripture entries ready for the UI.
    """
    paragraphs = extract_text_from_docx(filepath)
    scriptures = find_scriptures(paragraphs)
    return scriptures