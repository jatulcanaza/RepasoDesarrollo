document.addEventListener('DOMContentLoaded', () => {
    // Obtiene los elementos del DOM
    const fileInput = document.getElementById('file-input'); // Campo de entrada de archivos
    const summarizeButton = document.getElementById('summarize-button'); // Botón para resumir
    const loading = document.getElementById('loading'); // Elemento indicador de carga
    const resultDiv = document.getElementById('result'); // Contenedor del resultado
    const resultText = document.getElementById('result-text'); // Texto del resultado
    const fileLabel = document.getElementById('file-label'); // Etiqueta del archivo seleccionado

    // Evento que se activa cuando el usuario selecciona un archivo
    fileInput.addEventListener('change', (event) => {
        const file = event.target.files[0]; // Obtiene el primer archivo seleccionado
        if (file) {
            summarizeButton.classList.remove('hidden'); // Muestra el botón de resumir
            fileLabel.textContent = "📂 " + file.name; // Muestra el nombre del archivo en la etiqueta
        }
    });

    // Evento que se activa al hacer clic en el botón de resumir
    summarizeButton.addEventListener('click', () => {
        if (fileInput.files.length === 0) { // Verifica si no hay archivo seleccionado
            alert('Por favor, selecciona un archivo.'); // Muestra una alerta
            return;
        }

        const file = fileInput.files[0]; // Obtiene el archivo seleccionado
        const formData = new FormData(); // Crea un objeto FormData para enviar el archivo
        formData.append('file', file); // Agrega el archivo al FormData

        loading.classList.remove('hidden'); // Muestra el indicador de carga
        resultDiv.classList.add('hidden'); // Oculta la sección de resultado

        // Realiza una solicitud fetch al backend para resumir el archivo
        fetch('http://127.0.0.1:5000/summarize-file', {
            method: 'POST', // Método HTTP
            body: formData, // Envío del archivo como FormData
        })
        .then(response => response.json()) // Convierte la respuesta en JSON
        .then(data => {
            loading.classList.add('hidden'); // Oculta el indicador de carga

            if (data.summary) { // Si el servidor devuelve un resumen
                resultText.textContent = data.summary; // Muestra el resumen
                resultDiv.classList.remove('hidden'); // Muestra la sección de resultado
            } else {
                resultText.textContent = `❌ Error: ${data.error || 'No se pudo generar el resumen.'}`;
                resultDiv.classList.remove('hidden'); // Muestra el error en la sección de resultado
            }
        })
        .catch(error => {
            console.error('Error:', error); // Muestra el error en la consola
            loading.classList.add('hidden'); // Oculta el indicador de carga
            resultText.textContent = '❌ Error: No se pudo conectar al servidor.'; // Muestra un mensaje de error
            resultDiv.classList.remove('hidden'); // Muestra la sección de resultado con el error
        });
    });
});
