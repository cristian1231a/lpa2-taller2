from flask import Flask, render_template, request, send_file, abort
import requests
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import mm
from io import BytesIO
import os

app = Flask(__name__)
BACKEND_URL = os.getenv('BACKEND_URL', 'http://backend:8000')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/generar-pdf', methods=['POST'])
def generar_pdf():
    try:
        id_factura = request.form['id_factura']
        response = requests.get(f'{BACKEND_URL}/facturas/v1/{id_factura}')
        
        if response.status_code != 200:
            abort(404, description="Factura no encontrada")
            
        factura = response.json()
        
        # TODO: Crear buffer y doc para la creación del PDF
        

        # TODO: Adicionar el Título, ID

        
        # TODO: Agregar Información de la Empresa


        # TODO: Agregar Información del Cliente


        # TODO: Adicionar el Detalle de la Factura: cantidad, descripción, precio unitario y total


        # TODO: Adicionar Subtotal, impuesto y Total


        # Generar el doc y limpiar el buffer
        doc.build(elements)
        buffer.seek(0)
        
        # TODO: Retornar a la página el PDF para visualizar y descargar

        
    except requests.exceptions.ConnectionError:
        abort(503, description="Error de conexión con el servidor")
    except Exception as e:
        abort(500, description=str(e))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3000, debug=True)

