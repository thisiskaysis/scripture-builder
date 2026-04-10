"""
formatter.py
------------
Converts raw parsed scripture entries into a list of slide payloads ready
for .pro binary injection.

Each input entry (from parse_sermon_doc) is a dict:
    {
        'ref':         'John 3:16',
        'text':        '¹ For God so loved the world...',  # raw verse text
        'translation': 'NIV',   # or None
    }

Each output slide payload is a dict:
    {
        'ref':  'John 3:16 (NIV)',   # formatted reference line — appears on every slide
        'text': '¹ For God so loved...',  # verse text chunk for this slide
    }
"""

import re

# ---------------------------------------------------------------------------
# Unicode superscript digits
# ---------------------------------------------------------------------------

SUPERSCRIPT_DIGITS = {
    '0': '⁰', '1': '¹', '2': '²', '3': '³', '4': '⁴',
    '5': '⁵', '6': '⁶', '7': '⁷', '8': '⁸', '9': '⁹',
}

def to_superscript(n: int) -> str:
    """Convert an integer to its unicode superscript string. e.g. 12 → '¹²'"""
    return ''.join(SUPERSCRIPT_DIGITS[d] for d in str(n))


# ---------------------------------------------------------------------------
# Reference formatting
# ---------------------------------------------------------------------------

def format_reference(ref: str, translation: str | None) -> str:
    """
    Format a reference string with translation.
    e.g. 'john 3:16' + 'NIV' → 'John 3:16 (NIV)'
         '1 corinthians 13:4-7' + None → '1 Corinthians 13:4-7'
         'song of solomon 1:1' → 'Song of Solomon 1:1'
    """
    # Words that should stay lowercase unless they're the first word
    MINOR_WORDS = {'of', 'the', 'and', 'in', 'a', 'an', 'to', 'for', 'with'}

    parts = ref.strip().split()
    cased = []
    for i, p in enumerate(parts):
        if p[0].isdigit():
            # Leading book number (e.g. '1', '2', '3') — keep as-is
            cased.append(p)
        elif ':' in p or '-' in p:
            # Chapter:verse portion — keep exactly as-is
            cased.append(p)
        elif p.lower() in MINOR_WORDS and i != 0 and not cased[-1][0].isdigit():
            # Minor word not at start — lowercase
            cased.append(p.lower())
        else:
            cased.append(p.capitalize())
    formatted = ' '.join(cased)
    if translation:
        formatted += f' ({translation.upper()})'
    return formatted


# ---------------------------------------------------------------------------
# Verse parsing — split raw text into numbered verse chunks
# ---------------------------------------------------------------------------

# Matches a verse number at the start or after whitespace:
# handles plain digits like "1 " or "12 " that precede verse text
_VERSE_NUM_RE = re.compile(r'(?<!\w)(\d+)\s+')

def parse_verses(text: str) -> list[tuple[int | None, str]]:
    """
    Parse raw verse text into a list of (verse_number, verse_text) tuples.

    Handles input formats:
      - Plain numbered: "1 Blessed are... 2 Blessed are those..."
      - Already superscripted: "¹ Blessed are... ² Blessed are those..."
      - Single verse (no numbers): "For God so loved..."

    Returns:
      [(1, 'Blessed are...'), (2, 'Blessed are those...'), ...]
      or [(None, 'For God so loved...')] for a single unnumbered verse.
    """
    # First, normalise any existing unicode superscripts back to plain digits
    # so we have one consistent format to work with
    text = normalise_superscripts(text)

    # Strip and collapse internal line breaks / multiple spaces
    text = re.sub(r'\s+', ' ', text).strip()

    # Find all verse number positions
    matches = list(re.finditer(r'(?:^|\s)(\d+)\s+', text))

    if not matches:
        return [(None, text)]

    verses = []
    for i, m in enumerate(matches):
        verse_num = int(m.group(1))
        content_start = m.end()
        content_end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        verse_text = text[content_start:content_end].strip()
        verses.append((verse_num, verse_text))

    # If nothing useful was parsed (e.g. a reference number was mistaken
    # for a verse number), fall back to returning the whole text
    if not verses or all(v == '' for _, v in verses):
        return [(None, text)]

    return verses


def normalise_superscripts(text: str) -> str:
    """Convert unicode superscript digits back to plain digits followed by space."""
    reverse = {v: k for k, v in SUPERSCRIPT_DIGITS.items()}
    result = []
    i = 0
    while i < len(text):
        c = text[i]
        if c in reverse:
            # Collect consecutive superscript digits
            num_str = ''
            while i < len(text) and text[i] in reverse:
                num_str += reverse[text[i]]
                i += 1
            # Skip any trailing space that was part of the superscript format
            if i < len(text) and text[i] == ' ':
                i += 1
            result.append(num_str + ' ')
        else:
            result.append(c)
            i += 1
    return ''.join(result)


