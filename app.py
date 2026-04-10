"""
app.py
------
Flask routes for the Scripture Builder web UI.

Routes:
    GET  /          — serve the UI
    POST /upload    — parse a .docx sermon doc, return formatted scripture entries
    POST /generate  — take the scripture list from the UI, generate a .pro file
"""

import os
import re

from flask import Flask, render_template, request, jsonify
from werkzeug.utils import secure_filename

from sermon_parser import parse_sermon_doc
from formatter import format_scripture
from generator import ProGenerator, ScriptureSlide, OUTPUT_DIR, build_filename

app = Flask(__name__)

UPLOAD_FOLDER = os.path.join(OUTPUT_DIR, 'uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/upload', methods=['POST'])
def upload():
    """
    Accept a .docx file, parse it for scripture references, run each entry
    through the formatter, and return slide-ready payloads to the UI.
    """
    if 'file' not in request.files:
        return jsonify({'success': False, 'message': 'No file uploaded.'})

    file = request.files['file']

    if not (file.filename.endswith('.docx') or file.filename.endswith('.pdf')):
        return jsonify({'success': False, 'message': 'Please upload a .docx or .pdf file.'})

    filename = secure_filename(file.filename)
    filepath = os.path.join(UPLOAD_FOLDER, filename)
    file.save(filepath)

    try:
        raw_entries = parse_sermon_doc(filepath)

        if not raw_entries:
            return jsonify({
                'success': False,
                'message': 'No scriptures found in the document. '
                           'Check the formatting and try again.'
            })

        # Run each raw entry through the formatter to get slide-ready payloads.
        # Each entry may produce multiple payloads (due to 280-char splits).
        # We return the first payload per entry for display in the UI list,
        # but store all payloads so /generate can use them properly.
        ui_entries = []
        for entry in raw_entries:
            payloads = format_scripture(entry)
            # Use the first payload's ref/text for the UI display item.
            # The screens field is preserved from the parser's default.
            ui_entries.append({
                'ref': payloads[0]['ref'],
                'text': entry['text'],          # raw text — formatter runs again on /generate
                'translation': entry.get('translation'),
                'screens': entry.get('screens', ['left_pillar', 'right_pillar']),
            })

        return jsonify({'success': True, 'scriptures': ui_entries})

    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error reading document: {str(e)}'
        })


@app.route('/generate', methods=['POST'])
def generate():
    """
    Accept the UI scripture list, run the full pipeline, write a .pro file.
    """
    data = request.get_json()
    raw_slides = data.get('scriptures', [])
    service_label = data.get('serviceLabel', '').strip()

    if not raw_slides:
        return jsonify({'success': False, 'message': 'No scriptures provided.'})

    slides = [
        ScriptureSlide(
            ref=s['ref'],
            text=s['text'],
            screens=s.get('screens', ['left_pillar', 'right_pillar']),
            translation=s.get('translation'),
        )
        for s in raw_slides
    ]

    filename = build_filename(service_label)
    output_path = os.path.join(OUTPUT_DIR, filename)

    try:
        generator = ProGenerator(slides, output_path)
        saved_path, slide_count = generator.save()

        return jsonify({
            'success': True,
            'message': (
                f'{slide_count} slide(s) generated — '
                f'saved as "{filename}" in your ScriptureBuilder folder on the Desktop.'
            )
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error generating .pro file: {str(e)}'
        })


if __name__ == '__main__':
    app.run(debug=True)