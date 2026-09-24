import streamlit as st
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
import io
import datetime
import pandas as pd
import re

st.set_page_config(page_title="Servicio de Obstetricia - Control del Adolescente (Vertical)", layout="wide")

st.markdown("### 🏥 Servicio de Obstetricia")
st.markdown("**Registro para el Control del Adolescente - Formato HIS MINSA **")

if "lista_pacientes" not in st.session_state:
    st.session_state.lista_pacientes = []

# --- 1. DATOS DEL ESTABLECIMIENTO Y PROFESIONAL ---
st.markdown("#### 1. Datos del Establecimiento y Profesional")
col1, col2, col3 = st.columns(3)
with col1:
    mes = st.selectbox("Mes", ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"], index=8)
with col2:
    centro_salud = st.text_input("Centro de Salud / IPRESS", "C.S. Belén")
with col3:
    turno_op = st.selectbox("Turno", ["Mañana (M)", "Tarde (T)", "Noche (N)"])

col4, col5, col6 = st.columns(3)
with col4:
    anio = st.text_input("Año", "2026")
with col5:
    dni_profesional = st.text_input("DNI del Profesional (Exactamente 8 números)", max_chars=8, value="", placeholder="Ej: 28210469")
with col6:
    nombres_profesional = st.text_input("Nombres del Profesional", value="", placeholder="Apellidos y Nombres")

st.markdown("---")

# --- 2. FORMULARIO DE DATOS DEL PACIENTE ---
st.markdown(f"#### 2. Datos del Paciente, Antropometría y Condición (Paciente N° {len(st.session_state.lista_pacientes) + 1})")

with st.form("form_paciente", clear_on_submit=True):
    col_p1, col_p2, col_p3 = st.columns(3)
    with col_p1:
        fecha_atencion = st.date_input("Fecha de Atención", datetime.date.today())
    with col_p2:
        dni_paciente = st.text_input("DNI del Paciente (Exactamente 8 números)", max_chars=8, placeholder="Ej: 45678912")
    with col_p3:
        nombres_paciente = st.text_input("Nombres y Apellidos del Paciente", placeholder="Apellidos y Nombres")

    col_p4, col_p5, col_p6, col_p7 = st.columns(4)
    with col_p4:
        edad_anos = st.number_input("Edad (Años)", min_value=10, max_value=19, value=14)
    with col_p5:
        sexo_paciente = st.selectbox("Sexo", ["F (Femenino)", "M (Masculino)"])
    with col_p6:
        talla_str = st.text_input("Talla (cm)", value="", placeholder="Ej: 150.0")
    with col_p7:
        peso_str = st.text_input("Peso (kg)", value="", placeholder="Ej: 45.0")

    col_p8, col_p9, col_p10 = st.columns(3)
    with col_p8:
        perimetro_abd_str = st.text_input("Perímetro Abdominal (cm)", value="", placeholder="Ej: 72.0")
    with col_p9:
        hb_str = st.text_input("Hemoglobina - Hb (g/dl)", value="", placeholder="Ej: 13.0")
    with col_p10:
        condicion_paciente = st.selectbox("Condición del Paciente", ["C (Continuador)", "N (Nuevo)", "R (Reingresante)"])

    st.markdown("---")
    st.markdown("#### 3. Diagnósticos y Procedimientos Oficiales")
    st.info("Se incluirán automáticamente las actividades normadas más 2 líneas adicionales con mayor altura.")

    tipo_diagnostico = st.selectbox("Tipo de Diagnóstico / Actividad (HIS)", ["D (Definitivo)", "P (Preventivo)", "R (Repetido)"])

    btn_guardar = st.form_submit_button("➕ Guardar e Ingresar Siguiente", type="primary")

    if btn_guardar:
        dni_pac_limpio = re.sub(r'\D', '', dni_paciente)
        dni_prof_limpio = re.sub(r'\D', '', dni_profesional)

        if not dni_prof_limpio or len(dni_prof_limpio) != 8:
            st.error("⚠️ El DNI del Profesional debe contener exactamente 8 dígitos numéricos.")
        elif not dni_pac_limpio or len(dni_pac_limpio) != 8:
            st.error("⚠️ El DNI del Paciente debe contener exactamente 8 dígitos numéricos.")
        elif not nombres_paciente:
            st.error("⚠️ Por favor, ingrese los Nombres del Paciente.")
        else:
            cond_letra = condicion_paciente[0]
            tipo_letra = tipo_diagnostico[0]
            sexo_letra = sexo_paciente[0]

            val_talla = talla_str.strip() if talla_str.strip() != "" else ""
            val_peso = peso_str.strip() if peso_str.strip() != "" else ""
            val_pa = perimetro_abd_str.strip() if perimetro_abd_str.strip() != "" else ""
            val_hb = hb_str.strip() if hb_str.strip() != "" else ""

            lineas_antropometria = [
                f"Talla: {val_talla}",
                f"Peso: {val_peso}",
                f"P. Abd: {val_pa}",
                f"Hb: {val_hb}"
            ]
            antropometria_text = "<br/>".join(lineas_antropometria)

            codigos = ["Z003", "99384", "96150.01", "96150.02", "96150.03", "96150.05", "99402.09", "99401.15", "99403.01", "", ""]
            descripciones = [
                "EXAMEN DEL ESTADO DE DESARROLLO DEL ADOLESCENTE",
                "ATENCIÓN INICIAL Y EXHAUSTIVA DE MEDICINA PREVENTIVA",
                "TAMIZAJE DE SALUD MENTAL EN VIOLENCIA",
                "TAMIZAJE DE SALUD MENTAL EN ALCOHOL Y DROGAS",
                "TAMIZAJE DE SALUD MENTAL EN TRASTORNOS DEPRESIVOS",
                "TAMIZAJE DE SALUD MENTAL EN HABILIDADES SOCIALES",
                "CONSEJERÍA DE PREVENCIÓN DE RIESGOS EN SALUD MENTAL",
                "CONSEJERÍA EN HABILIDADES SOCIALES",
                "CONSEJERÍA NUTRICIONAL: ALIMENTACIÓN SALUDABLE",
                "<br/>",
                "<br/>"
            ]
            labs = ["", "2", "", "", "", "", "1", "", "2", "", ""]
            prds = [tipo_letra] * 9 + ["", ""]

            nuevo_paciente = {
                "nro": len(st.session_state.lista_pacientes) + 1,
                "dni": dni_pac_limpio,
                "nombres": nombres_paciente,
                "edad": edad_anos,
                "sexo": sexo_letra,
                "fecha_nac": str(fecha_atencion),
                "antropometria": antropometria_text,
                "condicion": cond_letra,
                "codigos": codigos,
                "descripciones": descripciones,
                "labs": labs,
                "prds": prds
            }
            st.session_state.lista_pacientes.append(nuevo_paciente)
            st.success(f"✅ ¡Paciente guardado con éxito! (Total registrados: {len(st.session_state.lista_pacientes)})")

# --- 4. LISTA DE PACIENTES REGISTRADOS Y GENERACIÓN DE PDF ---
if len(st.session_state.lista_pacientes) > 0:
    st.markdown("---")
    st.markdown(f"### 📋 Pacientes Registrados ({len(st.session_state.lista_pacientes)})")
    
    df_preview = pd.DataFrame([{
        "nro": p["nro"], "dni": p["dni"], "nombres": p["nombres"], "edad": p["edad"], "sexo": p["sexo"],
        "antropometria": p["antropometria"].replace("<br/>", " | "), "condicion": p["condicion"],
        "codigos": "<br/>".join([c if c != "" else "(En blanco)" for c in p["codigos"]]),
        "diagnosticos": "<br/>".join([d if d != "<br/>" else "(En blanco grande)" for d in p["descripciones"]]),
        "labs": "<br/>".join([l if l != "" else "-" for l in p["labs"]]),
        "prd": "<br/>".join([pr if pr != "" else "-" for pr in p["prds"]])
    } for p in st.session_state.lista_pacientes])
    
    st.dataframe(df_preview, use_container_width=True)

    col_btn1, col_btn2 = st.columns(2)
    with col_btn1:
        if st.button("🗑️ Limpiar Toda la Lista"):
            st.session_state.lista_pacientes = []
            st.rerun()

    with col_btn2:
        if st.button("📄 Generar PDF A4 Vertical (Edad Ajustada)"):
            buffer = io.BytesIO()
            doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=10, leftMargin=10, topMargin=10, bottomMargin=10)
            styles = getSampleStyleSheet()

            h_min = ParagraphStyle('HMin', parent=styles['Normal'], fontSize=6.5, leading=7.5, alignment=1, fontName='Helvetica-Bold', textColor=colors.black)
            h_sub = ParagraphStyle('HSub', parent=styles['Normal'], fontSize=5.5, leading=6.5, alignment=1, fontName='Helvetica', textColor=colors.black)
            h_title = ParagraphStyle('HTitle', parent=styles['Normal'], fontSize=7.5, leading=8.5, alignment=1, fontName='Helvetica-Bold', textColor=colors.black)
            
            cell_style = ParagraphStyle('CellStyle', parent=styles['Normal'], fontSize=5.5, leading=6.8, textColor=colors.black)
            cell_center = ParagraphStyle('CellCenter', parent=styles['Normal'], fontSize=5.5, leading=6.8, alignment=1, textColor=colors.black)
            
            # Estilo específico para la edad: tamaño más compacto para que no salte de línea
            cell_edad = ParagraphStyle('CellEdad', parent=styles['Normal'], fontSize=5, leading=6, alignment=1, textColor=colors.black)
            
            header_style = ParagraphStyle('HeaderStyle', parent=styles['Normal'], fontSize=5.8, leading=7, alignment=1, fontName='Helvetica-Bold', textColor=colors.black)

            elements = []

            turno_m = "X" if "Mañana" in turno_op else ""
            turno_t = "X" if "Tarde" in turno_op else ""
            turno_n = "X" if "Noche" in turno_op else ""

            chunks = [st.session_state.lista_pacientes[i:i + 4] for i in range(0, len(st.session_state.lista_pacientes), 4)]

            for page_idx, chunk in enumerate(chunks):
                top_left_data = [
                    [Paragraph("<b>LOTE</b>", cell_style), Paragraph("", cell_style)],
                    [Paragraph("<b>PAGINA</b>", cell_style), Paragraph(f"{page_idx+1:02d}", cell_style)],
                    [Paragraph("<b>FECHA PROC.</b>", cell_style), Paragraph("", cell_style)],
                    [Paragraph("<b>DNI DIGIT.</b>", cell_style), Paragraph("", cell_style)]
                ]
                t_left = Table(top_left_data, colWidths=[35, 44])
                t_left.setStyle(TableStyle([
                    ('GRID', (0,0), (-1,-1), 0.4, colors.black),
                    ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
                    ('BACKGROUND', (0,0), (0,-1), colors.HexColor('#f0f0f0')),
                    ('TOPPADDING', (0,0), (-1,-1), 1),
                    ('BOTTOMPADDING', (0,0), (-1,-1), 1),
                ]))

                top_mid_data = [
                    [Paragraph("MINISTERIO DE SALUD", h_min)],
                    [Paragraph("OFICINA GENERAL DE TECNOLOGIAS DE LA INFORMACION", h_sub)],
                    [Paragraph("UNIDAD DE ESTADISTICA - RED DE SALUD HUAMANGA", h_sub)],
                    [Paragraph("<b>Registro Diario de Atención y Otras Actividades de Salud</b>", h_title)]
                ]
                t_mid = Table(top_mid_data, colWidths=[279])
                t_mid.setStyle(TableStyle([
                    ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
                    ('ALIGN', (0,0), (-1,-1), 'CENTER'),
                    ('BOTTOMPADDING', (0,0), (-1,-1), 1),
                ]))

                top_right_data = [
                    [Paragraph("<b>FIRMA Y SELLO RESPONSABLE HIS MINSA</b>", cell_style)],
                    [Paragraph("<br/><br/>", cell_style)],
                    [Paragraph(f"<b>TURNO:</b> M:[{turno_m}] T:[{turno_t}] N:[{turno_n}]", cell_style)]
                ]
                t_right = Table(top_right_data, colWidths=[120], rowHeights=[12, 22, 12])
                t_right.setStyle(TableStyle([
                    ('GRID', (0,0), (-1,-1), 0.4, colors.black),
                    ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
                    ('ALIGN', (0,0), (-1,-1), 'CENTER'),
                    ('BACKGROUND', (0,0), (0,0), colors.HexColor('#f0f0f0')),
                ]))

                t_header_main = Table([[t_left, t_mid, t_right]], colWidths=[79, 279, 120])
                t_header_main.setStyle(TableStyle([
                    ('VALIGN', (0,0), (-1,-1), 'TOP'),
                    ('LEFTPADDING', (0,0), (-1,-1), 0),
                    ('RIGHTPADDING', (0,0), (-1,-1), 0),
                ]))
                elements.append(t_header_main)
                elements.append(Spacer(1, 4))

                meta_data = [
                    [
                        Paragraph("<b>2. AÑO</b>", header_style),
                        Paragraph("<b>3. MES</b>", header_style),
                        Paragraph("<b>4. NOMBRE DE ESTABLECIMIENTO DE SALUD (IPRESS)</b>", header_style),
                        Paragraph("<b>5. UNIDAD PRODUCTORA DE SERVICIOS (UPSS)</b>", header_style),
                        Paragraph("<b>6. NOMBRE DEL RESPONSABLE DE LA ATENCIÓN</b>", header_style)
                    ],
                    [
                        Paragraph(anio, cell_style),
                        Paragraph(mes.upper(), cell_style),
                        Paragraph(centro_salud, cell_style),
                        Paragraph("OBSTETRICIA", cell_style),
                        Paragraph(f"{re.sub(r'\D', '', dni_profesional)} - {nombres_profesional}", cell_style)
                    ]
                ]
                t_meta = Table(meta_data, colWidths=[30, 50, 150, 100, 148])
                t_meta.setStyle(TableStyle([
                    ('GRID', (0,0), (-1,-1), 0.4, colors.black),
                    ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#e2e8f0')),
                    ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
                    ('ALIGN', (0,0), (-1,-1), 'CENTER'),
                    ('TOPPADDING', (0,0), (-1,-1), 2.5),
                    ('BOTTOMPADDING', (0,0), (-1,-1), 2.5),
                ]))
                elements.append(t_meta)
                elements.append(Spacer(1, 4))

                headers = [
                    Paragraph("<b>N°</b>", header_style),
                    Paragraph("<b>DNI</b>", header_style),
                    Paragraph("<b>Nombres y Apellidos del Paciente</b>", header_style),
                    Paragraph("<b>Edad</b>", header_style),
                    Paragraph("<b>Sexo</b>", header_style),
                    Paragraph("<b>F. Atención</b>", header_style),
                    Paragraph("<b>Antropometría / Hb</b>", header_style),
                    Paragraph("<b>N/C/R</b>", header_style),
                    Paragraph("<b>CIE / CPT</b>", header_style),
                    Paragraph("<b>Actividades / Diagnósticos</b>", header_style),
                    Paragraph("<b>Lab</b>", header_style),
                    Paragraph("<b>P/D/R</b>", header_style)
                ]

                table_data = [headers]
                
                for p in chunk:
                    sub_rows = []
                    for idx, (cod, desc, lab, prd) in enumerate(zip(p["codigos"], p["descripciones"], p["labs"], p["prds"])):
                        sub_rows.append([
                            Paragraph(cod, cell_center),
                            Paragraph(desc, cell_style),
                            Paragraph(lab, cell_center),
                            Paragraph(prd, cell_center)
                        ])

                    sub_style = [
                        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
                        ('TOPPADDING', (0,0), (-1,-1), 1),
                        ('BOTTOMPADDING', (0,0), (-1,-1), 1),
                        ('LEFTPADDING', (0,0), (-1,-1), 1),
                        ('RIGHTPADDING', (0,0), (-1,-1), 1),
                    ]
                    
                    sub_style.append(('TOPPADDING', (0, 9), (-1, 10), 6.5))
                    sub_style.append(('BOTTOMPADDING', (0, 9), (-1, 10), 6.5))

                    for i in range(len(sub_rows) - 1):
                        sub_style.append(('LINEBELOW', (0, i), (-1, i), 0.25, colors.HexColor('#cbd5e0')))

                    t_sub_paciente = Table(sub_rows, colWidths=[40, 114, 18, 18])
                    t_sub_paciente.setStyle(TableStyle(sub_style))

                    table_data.append([
                        Paragraph(str(p["nro"]), cell_center),
                        Paragraph(p["dni"], cell_center),
                        Paragraph(p["nombres"], cell_style),
                        Paragraph(str(p["edad"]), cell_edad),  # <--- Aplicado el estilo ajustado para la edad
                        Paragraph(p["sexo"], cell_center),
                        Paragraph(p["fecha_nac"], cell_center),
                        Paragraph(p["antropometria"], cell_center),
                        Paragraph(p["condicion"], cell_center),
                        t_sub_paciente, "", "", ""
                    ])

                # Ancho de columnas ajustado: Edad pasa de 18 a 23 para evitar saltos
                t = Table(table_data, colWidths=[15, 42, 75, 23, 18, 42, 60, 21, 40, 114, 18, 20])
                
                t_style_commands = [
                    ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#2b6cb0')),
                    ('TEXTCOLOR', (0,0), (-1,0), colors.white),
                    ('ALIGN', (0,0), (-1,-1), 'CENTER'),
                    ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
                    ('GRID', (0,0), (-1,-1), 0.4, colors.black),
                    ('TOPPADDING', (0,0), (-1,-1), 1),
                    ('BOTTOMPADDING', (0,0), (-1,-1), 1),
                    ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor('#f7fafc')])
                ]
                
                for row_idx in range(1, len(chunk) + 1):
                    t_style_commands.append(('SPAN', (8, row_idx), (11, row_idx)))
                    t_style_commands.append(('LEFTPADDING', (8, row_idx), (11, row_idx), 0))
                    t_style_commands.append(('RIGHTPADDING', (8, row_idx), (11, row_idx), 0))
                    t_style_commands.append(('TOPPADDING', (8, row_idx), (11, row_idx), 0))
                    t_style_commands.append(('BOTTOMPADDING', (8, row_idx), (11, row_idx), 0))

                t.setStyle(TableStyle(t_style_commands))
                elements.append(t)

                if page_idx < len(chunks) - 1:
                    elements.append(PageBreak())

            doc.build(elements)
            buffer.seek(0)

            st.download_button(
                label="📥 Descargar PDF A4 Vertical (Edad en una línea)",
                data=buffer,
                file_name="Hoja_HIS_A4_Vertical_Edad_Ajustada.pdf",
                mime="application/pdf"
            )
