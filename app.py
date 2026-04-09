from flask import Flask, render_template, request, jsonify
import os
import re
from werkzeug.utils import secure_filename
from sermon_parser import parse_sermon_doc
from generator import ProGenerator, ScriptureSlide

app = Flask(__name__)

OUTPUT_DIR = os.path.join(os.path.expanduser('~'), 'Desktop', 'ScriptureBuilder')
os.makedirs(OUTPUT_DIR, exist_ok=True)

UPLOAD_FOLDER = os.path.join(OUTPUT_DIR, 'uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/generate', methods=['POST'])
def generate():
    data = request.get_json()
    raw_slides = data.get('scriptures', [])
    service_label = data.get('serviceLabel', '').strip()

    if not raw_slides:
        return jsonify({ 'success': False, 'message': 'No scriptures provided.' })

    slides = [
        ScriptureSlide(
            ref=s['ref'],
            text=s['text'],
            screens=s['screens']
        )
        for s in raw_slides
    ]

    # Build a clean filename from the service label if provided
    if service_label:
        safe_label = re.sub(r'[^\w\s-]', '', service_label)
        safe_label = re.sub(r'\s+', '-', safe_label).strip('-')
        filename = f'{safe_label}.pro'
    else:
        filename = 'scriptures.pro'

    output_path = os.path.join(OUTPUT_DIR, filename)
    generator = ProGenerator(slides, output_path)
    saved_path = generator.save()

    return jsonify({
        'success': True,
        'message': f'{len(slides)} slide(s) generated — saved as "{filename}" in your ScriptureBuilder folder on the Desktop.'
    })

@app.route('/upload', methods=['POST'])
def upload():
    if 'file' not in request.files:
        return jsonify({ 'success': False, 'message': 'No file uploaded.' })

    file = request.files['file']

    if not file.filename.endswith('.docx'):
        return jsonify({ 'success': False, 'message': 'Please upload a .docx file.' })

    filename = secure_filename(file.filename)
    filepath = os.path.join(UPLOAD_FOLDER, filename)
    file.save(filepath)

    try:
        scriptures = parse_sermon_doc(filepath)
        if not scriptures:
            return jsonify({ 'success': False, 'message': 'No scriptures found in the document. Check the formatting and try again.' })

        return jsonify({ 'success': True, 'scriptures': scriptures })

    except Exception as e:
        return jsonify({ 'success': False, 'message': f'Error reading document: {str(e)}' })

if __name__ == '__main__':
    app.run(debug=True)