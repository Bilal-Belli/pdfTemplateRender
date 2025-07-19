from flask import Flask, json, request, send_file, jsonify, render_template
import csv
import io
import os
import zipfile
import tempfile
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from PyPDF2 import PdfReader, PdfWriter

app = Flask(__name__)
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')  # See below for template

@app.route('/upload', methods=['POST'])
def upload():
    file = request.files['pdf']
    path = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(path)
    return jsonify({'filename': file.filename})

@app.route("/generate-pdfs", methods=["POST"])
def generate_pdfs():
    tags = request.form.get("tags")
    csv_rows = request.form.get("csv")
    pdf_file = request.files.get("pdf_template")
    if not tags or not csv_rows or not pdf_file:
        return jsonify({"error": "Missing data"}), 400
    tags = json.loads(tags)
    # Save uploaded PDF template to a temp file
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        pdf_file.save(tmp.name)
        template_path = tmp.name
    # Parse CSV
    csv_reader = csv.DictReader(io.StringIO(csv_rows))
    # Create ZIP
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, "w") as zipf:
        for i, row in enumerate(csv_reader):
            pdf_bytes = io.BytesIO()
            packet = io.BytesIO()
            can = canvas.Canvas(packet, pagesize=letter)
            coordinates = {}
            for tag in tags:
                name = tag["tag"]
                xy = (tag["x"], tag["y"])
                coordinates.setdefault(name, []).append(xy)
            for tag_name, value in row.items():
                if tag_name in coordinates:
                    for x, y in coordinates[tag_name]:
                        can.drawString(x, y, f"{value}")
            can.save()
            packet.seek(0)
            new_pdf = PdfReader(packet)
            existing_pdf = PdfReader(template_path)
            output = PdfWriter()
            page = existing_pdf.pages[0]
            page.merge_page(new_pdf.pages[0])
            output.add_page(page)
            output.write(pdf_bytes)
            pdf_bytes.seek(0)
            zipf.writestr(f"filled_{i}.pdf", pdf_bytes.read())

    zip_buffer.seek(0)
    return send_file(
        zip_buffer,
        mimetype="application/zip",
        as_attachment=True,
        download_name="filled_pdfs.zip"
    )

if __name__ == '__main__':
    app.run(debug=True)