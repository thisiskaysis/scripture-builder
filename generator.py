"""
generator.py
------------
Orchestrates the full pipeline from formatted slide payloads to a .pro file.

Pipeline:
    app.py  →  generator.py  →  formatter.py  →  pro_builder.py  →  .pro file
"""

import os
import re
from datetime import datetime

from formatter import format_scripture
from pro_builder import generate_pro_file

# Output directory on the user's Desktop
OUTPUT_DIR = os.path.join(os.path.expanduser('~'), 'Desktop', 'ScriptureBuilder')
os.makedirs(OUTPUT_DIR, exist_ok=True)


class ScriptureSlide:
    """
    Represents a single raw scripture entry from the UI.

    Fields:
        ref         — verse reference, e.g. 'John 3:16' or 'John 3:16 (NIV)'
        text        — raw verse text (may include leading verse numbers)
        translation — translation label, e.g. 'NIV' (optional, may already
                      be embedded in ref)
        screens     — list of screen targets (kept for UI display; the .pro
                      template handles actual screen routing)
    """

    def __init__(self, ref: str, text: str, screens: list[str],
                 translation: str | None = None):
        self.ref = ref
        self.text = text
        self.screens = screens
        self.translation = translation

    def to_entry(self) -> dict:
        """
        Convert to the dict format expected by formatter.format_scripture.

        If the translation is already embedded in the ref (e.g. 'John 3:16 (NIV)')
        we strip it out so the formatter can re-attach it cleanly.
        """
        ref = self.ref.strip()
        translation = self.translation

        # If ref already contains a translation label, extract it
        embedded = re.search(r'\s*\(([A-Z]{2,5})\)\s*$', ref)
        if embedded:
            translation = embedded.group(1)
            ref = ref[:embedded.start()].strip()

        return {
            'ref': ref,
            'text': self.text,
            'translation': translation,
        }


def build_filename(service_label: str) -> str:
    """Build a safe .pro filename from the service label."""
    if service_label:
        safe = re.sub(r'[^\w\s-]', '', service_label)
        safe = re.sub(r'\s+', '-', safe).strip('-')
        return f'{safe}.pro'
    timestamp = datetime.now().strftime('%Y%m%d-%H%M%S')
    return f'scriptures-{timestamp}.pro'


class ProGenerator:
    """
    Takes a list of ScriptureSlide objects, runs them through the formatter,
    and produces a .pro file via pro_builder.
    """

    def __init__(self, slides: list[ScriptureSlide], output_path: str):
        self.slides = slides
        self.output_path = output_path

    def build_payloads(self) -> list[dict]:
        """
        Run each slide through the formatter to produce a flat list of
        slide payloads (one per .pro slide, accounting for 280-char splits).
        """
        payloads = []
        for slide in self.slides:
            entry = slide.to_entry()
            payloads.extend(format_scripture(entry))
        return payloads

    def save(self) -> tuple[str, int]:
        """
        Format all slides and write the .pro file.

        Returns:
            (output_path, slide_count)
        """
        payloads = self.build_payloads()

        if not payloads:
            raise ValueError('No slide payloads were generated.')

        generate_pro_file(
            slide_payloads=payloads,
            output_path=self.output_path,
        )

        return self.output_path, len(payloads)