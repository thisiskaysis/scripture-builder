"""
pro_builder.py
--------------
Generates a ProPresenter 7 .pro file from a list of formatted slide payloads.

Strategy: clone the template binary (__SCRIPTURE.pro) for each slide,
surgically replace the two RTF content fields (MAIN SCRIPTURE REF and
MAIN SCRIPTURE TEXT), regenerate per-slide UUIDs, then assemble all
slides into a single .pro file with correct protobuf framing.

Each slide payload is a dict:
    {
        'ref':  'John 3:16 (NIV)',
        'text': 'For God so loved the world...',
    }
"""

import os
import re
import sys
import uuid
import struct

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------

def _get_template_path() -> str:
    """
    Locate __SCRIPTURE.pro whether running in development or bundled
    by PyInstaller (where sys._MEIPASS points to the temp bundle dir).
    """
    if getattr(sys, 'frozen', False):
        base = sys._MEIPASS
    else:
        base = os.path.dirname(__file__)
    return os.path.join(base, '__SCRIPTURE.pro')

TEMPLATE_PATH = _get_template_path()


# ---------------------------------------------------------------------------
# Protobuf primitives
# ---------------------------------------------------------------------------

def encode_varint(n: int) -> bytes:
    """Encode a non-negative integer as a protobuf varint."""
    parts = []
    while True:
        b = n & 0x7F
        n >>= 7
        if n:
            parts.append(b | 0x80)
        else:
            parts.append(b)
            break
    return bytes(parts)


def read_varint(data: bytes, pos: int) -> tuple[int, int]:
    """Read a varint from data starting at pos. Returns (value, new_pos)."""
    result = 0
    shift = 0
    while pos < len(data):
        b = data[pos]
        pos += 1
        result |= (b & 0x7F) << shift
        if not (b & 0x80):
            break
        shift += 7
    return result, pos


def read_length_delimited(data: bytes, pos: int) -> tuple[bytes, int]:
    length, pos = read_varint(data, pos)
    return data[pos:pos + length], pos + length


def wrap_field(field_number: int, wire_type: int, content: bytes) -> bytes:
    """Wrap content in a protobuf field tag + length (wire type 2 only)."""
    tag = (field_number << 3) | wire_type
    if wire_type == 2:
        return encode_varint(tag) + encode_varint(len(content)) + content
    raise ValueError(f"Only wire type 2 supported here, got {wire_type}")


def wrap_ld(field_number: int, content: bytes) -> bytes:
    """Shorthand: wrap bytes as a length-delimited (wire type 2) field."""
    return wrap_field(field_number, 2, content)


# ---------------------------------------------------------------------------
# RTF builders
# ---------------------------------------------------------------------------

# Unicode superscript digits that ARE in Windows-1252
_W1252_SUPER = {'1': 'b9', '2': 'b2', '3': 'b3'}

SUPERSCRIPT_CHARS = {
    '⁰': '0', '¹': '1', '²': '2', '³': '3', '⁴': '4',
    '⁵': '5', '⁶': '6', '⁷': '7', '⁸': '8', '⁹': '9',
}


def superscript_to_rtf(sup_str: str) -> str:
    """
    Convert a unicode superscript string (e.g. '²¹') to RTF.
    Uses Windows-1252 escapes for ¹²³ and \\super for everything else.
    e.g. '²¹' → "\\'b2\\'b9"
         '¹⁰' → "\\'b910"  (\\super wraps the whole number cleanly)
    """
    # Extract the digit string from superscript chars
    digits = ''.join(SUPERSCRIPT_CHARS.get(c, c) for c in sup_str)

    # If all digits are encodable as W1252 superscripts, use escapes
    if all(d in _W1252_SUPER for d in digits):
        return ''.join(f"\\'{_W1252_SUPER[d]}" for d in digits)

    # Otherwise use RTF \super command (standard, ProPresenter supports it)
    return '{\\super ' + digits + '}'