# ---------------------------------------------------------------------------
# Text splitting — the core logic
# ---------------------------------------------------------------------------

MAX_CHARS = 280

# Sentence-ending punctuation
_SENTENCE_END_RE = re.compile(r'[.!?]["\u201d]?\s+')
# Logical break punctuation (lower priority)
_LOGICAL_BREAK_RE = re.compile(r'[,;\u2014]\s+')  # comma, semicolon, em-dash


def find_best_split(text: str, limit: int = MAX_CHARS) -> int:
    """
    Find the best character index to split `text` at or before `limit`.

    Priority:
      1. Sentence end (.  !  ?) — split AFTER the punctuation + space
      2. Logical break (, ; —)  — split AFTER the punctuation + space
      3. Word boundary          — split at last space before limit
      4. Hard limit             — split at limit (should never reach mid-word
                                  because priority 3 always finds a space)

    Returns the split index (text[:index] is slide 1, text[index:] is slide 2).
    """
    if len(text) <= limit:
        return len(text)

    search_region = text[:limit + 1]  # +1 to catch a break right at limit

    # 1. Sentence end — find the last one within limit
    best = None
    for m in _SENTENCE_END_RE.finditer(search_region):
        end = m.end()
        if end <= limit:
            best = end
    if best:
        return best

    # 2. Logical break — last one within limit
    for m in _LOGICAL_BREAK_RE.finditer(search_region):
        end = m.end()
        if end <= limit:
            best = end
    if best:
        return best

    # 3. Word boundary — last space at or before limit
    idx = search_region.rfind(' ', 0, limit)
    if idx != -1:
        return idx + 1  # split after the space so next chunk doesn't start with space

    # 4. Hard limit (should be unreachable for normal prose)
    return limit


def build_slide_chunks(
    verses: list[tuple[int | None, str]],
    is_multi_verse: bool,
    limit: int = MAX_CHARS,
) -> list[str]:
    """
    Given a list of (verse_num, verse_text) tuples, produce a list of
    text strings — one per slide — each within `limit` characters.

    Rules:
      - Prefer to break at verse boundaries (start of a new verse)
      - Fall back to sentence/logical/word boundary within a verse
      - Superscript appears at the start of each verse, wherever it lands
      - Single-verse passages: no superscript
    """
    slides = []
    current = ''

    for verse_num, verse_text in verses:
        # Build the prefix for this verse
        if is_multi_verse and verse_num is not None:
            prefix = to_superscript(verse_num) + ' '
        else:
            prefix = ''

        verse_content = prefix + verse_text

        if not current:
            # Starting fresh — just start filling
            current = verse_content
        else:
            # Try to append this verse to the current slide
            candidate = current + ' ' + verse_content
            if len(candidate) <= limit:
                current = candidate
            else:
                # Verse boundary split — flush current, start new slide
                slides.append(current.strip())
                current = verse_content

        # Now handle the case where current itself exceeds limit
        # (a single verse chunk that is too long)
        while len(current) > limit:
            split_at = find_best_split(current, limit)
            slides.append(current[:split_at].strip())
            remainder = current[split_at:].strip()
            current = remainder

    if current.strip():
        slides.append(current.strip())

    return slides


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def format_scripture(entry: dict) -> list[dict]:
    """
    Take a single parsed scripture entry and return a list of slide payloads.

    Input:
        {
            'ref':         'John 3:16',
            'text':        '16 For God so loved the world...',
            'translation': 'NIV',
        }

    Output (one dict per slide):
        [
            {'ref': 'John 3:16 (NIV)', 'text': 'For God so loved the world...'},
        ]
    """
    ref_line = format_reference(entry['ref'], entry.get('translation'))
    raw_text = entry.get('text', '').strip()

    verses = parse_verses(raw_text)
    # Only use superscripts when the reference is a range (e.g. 3:16-18).
    # A single verse with a leading number like "16 For God..." must NOT get a superscript.
    ref_has_range = bool(re.search(r':\d+-\d+', entry['ref']))
    is_multi = len(verses) > 1 and ref_has_range

    chunks = build_slide_chunks(verses, is_multi_verse=is_multi)

    return [{'ref': ref_line, 'text': chunk} for chunk in chunks]


def format_all(entries: list[dict]) -> list[dict]:
    """
    Process a list of parsed scripture entries into a flat list of slide payloads.
    """
    slides = []
    for entry in entries:
        slides.extend(format_scripture(entry))
    return slides