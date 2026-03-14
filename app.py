from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/generate', methods=['POST'])
def generate():
    data = request.get_json()
    scriptures = data.get('scriptures', [])

    # Just printing for now — we'll build the .pro generator next
    for s in scriptures:
        print(f"  {s['ref']} → screens: {s['screens']}")
        print(f"  Text: {s['text'][:60]}...")

    return jsonify({ 'message': f'{len(scriptures)} scripture(s) received. Generator coming next!' })

if __name__ == '__main__':
    app.run(debug=True)