def text_to_rtf_body(text: str) -> str:
    """
    Convert plain text (with unicode superscript verse markers) to RTF body.

    Handles:
    - Unicode superscript digits → RTF escapes or \\super
    - Special RTF chars (\\, {, }) → escaped
    - Smart quotes and em-dashes → RTF escapes
    - Regular text → passed through
    """
    rtf = []
    i = 0
    while i < len(text):
        c = text[i]

        # Collect a run of superscript chars
        if c in SUPERSCRIPT_CHARS:
            sup_run = ''
            while i < len(text) and text[i] in SUPERSCRIPT_CHARS:
                sup_run += text[i]
                i += 1
            rtf.append(superscript_to_rtf(sup_run))
            continue

        # RTF special chars
        if c == '\\':
            rtf.append('\\\\')
        elif c == '{':
            rtf.append('\\{')
        elif c == '}':
            rtf.append('\\}')
        # Smart quotes
        elif c == '\u2018' or c == '\u2019':  # ' '
            rtf.append("\\'92" if c == '\u2019' else "\\'91")
        elif c == '\u201c':  # "
            rtf.append("\\'93")
        elif c == '\u201d':  # "
            rtf.append("\\'94")
        # Em dash
        elif c == '\u2014':
            rtf.append("\\'97")
        # En dash
        elif c == '\u2013':
            rtf.append("\\'96")
        # Ellipsis
        elif c == '\u2026':
            rtf.append("\\'85")
        # Non-ASCII — encode as RTF unicode escape
        elif ord(c) > 127:
            rtf.append(f'\\uc0\\u{ord(c)} ')
        else:
            rtf.append(c)

        i += 1

    return ''.join(rtf)


# RTF template for MAIN SCRIPTURE REF (element 1)
# Matches the exact structure from the template file
_RTF_REF_TEMPLATE = (
    '{{\\rtf1\\ansi\\ansicpg1252\\cocoartf2868\n'
    '\\cocoatextscaling0\\cocoaplatform0'
    '{{\\fonttbl\\f0\\fnil\\fcharset0 HelveticaNeue-Bold;'
    '\\f1\\fnil\\fcharset0 AppleColorEmoji;}}\n'
    '{{\\colortbl;\\red255\\green255\\blue255;\\red255\\green255\\blue255;}}\n'
    '{{\\*\\expandedcolortbl;;\\cssrgb\\c100000\\c100000\\c100000;}}\n'
    '\\deftab1680\n'
    '\\pard\\pardeftab1680\\sl192\\slmult1\\pardirnatural\\qc\\partightenfactor0\n'
    '\n'
    '\\f0\\b\\fs100 \\cf2 \\kerning1\\expnd-4\\expndtw-20\n'
    '\\CocoaLigature0 {ref_text}}}'
)

# RTF template for MAIN SCRIPTURE TEXT (element 2)
_RTF_TEXT_TEMPLATE = (
    '{{\\rtf1\\ansi\\ansicpg1252\\cocoartf2868\n'
    '\\cocoatextscaling0\\cocoaplatform0'
    '{{\\fonttbl\\f0\\fnil\\fcharset0 HelveticaNeue-Medium;'
    '\\f1\\fnil\\fcharset0 AppleColorEmoji;}}\n'
    '{{\\colortbl;\\red255\\green255\\blue255;\\red255\\green255\\blue255;}}\n'
    '{{\\*\\expandedcolortbl;;\\cssrgb\\c100000\\c100000\\c100000;}}\n'
    '\\deftab1680\n'
    '\\pard\\pardeftab1680\\sl192\\slmult1\\pardirnatural\\qc\\partightenfactor0\n'
    '\n'
    '\\f0\\fs64 \\cf2 \\kerning1\\expnd-4\\expndtw-20\n'
    '\\CocoaLigature0 {body_text}}}'
)

# Unique byte signatures used to locate each RTF field in the binary
_RTF_REF_SIGNATURE = (
    b'{\\rtf1\\ansi\\ansicpg1252\\cocoartf2868\n'
    b'\\cocoatextscaling0\\cocoaplatform0'
    b'{\\fonttbl\\f0\\fnil\\fcharset0 HelveticaNeue-Bold;'
    b'\\f1\\fnil\\fcharset0 AppleColorEmoji;}'
)

