# Importar las bibliotecas necesarias
import os  # Proporciona funciones para interactuar con el sistema operativo, como acceder a variables de entorno
from flask import Flask, request, jsonify  # Flask es un micro-framework para aplicaciones web, request se usa para acceder a las solicitudes HTTP, jsonify convierte respuestas en formato JSON
from flask_cors import CORS  # CORS se utiliza para permitir solicitudes de diferentes dominios
from dotenv import load_dotenv  # Carga las variables de entorno desde un archivo .env
from groq import Groq  # Biblioteca para interactuar con la API de Groq
import pandas as pd  # Biblioteca para manipular datos estructurados (como archivos Excel y CSV)

# Cargar variables de entorno desde el archivo .env
load_dotenv()

# Inicializar la aplicación Flask
app = Flask(__name__)  # Crea una instancia de la aplicación Flask
CORS(app, resources={r"/*": {"origins": "*"}})  # Permite solicitudes CORS de todos los orígenes para toda la aplicación

# Inicializar el cliente de Groq utilizando la API Key cargada desde las variables de entorno
api_key = os.getenv('GROQ_API_KEY')  # Obtiene la clave de API de Groq desde el archivo .env
if not api_key:  # Si no se encuentra la clave de API, lanza un error
    raise ValueError("Falta la API Key de Groq en el archivo .env")
qclient = Groq(api_key=api_key)  # Crea un cliente de Groq utilizando la clave de API


# Función para extraer texto de archivos Excel (XLSX)
def extract_text_from_excel(excel_file):
    df = pd.read_excel(excel_file)  # Lee el archivo Excel y lo convierte en un DataFrame de pandas
    return df.to_string()  # Convierte el DataFrame en una cadena de texto


# Ruta para manejar la subida de archivos y generar un resumen
@app.route('/summarize-file', methods=['POST'])  # Define una ruta de la API para manejar solicitudes POST a '/summarize-file'
def summarize_file():
    try:
        # Verifica si el archivo está presente en la solicitud
        if 'file' not in request.files:
            return jsonify({"error": "No se proporcionó ningún archivo"}), 400  # Si no se proporciona archivo, devuelve un error 400

        file = request.files['file']  # Obtiene el archivo de la solicitud
        file_extension = file.filename.split('.')[-1].lower()  # Obtiene la extensión del archivo

        print(f"📂 Archivo recibido: {file.filename}")  # Imprime el nombre del archivo para depuración

        # Dependiendo de la extensión del archivo, llama a la función correspondiente para extraer el texto
        if file_extension == 'xlsx':
            text = extract_text_from_excel(file)
        else:
            return jsonify({"error": "Formato de archivo no soportado"}), 400  # Si el formato no es soportado, devuelve un error

        # Si no se extrajo texto, devuelve un error
        if not text.strip():
            return jsonify({"error": "No se pudo extraer texto del archivo"}), 400

        # Crea una solicitud de resumen a Groq, enviando el texto extraído
        response = qclient.chat.completions.create(
            messages=[
                {"role": "system", "content": "En base al texto etiquetar: Votos de Noboa, Votos Luisa, Votos Nulo. Una vez contado quiero que cuentes cuantos votos tiene el nulo y me des una conclusión"},  # Instrucciones al asistente
                {"role": "user", "content": text[:3000]},  # El texto extraído (limitado a 3000 caracteres)
            ],
            model="mixtral-8x7b-32768"  # El modelo a utilizar para el resumen
        )

        # Obtiene el resumen generado por Groq
        summary = response.choices[0].message.content

        # Devuelve el resumen como respuesta JSON
        return jsonify({"summary": summary})

    except Exception as e:  # Si ocurre un error, maneja la excepción
        print(f"❌ Error en el servidor: {e}")  # Imprime el error para depuración
        return jsonify({"error": str(e)}), 500  # Devuelve un error 500 con el mensaje de excepción

# Inicia el servidor Flask en el puerto 5000 en modo de depuración
if __name__ == '__main__':
    app.run(debug=True, port=5000)
