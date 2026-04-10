import json
import base64
from io import BytesIO
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4

def handler(event, context):
    # 1. RECIBIR LOS DATOS
    # Intentamos leer el JSON que envía el puente PHP por método POST
    try:
        if event.get("httpMethod") == "POST":
            # Aquí es donde \u00d1 se convierte en Ñ automáticamente
            partidos = json.loads(event.get("body", "[]"))
        else:
            # Datos de prueba por si accedes directo desde el navegador
            partidos = [{"local": "EQUIPO PRUEBA A", "visitante": "EQUIPO PRUEBA B", "hora": "00:00"}]
    except Exception as e:
        partidos = []

    # 2. CONFIGURAR EL DOCUMENTO
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4 # Dimensiones de la hoja A4

    # 3. GENERAR LAS HOJAS (Una por cada partido)
    for p in partidos:
        # --- ENCABEZADO PRINCIPAL ---
        c.setFont("Helvetica-Bold", 14)
        c.drawCentredString(width/2, height - 50, "CAMPEONATO SUB 40 BARRIO CALLUMA")
        
        c.setFont("Helvetica-Bold", 11)
        c.drawCentredString(width/2, height - 68, "HOJA DE CONTROL DE PARTIDO")
        
        # --- INFORMACIÓN DEL ENCUENTRO ---
        c.setFont("Helvetica", 10)
        # Nombres de los equipos (Aquí brilla la Ñ)
        equipo_a = p.get('local', '________________').upper()
        equipo_b = p.get('visitante', '________________').upper()
        hora_p = p.get('hora', '__:__')

        c.drawString(50, height - 110, f"EQUIPO A: {equipo_a}")
        c.drawString(320, height - 110, f"EQUIPO B: {equipo_b}")
        c.drawString(50, height - 130, f"HORA: {hora_p}")
        c.drawString(320, height - 130, "FECHA: ____ / ____ / 2026")

        # --- FUNCIÓN INTERNA PARA DIBUJAR LAS TABLAS ---
        def dibujar_tabla(x, y, titulo):
            c.setFont("Helvetica-Bold", 9)
            c.drawString(x + 2, y + 5, titulo)
            
            # Recuadro exterior de la tabla (Ancho: 240, Alto: 350 para 20 jugadores)
            c.rect(x, y - 350, 240, 350) 
            
            # Encabezados de columna
            c.line(x, y - 18, x + 240, y - 18)
            c.setFont("Helvetica-Bold", 8)
            c.drawString(x + 5, y - 13, "N#")
            c.drawString(x + 30, y - 13, "NOMBRE Y APELLIDO")
            c.drawString(x + 160, y - 13, "T.A")
            c.drawString(x + 185, y - 13, "T.R")
            c.drawString(x + 210, y - 13, "GOL")

            # Dibujar 20 filas para los jugadores
            for i in range(1, 21):
                pos_y = (y - 18) - (i * 16.6)
                c.line(x, pos_y, x + 240, pos_y)
            
            # Líneas verticales divisorias
            c.line(x + 25, y - 18, x + 25, y - 350)  # Tras N#
            c.line(x + 155, y - 18, x + 155, y - 350) # Tras Nombre
            c.line(x + 180, y - 18, x + 180, y - 350) # Tras T.A
            c.line(x + 205, y - 18, x + 205, y - 350) # Tras T.R

        # Dibujamos ambas tablas
        dibujar_tabla(45, height - 160, f"JUGADORES: {equipo_a}")
        dibujar_tabla(310, height - 160, f"JUGADORES: {equipo_b}")

        # --- ÁREA DE FIRMAS (Al final de la página) ---
        c.setFont("Helvetica-Bold", 9)
        c.line(70, 80, 220, 80)
        c.drawCentredString(145, 68, "FIRMA CAPITÁN A")

        c.line(350, 80, 500, 80)
        c.drawCentredString(425, 68, "FIRMA CAPITÁN B")

        c.line(width/2 - 60, 40, width/2 + 60, 40)
        c.drawCentredString(width/2, 28, "FIRMA ÁRBITRO")

        # IMPORTANTE: Finaliza la página actual y prepara la siguiente para el otro partido
        c.showPage()

    # 4. FINALIZAR Y ENVIAR EL ARCHIVO
    c.save()
    pdf_output = buffer.getvalue()
    buffer.close()

    return {
        "statusCode": 200,
        "headers": {
            "Content-Type": "application/pdf",
            "Content-Disposition": "attachment; filename=hojas_control_torneo.pdf",
            "Access-Control-Allow-Origin": "*" # Permite que tu PHP lo reciba
        },
        "body": base64.b64encode(pdf_output).decode("utf-8"),
        "isBase64Encoded": True
    }