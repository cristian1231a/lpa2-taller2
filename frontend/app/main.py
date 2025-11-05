from flask import Flask, render_template, request, send_file, abort
import requests
from reportlab.lib.pagesizes import A4, letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import mm
from io import BytesIO
import os

app = Flask(__name__)
# Usar esta línea para LOCAL
# BACKEND_URL = os.getenv('BACKEND_URL', 'http://localhost:8000')

# Usar esta línea en Docker
BACKEND_URL = os.getenv('BACKEND_URL', 'http://backend:8000') 
                                                                                                                                                                                                                             

@app.route('/')                                                     
def index():                                                                
    return render_template('index.html')

@app.route('/generar-pdf', methods=['POST'])
def generar_pdf():
    try:                                                                                                        
        print(request.form)
        id_factura = request.form['id_factura']
        response = requests.get(f'{BACKEND_URL}/facturas/v1/{id_factura}')
        
        if response.status_code != 200:
            abort(404, description="Factura no encontrada")
            
        factura = response.json()
       
        # TODO: Crear buffer y doc para la creación del PDF

        buffer = BytesIO()
        
       # 🧾 Crear documento PDF en el buffer
        doc = SimpleDocTemplate(buffer, pagesize=letter)
        elements = []

        # TODO: Adicionar el Título, ID
        styles = getSampleStyleSheet()

        # Cabecera: título, número y fecha
        titulo_style = styles['Title']
        normal = styles['Normal']
        heading = styles.get('Heading2', normal)

        numero = factura.get('numero_factura', id_factura)
        fecha = factura.get('fecha_emision', '')
        empresa = factura.get('empresa', {})
        cliente = factura.get('cliente', {})

        elements.append(Paragraph("Factura", titulo_style))
        elements.append(Spacer(1, 6))
        elements.append(Paragraph(f"Factura: {numero}", normal))
        elements.append(Paragraph(f"Fecha de emision: {fecha}", normal))
        elements.append(Spacer(1, 12))

        # Datos de la empresa
        empresa_lines = []
        if empresa.get('nombre'):
            empresa_lines.append(empresa.get('nombre'))
        if empresa.get('direccion'):
            empresa_lines.append(empresa.get('direccion').replace('\n', '<br/>'))
        if empresa.get('telefono'):
            empresa_lines.append(f"Tel: {empresa.get('telefono')}")
        if empresa.get('email'):
            empresa_lines.append(f"Email: {empresa.get('email')}")
        if empresa_lines:
            elements.append(Paragraph("Empresa:", heading))
            elements.append(Paragraph("<br/>".join(empresa_lines), normal))
            elements.append(Spacer(1, 8))

        # Datos del cliente
        cliente_lines = []
        if cliente.get('nombre'):
            cliente_lines.append(cliente.get('nombre'))
        if cliente.get('direccion'):
            cliente_lines.append(cliente.get('direccion').replace('\n', '<br/>'))
        if cliente.get('telefono'):
            cliente_lines.append(f"Tel: {cliente.get('telefono')}")
        if cliente_lines:
            elements.append(Paragraph("Cliente:", heading))
            elements.append(Paragraph("<br/>".join(cliente_lines), normal))
            elements.append(Spacer(1, 12))

        # Detalle / items (usa 'detalle' en la estructura suministrada)
        items = factura.get('detalle', []) or []
        if items:
            data = [["Cantidad", "Descripción", "Precio unitario", "Total"]]
            for it in items:
                qty = it.get('cantidad', '')
                desc = it.get('descripcion', '')
                unit = it.get('precio_unitario', '')
                total_it = it.get('total', '')

                def fmt(v):
                    return f"{v:,.2f}" if isinstance(v, (int, float)) else str(v)

                data.append([
                    str(qty),
                    desc,
                    fmt(unit),
                    fmt(total_it)
                ])

            table = Table(data, colWidths=[50, 280, 90, 90])
            table.setStyle(TableStyle([
                ('BACKGROUND', (0,0), (-1,0), colors.grey),
                ('TEXTCOLOR',(0,0),(-1,0),colors.whitesmoke),
                ('GRID', (0,0), (-1,-1), 0.5, colors.black),
                ('ALIGN', (2,1), (-1,-1), 'RIGHT'),
                ('VALIGN', (0,0), (-1,-1), 'TOP'),
                ('LEFTPADDING', (1,1), (1,-1), 6)
            ]))
            elements.append(table)
            elements.append(Spacer(1, 12))

        # Totales
        def fmt_total(v):
            return f"{v:,.2f}" if isinstance(v, (int, float)) else str(v)

        subtotal = factura.get('subtotal')
        impuesto = factura.get('impuesto')
        total = factura.get('total')

        if subtotal is not None:
            elements.append(Paragraph(f"Subtotal: {fmt_total(subtotal)}", normal))
        if impuesto is not None:
            elements.append(Paragraph(f"Impuesto: {fmt_total(impuesto)}", normal))
        if total is not None:
            elements.append(Spacer(1, 6))
            elements.append(Paragraph(f"Total: {fmt_total(total)}", styles['Heading2']))
        # Generar el doc y limpiar el buffer
        doc.build(elements)
        buffer.seek(0)
        
        # Retornar a la página el PDF para visualizar y descargar
        return send_file(
            buffer,
            mimetype='application/pdf',
            as_attachment=True,
            download_name=f"factura_{id_factura}.pdf"
        )

        
    except requests.exceptions.ConnectionError:
        abort(503, description="Error de conexión con el servidor")
    except Exception as e:
        abort(500, description=str(e))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3000, debug=True)