_RTF_TEXT_SIGNATURE = (
    b'{\\rtf1\\ansi\\ansicpg1252\\cocoartf2868\n'
    b'\\cocoatextscaling0\\cocoaplatform0'
    b'{\\fonttbl\\f0\\fnil\\fcharset0 HelveticaNeue-Medium;'
    b'\\f1\\fnil\\fcharset0 AppleColorEmoji;}'
)


def build_rtf_ref(ref_text: str) -> bytes:
    """Build RTF bytes for the MAIN SCRIPTURE REF field."""
    rtf_body = text_to_rtf_body(ref_text)
    rtf_str = _RTF_REF_TEMPLATE.format(ref_text=rtf_body)
    return rtf_str.encode('ascii', errors='replace')


def build_rtf_text(body_text: str) -> bytes:
    """Build RTF bytes for the MAIN SCRIPTURE TEXT field."""
    rtf_body = text_to_rtf_body(body_text)
    rtf_str = _RTF_TEXT_TEMPLATE.format(body_text=rtf_body)
    return rtf_str.encode('ascii', errors='replace')


# ---------------------------------------------------------------------------
# UUID handling
# ---------------------------------------------------------------------------

# UUIDs that must stay stable — they are cross-referenced by linked elements
_STABLE_UUIDS = {
    'CEFA709F-B3F8-4250-A71D-0CE854E721C1',  # MAIN SCRIPTURE REF master
    '2BA0A173-4AFF-40D6-A156-A62A18DFCED2',  # MAIN SCRIPTURE TEXT master
}

# All other UUIDs in a slide get regenerated per slide
_UUID_PATTERN = re.compile(
    rb'[0-9A-F]{8}-[0-9A-F]{4}-[0-9A-F]{4}-[0-9A-F]{4}-[0-9A-F]{12}'
)


def new_uuid() -> str:
    return str(uuid.uuid4()).upper()


def regenerate_slide_uuids(slide_data: bytes) -> bytes:
    """
    Replace all non-stable UUIDs in a slide blob with fresh UUIDs.
    Stable UUIDs (master content refs) are preserved unchanged.
    """
    # Build a mapping of old UUID → new UUID for this slide
    seen = {}
    for m in _UUID_PATTERN.finditer(slide_data):
        uid = m.group().decode()
        if uid not in _STABLE_UUIDS and uid not in seen:
            seen[uid] = new_uuid()

    result = slide_data
    for old, new in seen.items():
        result = result.replace(old.encode(), new.encode())
    return result


# ---------------------------------------------------------------------------
# RTF field replacement
# ---------------------------------------------------------------------------

def find_rtf_field_bounds(data: bytes, signature: bytes) -> tuple[int, int]:
    """
    Locate an RTF field in the binary and return (tag_pos, content_end).

    The field is a protobuf length-delimited value:
        [tag byte: 0x2a][length varint][RTF content]

    We find content_start via the signature, then walk backwards to find
    the length varint (1-5 bytes), using the decoded length to find content_end.

    Returns (tag_pos, content_end) so the entire field can be replaced.
    """
    content_start = data.find(signature)
    if content_start == -1:
        raise ValueError(f'RTF signature not found: {signature[:40]}')

    # Walk backwards from content_start trying varint lengths 1-5
    for varint_len in range(1, 6):
        varint_start = content_start - varint_len
        if varint_start < 1:
            continue
        val, end = read_varint(data, varint_start)
        if end == content_start:
            # Verify the tag byte immediately before the varint is 0x2a
            tag_pos = varint_start - 1
            if data[tag_pos] == 0x2a:
                content_end = content_start + val
                return tag_pos, content_end

    raise ValueError('Could not locate RTF field boundaries')


