import streamlit as st
import pandas as pd
import json
from groq import Groq
from dotenv import load_dotenv
import os

# Cargar variables de entorno
load_dotenv()

# Obtener la clave API de Groq
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# Verificar que la API Key está presente
if not GROQ_API_KEY:
    st.error("❌ ERROR: No se encontró la API Key de Groq. Verifica tu archivo .env.")
    st.stop()

# Inicializar el cliente de Groq
qclient = Groq(api_key=GROQ_API_KEY)

def extraccionData():
    """Carga los datos desde un archivo CSV y los convierte en JSON."""
    try:
        df = pd.read_csv("datos_desordenados.csv")
        jsonData = df.to_json(orient="records", force_ascii=False, indent=4)
        return jsonData
    except FileNotFoundError:
        st.error("❌ ERROR: No se encontró el archivo 'datos_desordenados.csv'.")
        return None
    except pd.errors.EmptyDataError:
        st.error("❌ ERROR: El archivo CSV está vacío.")
        return None
    except Exception as e:
        st.error(f"❌ ERROR: Ocurrió un problema al leer el CSV: {str(e)}")
        return None

# Extraer los datos
data = extraccionData()
if not data:
    st.stop()

# Interfaz de Streamlit
st.title("Clasificación de Código")

# Campo de entrada para el código
codigo = st.number_input("Ingrese el código:", min_value=0)

# Inicializa una variable para la respuesta
respuesta = ""

# Inicializa una lista para el historial de respuestas
if "historial" not in st.session_state:
    st.session_state.historial = []

# Si el usuario hace clic en "Clasificar"
if st.button("Clasificar"):
    try:
        # Cargar los datos desde JSON
        datos = json.loads(data)  # Convertir la cadena JSON en una lista de diccionarios
        valor_asociado = next((item["valor"] for item in datos if item["codigo"] == codigo), None)

        if valor_asociado:
            # Construir el prompt para Groq
            prompt = (
                f"Analiza el siguiente texto: {valor_asociado} y asígnale una etiqueta "
                f"(deportes, política, religión, cine). Si no puedes asignar una etiqueta, "
                f"responde con 'No se pudo generar una etiqueta'. "
                f"Solo muestra la respuesta en este formato: {codigo},etiqueta sin ningún texto adicional."
            )

            # Realizar la solicitud a la API de Groq
            chat_completion = qclient.chat.completions.create(
                messages=[{"role": "user", "content": prompt}],
                model="qwen-2.5-32b",
            )

            # Obtener la respuesta de Groq
            etiqueta = chat_completion.choices[0].message.content.strip()

            # Formatear la respuesta
            respuesta = f"{etiqueta}"
        else:
            respuesta = "No se pudo generar una etiqueta (código no encontrado)."

        # Agregar la respuesta al historial
        st.session_state.historial.append(respuesta)

    except Exception as e:
        respuesta = f"❌ ERROR: Ocurrió un problema con la clasificación: {str(e)}"
        st.session_state.historial.append(respuesta)

# Mostrar la respuesta en un área de texto
st.text_area("Respuesta:", respuesta, height=100)

# Mostrar el historial de respuestas en otro área de texto
st.text_area("Historial de respuestas:", "\n".join(st.session_state.historial), height=200)
