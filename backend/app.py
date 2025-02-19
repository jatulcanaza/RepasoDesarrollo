import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
from groq import Groq
import PyPDF2
import pandas as pd
import xml.etree.ElementTree as ET
import csv

# Cargar variables de entorno
load_dotenv()

# Inicializar Flask
app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})  # Permitir todas las solicitudes

# Inicializar cliente de Groq
api_key = os.getenv('GROQ_API_KEY')
if not api_key:
    raise ValueError("Falta la API Key de Groq en el archivo .env")
qclient = Groq(api_key=api_key)

# Funciones para extraer texto de archivos
def extract_text_from_pdf(pdf_file):
    pdf_reader = PyPDF2.PdfReader(pdf_file)
    text = "".join([page.extract_text() for page in pdf_reader.pages if page.extract_text()])
    return text

def extract_text_from_excel(excel_file):
    df = pd.read_excel(excel_file)
    return df.to_string()

def extract_text_from_xml(xml_file):
    tree = ET.parse(xml_file)
    root = tree.getroot()
    return " ".join([element.text.strip() for element in root.iter() if element.text and element.text.strip()])

def extract_text_from_csv(csv_file):
    df = pd.read_csv(csv_file)
    return df.to_string()

# Función para dividir texto en fragmentos
def split_text_into_chunks(text, chunk_size=3000, overlap=200):
    chunks = []
    start = 0

    while start < len(text):
        end = start + chunk_size
        if end < len(text):
            while end > start and text[end] != ' ':  # Evitar cortes bruscos de palabras
                end -= 1
        chunks.append(text[start:end])
        start = end - overlap  # Solapamiento para mantener contexto

    return chunks

# Ruta para manejar la subida de archivos y generar un resumen
@app.route('/summarize-file', methods=['POST'])
def summarize_file():
    try:
        if 'file' not in request.files:
            return jsonify({"error": "No se proporcionó ningún archivo"}), 400

        file = request.files['file']
        file_extension = file.filename.split('.')[-1].lower()

        print(f"📂 Archivo recibido: {file.filename}")

        if file_extension == 'pdf':
            text = extract_text_from_pdf(file)
        elif file_extension == 'xlsx':
            text = extract_text_from_excel(file)
        elif file_extension == 'xml':
            text = extract_text_from_xml(file)
        elif file_extension == 'csv':
            text = extract_text_from_csv(file)
        else:
            return jsonify({"error": "Formato de archivo no soportado"}), 400

        if not text.strip():
            return jsonify({"error": "No se pudo extraer texto del archivo"}), 400

        # Dividir el texto en chunks
        chunks = split_text_into_chunks(text, chunk_size=3000, overlap=200)

        summaries = []
        for chunk in chunks:
            response = qclient.chat.completions.create(
                messages=[
                    {"role": "system", "content": "Eres un asistente que resume documentos en español."},
                    {"role": "user", "content": chunk},
                ],
                model="mixtral-8x7b-32768"
            )
            summaries.append(response.choices[0].message.content)

        # Unir los resúmenes en un resumen final
        final_summary = " ".join(summaries)

        # Si el resumen sigue siendo largo, hacer un segundo resumen
        if len(final_summary) > 3000:
            response = qclient.chat.completions.create(
                messages=[
                    {"role": "system", "content": "Eres un asistente que genera resúmenes concisos."},
                    {"role": "user", "content": final_summary[:3000]},
                ],
                model="mixtral-8x7b-32768"
            )
            final_summary = response.choices[0].message.content

        return jsonify({"summary": final_summary})

    except Exception as e:
        print(f"❌ Error en el servidor: {e}")
        return jsonify({"error": str(e)}), 500

# Iniciar el servidor Flask
if __name__ == '__main__':
    app.run(debug=True, port=5000)