def replace_rtf_field(data: bytes, signature: bytes, new_rtf: bytes) -> bytes:
    """
    Replace an RTF field in the binary with new RTF content.
    Correctly rebuilds the protobuf tag + length varint + content.
    """
    tag_pos, content_end = find_rtf_field_bounds(data, signature)
    # Rebuild: tag (0x2a) + new length varint + new content
    new_field = bytes([0x2a]) + encode_varint(len(new_rtf)) + new_rtf
    return data[:tag_pos] + new_field + data[content_end:]


# ---------------------------------------------------------------------------
# Slide blob extraction
# ---------------------------------------------------------------------------

def extract_all_fields_with_pos(data: bytes) -> list:
    """Extract all protobuf fields with their byte positions."""
    fields = []
    pos = 0
    while pos < len(data):
        try:
            start = pos
            tag, new_pos = read_varint(data, pos)
            fn = tag >> 3
            wt = tag & 0x7
            if wt == 0:
                val, new_pos = read_varint(data, new_pos)
            elif wt == 2:
                val, new_pos = read_length_delimited(data, new_pos)
            elif wt == 1:
                val = data[new_pos:new_pos + 8]
                new_pos += 8
            elif wt == 5:
                val = data[new_pos:new_pos + 4]
                new_pos += 4
            else:
                break
            fields.append((fn, wt, val, start, new_pos))
            pos = new_pos
        except Exception:
            break
    return fields


def extract_template_parts(template_data: bytes) -> dict:
    """
    Navigate the template binary and extract all the parts we need:
    - The slide blob (to clone per scripture)
    - The bytes before and after the slide section (to reassemble)
    - The F2 trailing bytes (the '\"\\x02\\x18\\x01' suffix after the slide)
    """
    root_fields = extract_all_fields_with_pos(template_data)

    # F13: the presentation block
    f13_entry = next(e for e in root_fields if e[0] == 13)
    f13_data = f13_entry[2]

    f13_fields = extract_all_fields_with_pos(f13_data)
    f13_10s = [e for e in f13_fields if e[0] == 10]

    # First F10: the main slide group
    mc_data = f13_10s[0][2]
    mc_fields = extract_all_fields_with_pos(mc_data)

    # F23: the slides blob
    f23_entry = next(e for e in mc_fields if e[0] == 23)
    f23_data = f23_entry[2]
    f23_fields = extract_all_fields_with_pos(f23_data)

    # F2: the slides list container
    f2_entry = next(e for e in f23_fields if e[0] == 2)
    f2_data = f2_entry[2]
    f2_fields = extract_all_fields_with_pos(f2_data)

    # The single slide (F1 in F2)
    slide_entry = next(e for e in f2_fields if e[0] == 1)
    slide_data = slide_entry[2]
    slide_end_in_f2 = slide_entry[4]

    # Trailing bytes in F2 after the slide (e.g. b'"\x02\x18\x01')
    f2_trailer = f2_data[slide_end_in_f2:]

    # Other fields in mc_data (before F23) — needed to rebuild mc
    mc_prefix_fields = [e for e in mc_fields if e[0] != 23]

    # Other fields in f13 (F10[1], F10[2], F12, etc.) — needed to rebuild f13
    f13_other_10s = f13_10s[1:]  # arrangement and background groups
    f13_non_10_fields = [e for e in f13_fields if e[0] != 10]

    # Root prefix (everything before F13) and suffix (everything after F13)
    f13_start = f13_entry[3]
    f13_full_end = f13_entry[4]
    root_prefix = template_data[:f13_start]
    root_suffix = template_data[f13_full_end:]

    return {
        'slide_data': slide_data,
        'f2_trailer': f2_trailer,
        'mc_prefix_fields': mc_prefix_fields,   # raw field entries
        'mc_data': mc_data,                      # full mc bytes for prefix rebuild
        'f23_data': f23_data,                    # for non-F2 fields
        'f13_other_10s': f13_other_10s,
        'f13_non_10_fields': f13_non_10_fields,
        'f13_data': f13_data,
        'root_prefix': root_prefix,
        'root_suffix': root_suffix,
    }


