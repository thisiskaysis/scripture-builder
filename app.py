from flask import Flask, render_template, request, jsonify
import os
from generator import ProGenerator, ScriptureSlide

app = Flask(__name__)

OUTPUT_DIR = os.path.join(os.path.expanduser('~'), 'Desktop', 'ScriptureBuilder')
os.makedirs(OUTPUT_DIR, exist_ok=True)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/generate', methods=['POST'])
def generate():
    data = request.get_json()
    raw_slides = data.get('scriptures', [])

    if not raw_slides:
        return jsonify({ 'success': False, 'message': 'No scriptures provided.' })

    # Build slide objects
    slides = [
        ScriptureSlide(
            ref=s['ref'],
            text=s['text'],
            screens=s['screens']
        )
        for s in raw_slides
    ]

    # Generate the file
    output_path = os.path.join(OUTPUT_DIR, 'scriptures.pro')
    generator = ProGenerator(slides, output_path)
    saved_path = generator.save()

    return jsonify({
        'success': True,
        'message': f'{len(slides)} slide(s) generated. Preview saved to your Desktop in the ScriptureBuilder folder.'
    })

if __name__ == '__main__':
    app.run(debug=True)