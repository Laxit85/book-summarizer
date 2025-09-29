import os
from flask import Flask, request, render_template, redirect, url_for, send_file, jsonify, session
from werkzeug.utils import secure_filename
from book_summarizer import main as summarize_file
import io
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import json
import threading
import uuid

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'pdf', 'txt'}

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.secret_key = 'your_secret_key_here'  # Change this to a random secret key

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

results_store = {}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def process_file(filepath, task_id):
    results = summarize_file(filepath, return_results=True)
    results_store[task_id] = results

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        if 'file' not in request.files:
            return render_template('index.html', error='No file part')
        file = request.files['file']
        if file.filename == '':
            return render_template('index.html', error='No selected file')
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            task_id = str(uuid.uuid4())
            session['task_id'] = task_id
            # Start background processing
            thread = threading.Thread(target=process_file, args=(filepath, task_id))
            thread.start()
            return redirect(url_for('processing'))
        else:
            return render_template('index.html', error='Unsupported file type')
    return render_template('index.html')

@app.route('/processing')
def processing():
    task_id = session.get('task_id')
    if not task_id or task_id not in results_store:
        return render_template('processing.html')
    results = results_store.pop(task_id, None)
    if results:
        return render_template('index.html', results=results)
    return render_template('processing.html')

@app.route('/export/json', methods=['POST'])
def export_json():
    data = request.get_json()
    json_str = json.dumps(data, indent=2)
    return send_file(
        io.BytesIO(json_str.encode()),
        mimetype='application/json',
        as_attachment=True,
        download_name='book_summary.json'
    )

@app.route('/export/pdf', methods=['POST'])
def export_pdf():
    data = request.get_json()
    buffer = io.BytesIO()
    p = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter
    y = height - 40
    p.setFont("Helvetica-Bold", 16)
    p.drawString(40, y, "Book Summary and MCQs")
    y -= 30
    p.setFont("Helvetica", 12)
    for chapter in data:
        if y < 100:
            p.showPage()
            y = height - 40
        p.setFont("Helvetica-Bold", 14)
        p.drawString(40, y, chapter['chapter'])
        y -= 20
        p.setFont("Helvetica", 12)
        summary_lines = chapter['summary'].split('\n')
        for line in summary_lines:
            if y < 60:
                p.showPage()
                y = height - 40
            p.drawString(50, y, line)
            y -= 15
        y -= 10
        p.setFont("Helvetica-Bold", 13)
        p.drawString(50, y, "MCQs:")
        y -= 20
        p.setFont("Helvetica", 12)
        for q in chapter['mcqs']:
            if y < 60:
                p.showPage()
                y = height - 40
            p.drawString(60, y, f"Q: {q['question']}")
            y -= 15
            for opt in q['options']:
                if y < 60:
                    p.showPage()
                    y = height - 40
                p.drawString(70, y, f"- {opt}")
                y -= 15
            y -= 10
        y -= 20
    p.save()
    buffer.seek(0)
    return send_file(
        buffer,
        mimetype='application/pdf',
        as_attachment=True,
        download_name='book_summary.pdf'
    )

if __name__ == '__main__':
    app.run(debug=True)