# ---------------------------------------------------------------------------
# Binary reassembly helpers
# ---------------------------------------------------------------------------

def field_bytes(entry: tuple) -> bytes:
    """Re-serialise a parsed field entry back to bytes."""
    fn, wt, val, start, end = entry
    tag = encode_varint((fn << 3) | wt)
    if wt == 0:
        return tag + encode_varint(val)
    elif wt == 2:
        return tag + encode_varint(len(val)) + val
    elif wt == 1:
        return tag + val  # 8 bytes
    elif wt == 5:
        return tag + val  # 4 bytes
    return b''


def rebuild_from_parts(parts: dict, slide_blobs: list[bytes]) -> bytes:
    """
    Reassemble the full .pro binary from template parts and new slide blobs.
    """
    # 1. Build F2 content: multiple F1 slides + trailer
    f2_content = b''
    for blob in slide_blobs:
        f2_content += wrap_ld(1, blob)
    f2_content += parts['f2_trailer']

    # 2. Wrap F2 in F23
    f23_content = wrap_ld(2, f2_content)

    # 3. Rebuild mc (main container) = prefix fields + F23
    mc_prefix_bytes = b''
    mc_all = extract_all_fields_with_pos(parts['mc_data'])
    for entry in mc_all:
        if entry[0] != 23:  # skip F23, we have the new one
            mc_prefix_bytes += field_bytes(entry)
    mc_content = mc_prefix_bytes + wrap_ld(23, f23_content)

    # 4. Rebuild F13 = non-F10 fields + F10[0] (new mc) + F10[1] + F10[2] + F12
    f13_all = extract_all_fields_with_pos(parts['f13_data'])
    f13_content = b''
    f10_written = False
    for entry in f13_all:
        if entry[0] == 10 and not f10_written:
            # First F10: our new mc
            f13_content += wrap_ld(10, mc_content)
            f10_written = True
        else:
            f13_content += field_bytes(entry)

    # 5. Wrap F13 in root
    new_f13_field = wrap_ld(13, f13_content)
    return parts['root_prefix'] + new_f13_field + parts['root_suffix']


# ---------------------------------------------------------------------------
# Per-slide builder
# ---------------------------------------------------------------------------

def build_slide(template_slide: bytes, ref: str, text: str) -> bytes:
    """
    Clone the template slide, inject new RTF content, regenerate UUIDs.
    """
    slide = template_slide

    # Build new RTF for each field
    new_rtf_ref = build_rtf_ref(ref)
    new_rtf_text = build_rtf_text(text)

    # Replace RTF content (ref first since it's at a lower byte offset)
    slide = replace_rtf_field(slide, _RTF_REF_SIGNATURE, new_rtf_ref)
    slide = replace_rtf_field(slide, _RTF_TEXT_SIGNATURE, new_rtf_text)

    # Regenerate per-slide UUIDs
    slide = regenerate_slide_uuids(slide)

    return slide


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def generate_pro_file(
    slide_payloads: list[dict],
    output_path: str,
    template_path: str = TEMPLATE_PATH,
) -> str:
    """
    Generate a .pro file from a list of slide payloads.

    Args:
        slide_payloads: list of {'ref': str, 'text': str} dicts
        output_path:    where to write the .pro file
        template_path:  path to __SCRIPTURE.pro template

    Returns:
        The output path.
    """
    if not slide_payloads:
        raise ValueError('No slide payloads provided')

    if not os.path.exists(template_path):
        raise FileNotFoundError(f'Template not found: {template_path}')

    with open(template_path, 'rb') as f:
        template_data = f.read()

    parts = extract_template_parts(template_data)

    slide_blobs = []
    for payload in slide_payloads:
        blob = build_slide(
            parts['slide_data'],
            ref=payload['ref'],
            text=payload['text'],
        )
        slide_blobs.append(blob)

    output_data = rebuild_from_parts(parts, slide_blobs)

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, 'wb') as f:
        f.write(output_data)

    return output_path