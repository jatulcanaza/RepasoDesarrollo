import os
from dotenv import load_dotenv
from loguru import logger
from groq import Groq
import streamlit as st


# Cargar variables de entorno desde un archivo .env
load_dotenv()

# Registrar la clave API de Groq en el log (solo para depuración, evitar en producción)
logger.info(os.getenv('GROQ_API_KEY'))

# Crear una instancia del cliente de Groq para manejar solicitudes de IA
qclient = Groq()

# Crear la interfaz en Streamlit
st.title('Conversión a Binario y Contador de Vocales')

# Verificar si la sesión de Streamlit tiene un historial de mensajes, si no, inicializarlo
if 'messages' not in st.session_state:
    st.session_state.messages = []

# Mostrar el historial de mensajes con el título "Historial"
st.subheader("Historial")
for message in st.session_state.messages:
    if message['role'] == 'user':
        with st.chat_message('user'):
            st.markdown(message['content'])
    else:
        with st.chat_message('assistant'):
            st.markdown(message['content'])

# Función para procesar la respuesta de Groq
def process_data(chat_completion) -> str:
    response = ""
    for chunk in chat_completion:
        if chunk.choices[0].delta.content:
            response += chunk.choices[0].delta.content
    return response

# Sección para ingresar datos
st.subheader("Ingresa un número y un texto")
user_input = st.text_input("Ejemplo: '5, hola mundo'")

if user_input:
    try:
        # Separar el número del texto
        num, text = user_input.split(",", 1)  # Dividir en número y texto
        num = num.strip()  # Limpiar espacios
        text = text.strip()

        # Validar que el número es realmente un número
        if not num.isdigit():
            st.error("El primer valor debe ser un número.")
        else:
            with st.chat_message('user'):
                st.markdown(user_input)

            st.session_state.messages.append({'role': 'user', 'content': user_input})

            with st.chat_message('assistant'):
                try:
                    # Solicitud a la API de Groq para conversión y conteo
                    stream_response = qclient.chat.completions.create(
                        messages=[ 
                            {"role": "system", "content": "Convierte el número dado a binario y cuenta las vocales del texto. Devuelve solo la respuesta en el formato '<binario>, existen <número> vocales, sin detalles adicionales. Ejemplo: '1001, existen 10 vocales'."},
                            {"role": "user", "content": f"Número: {num}, Texto: {text}"},
                        ],
                        model="llama-3.1-8b-instant",
                        stream=True
                    )
                    final_response = process_data(stream_response)  # Obtener respuesta

                    if not final_response:
                        st.error("No puedo generar una respuesta, porque solo tengo el entrenamiento en binario y contar vocales.")
                    else:
                        st.markdown(final_response)

                except Exception as e:
                    st.error("No puedo generar una respuesta, porque solo tengo el entrenamiento en binario y contar vocales.")

            st.session_state.messages.append({'role': 'assistant', 'content': final_response})

    except ValueError:
        st.error("Formato incorrecto. Usa: 'Número, Texto' (Ejemplo: '5, hola mundo')")
