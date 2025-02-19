from fastapi import FastAPI
from pydantic import BaseModel
from groq import Groq
from dotenv import load_dotenv
from fastapi.middleware.cors import CORSMiddleware
import os

# Cargar variables de entorno
load_dotenv()

# Inicializar FastAPI
app = FastAPI()

# Configuración de CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Permitir todas las solicitudes desde cualquier origen
    allow_credentials=True,
    allow_methods=["*"],  # Permitir cualquier método HTTP
    allow_headers=["*"],  # Permitir cualquier cabecera
)

# Instanciar cliente de Groq
qclient = Groq()

# Modelo de datos para la entrada
class UserInput(BaseModel):
    number: int
    text: str

# Ruta de ejemplo para procesar la entrada del usuario
@app.post("/process/")
async def process_input(user_input: UserInput):
    try:
        # Solicitar datos a Groq para la conversión y conteo
        stream_response = qclient.chat.completions.create(
            messages=[ 
                {"role": "system", "content": "Convierte el número dado a binario y cuenta las vocales del texto. Devuelve solo la respuesta en el formato '<binario>, existen <número> vocales, sin detalles adicionales. Ejemplo: '1001, existen 10 vocales'."},
                {"role": "user", "content": f"Número: {user_input.number}, Texto: {user_input.text}"},
            ],
            model="llama-3.1-8b-instant",
            stream=True
        )

        # Procesar la respuesta de Groq
        response = ""
        for chunk in stream_response:
            if chunk.choices[0].delta.content:
                response += chunk.choices[0].delta.content

        if not response:
            return {"error": "No puedo generar una respuesta, porque solo tengo el entrenamiento en binario y contar vocales."}
        
        return {"response": response}

    except Exception as e:
        return {"error": "No se pudo procesar la solicitud. Error en la API de Groq."}
