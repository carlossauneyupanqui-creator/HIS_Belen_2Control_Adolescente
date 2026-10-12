import streamlit as st
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
import io
import datetime
import pandas as pd
import re

st.set_page_config(page_title="Servicio de Obstetricia - 3er Control del Adolescente", layout="wide")

st.markdown("### 🏥 Servicio de Obstetricia")
st.markdown("**Registro para el 3er Control del Adolescente - Formato HIS MINSA (A4 Vertical)**")

if "lista_pacientes" not in st.session_state:
    st.session_state.lista_pacientes = []

# --- DICCIONARIO DE PROFESIONALES Y ESTABLECIMIENTOS ---
PROFESIONALES_DATA = {
    "28293195": {"nombre": "ROCIO INES PARIONA GARAY", "establecimiento": "C.S. Belen"},
    "28294675": {"nombre": "MAYLHI GRETA PRADO SOTO", "establecimiento": "C.S. Belen"},
    "28286827": {"nombre": "PILAR GIULIANA SANCHEZ HUAMANI", "establecimiento": "C.S. Belen"},
    "41321349": {"nombre": "LILIANA ARONI LLANTOY", "establecimiento": "C.S. Belen"},
    "28271583": {"nombre": "ADA MAXIMILIANA ARGAMONTE VILCHEZ", "establecimiento": "C.S. Belen"},
    "44635959": {"nombre": "LIZBETH CARINA CONGA CHOQUECAHUA", "establecimiento": "C.S. Belen"},
    "28308403": {"nombre": "ROSA CECILIA CORDERO QUISPE", "establecimiento": "C.S. Belen"},
    "28288099": {"nombre": "YENY KARIN IPURRE PALOMINO", "establecimiento": "C.S. Belen"},
    "28214069": {"nombre": "GLADYS ELIZABETH SALAZAR PERALTA", "establecimiento": "C.S. Belen"},
    "41679300": {"nombre": "NANCY CUBA ESCALANTE", "establecimiento": "C.S. Belen"},
    "41543063": {"nombre": "BERTHA CHOQUECAHUA SANTIAGO", "establecimiento": "C.S. Belen"},
    "10815848": {"nombre": "ENVER GUERRERO VALDIVIA", "establecimiento": "C.S. Belen"},
    "28225596": {"nombre": "JUANA VILCHEZ ARAMBURU", "establecimiento": "C.S. Belen"},
    "28273980": {"nombre": "CARMEN ROSA SOTO CHUQUICAHUA", "establecimiento": "C.S. Belen"},
    "40625338": {"nombre": "MARILUZ CACÐAHUARAY HUILLCAHUARI", "establecimiento": "C.S. Belen"},
    "28310577": {"nombre": "MIRIAM GUTIERREZ VIVANCO", "establecimiento": "C.S. Belen"},
    "40769895": {"nombre": "YAQUELIN ROCIO CHAVEZ AYALA", "establecimiento": "C.S. Belen"},
    "43971512": {"nombre": "JESSICA BEIBET GOMEZ ALDAZABAL", "establecimiento": "C.S. Belen"},
    "45142977": {"nombre": "MARISOL JUSTINA HUAMANI CALDERON", "establecimiento": "C.S. Belen"},
    "73976363": {"nombre": "DAYSI RIVERA ÐAUPARI", "establecimiento": "C.S. Belen"},
    "28288694": {"nombre": "BRITT CUETO PEREZ", "establecimiento": "P.S. Barrios Altos"},
    "28249696": {"nombre": "ISABEL CRISTINA HUASHUAYO DE LA CRUZ", "establecimiento": "P.S. Barrios Altos"},
    "42847457": {"nombre": "CARMEN ROSA ARONI QUISPE", "establecimiento": "P.S. Barrios Altos"},
    "41458635": {"nombre": "YENY CASTRO RONDINEL", "establecimiento": "P.S. Huascahura"},
    "73051975": {"nombre": "JIMENA FIORELA MARTINEZ BEJAR", "establecimiento": "P.S. Huascahura"},
    "28294032": {"nombre": "NANCY CHANHUALLA TINEO", "establecimiento": "P.S. Morro de Arica"},
    "28202243": {"nombre": "EMMA CARMEN VALLEJO CORAS", "establecimiento": "P.S. Morro de Arica"},
    "31189161": {"nombre": "LISBETH TAIPE TARCO", "establecimiento": "P.S. Morro de Arica"},
    "28316375": {"nombre": "JANETT MARISOL PICHARDO LUJAN", "establecimiento": "P.S. Rancha"},
    "41248331": {"nombre": "GUIULIANA IDALIA TORRES GOMEZ", "establecimiento": "P.S. Santa Ana"},
    "42516121": {"nombre": "YENY ROCIO LOPEZ TODELANO", "establecimiento": "P.S. Santa Ana"},
    "28269044": {"nombre": "JOSE ANTONIO RAMOS ATAURIMA", "establecimiento": "P.S. Santa Ana"},
    "42407587": {"nombre": "JUDITH NELIDA QUISPE ARCE", "establecimiento": "P.S. Santa Ana"},
    "48029513": {"nombre": "CELIA NOEMI YUCRA VELASQUEZ", "establecimiento": "P.S. Santa Ana"}
}

LISTA_ESTABLECIMIENTOS = [
    "C.S. Belen", 
    "P.S. Barrios Altos", 
    "P.S. Huascahura", 
    "P.S. Morro de Arica", 
    "P.S. Rancha", 
    "P.S. Santa Ana"
]

if "dni_seleccionado" not in st.session_state:
    st.session_state.dni_seleccionado = ""

# --- 1. DATOS DEL ESTABLECIMIENTO Y PROFESIONAL ---
st.markdown("#### 1. Datos del Establecimiento y Profesional")
col1, col2, col3 = st.columns(3)
with col1:
    mes = st.selectbox("Mes", ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"], index=8)
with col3:
    turno_op = st.selectbox("Turno", ["Mañana (M)", "Tarde (T)", "Noche (N)"])

col4, col5, col6 = st.columns(3)
with col4:
    anio = st.text_input("Año", "2026")

with col2:
    centro_salud = st.selectbox("Centro de Salud / IPRESS", LISTA_ESTABLECIMIENTOS, key="widget_est")

dnis_disponibles = [""] + [dni for dni, info in PROFESIONALES_DATA.items() if info["establecimiento"] == centro_salud]

if st.session_state.dni_seleccionado not in dnis_disponibles:
    st.session_state.dni_seleccionado = ""

with col5:
    try:
        idx_dni = dnis_disponibles.index(st.session_state.dni_seleccionado)
    except ValueError:
        idx_dni = 0
    
    dni_seleccionado = st.selectbox(
        "DNI del Profesional", 
        dnis_disponibles, 
        index=idx_dni, 
        key="widget_dni"
    )
    st.session_state.dni_seleccionado = dni_seleccionado

with col6:
    nombre_sugerido = PROFESIONALES_DATA.get(dni_seleccionado, {}).get("nombre", "")
    nombres_profesional = st.text_input("Nombres del Profesional", value=nombre_sugerido, placeholder="Apellidos y Nombres", disabled=True)

st.markdown("---")

# --- 2. FORMULARIO DE DATOS DEL PACIENTE ---
st.markdown(f"#### 2. Datos del Paciente, Antropometría y Condición - **3er Control** (Paciente N° {len(st.session_state.lista_pacientes) + 1})")

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
    st.markdown("#### 3. Diagnósticos y Procedimientos Oficiales (3er Control)")
    st.info("Se registrarán automáticamente los códigos normados para el 3er Control del Adolescente.")

    tipo_diagnostico = st.selectbox("Tipo de Diagnóstico / Actividad (HIS)", ["D (Definitivo)", "P (Preventivo)", "R (Repetido)"])

    btn_guardar = st.form_submit_button("➕ Guardar e Ingresar Siguiente", type="primary")

    if btn_guardar:
        dni_pac_limpio = re.sub(r'\D', '', dni_paciente)
        dni_prof_limpio = re.sub(r'\D', '', dni_seleccionado)

        if not dni_prof_limpio or len(dni_prof_limpio) != 8:
            st.error("⚠️ Por favor, seleccione un DNI del Profesional válido de 8 dígitos.")
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

            # CÓDIGOS Y LABS ESPECÍFICOS PARA EL 3ER CONTROL DEL ADOLESCENTE
            codigos = [
                "Z003",
                "99384",
                "99801",
                "99801",
                "99801",
                "99384.02",
                "99402.03",
                "99402.05",
                "99402.08",
                "",
                ""
            ]
            
            descripciones = [
                "EXAMEN DEL ESTADO DE DESARROLLO DEL ADOLESCENTE",
                "ATENCIÓN INTEGRAL DEL ADOLESCENTE",
                "EVALUACIÓN DE LA PRESIÓN ARTERIAL",
                "EVALUACIÓN DEL DESARROLLO SEXUAL (TANNER)",
                "EVALUACIÓN DE LA AGUDEZA VISUAL",
                "EVALUACIÓN DE LA SALUD OCUPACIONAL / ESTUDIOS",
                "CONSEJERÍA EN SALUD SEXUAL Y REPRODUCTIVA",
                "CONSEJERÍA DE PREVENCIÓN DE ENFERMEDADES NO TRANSMISIBLES",
                "CONSEJERÍA EN SALUD MENTAL Y ESTILOS DE VIDA SALUDABLES",
                "<br/>",
                "<br/>"
            ]
            
            labs = [
                "",
                "3",
                "TA",
                "2",
                "1",
                "",
                "2",
                "",
                "2",
                "",
                ""
            ]
            
            prds = [tipo_letra] * 9 + ["", ""]

            nuevo_paciente = {
                "nro": len(st.session_state.lista_pacientes) + 1,
                "dni": dni_pac_limpio,
                "nombres": nombres_paciente,
                "edad": edad_anos,
                "sexo": sexo_letra,
                "dia_atencion": fecha_atencion.strftime("%d"),
                "antropometria": antropometria_text,
                "condicion": cond_letra,
                "codigos": codigos,
                "descripciones": descripciones,
                "labs": labs,
                "prds": prds
            }
            st.session_state.lista_pacientes.append(nuevo_paciente)
            st.success(f"✅ ¡3er Control del Paciente guardado con éxito! (Total registrados: {len(st.session_state.lista_pacientes)})")

# --- 4. LISTA DE PACIENTES REGISTRADOS Y GENERACIÓN DE PDF ---
if len(st.session_state.lista_pacientes) > 0:
    st.markdown("---")
    st.markdown(f"### 📋 Pacientes Registrados ({len(st.session_state.lista_pacientes)})")
    
    df_preview = pd.DataFrame([{
        "nro": p["nro"], "dia": p["dia_atencion"], "dni": p["dni"], "nombres": p["nombres"], "edad": p["edad"], "sexo": p["sexo"],
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
        if st.button("📄 Generar PDF A4 Vertical (3er Control)"):
            buffer = io.BytesIO()
            doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=10, leftMargin=10, topMargin=10, bottomMargin=10)
            styles = getSampleStyleSheet()

            h_min = ParagraphStyle('HMin', parent=styles['Normal'], fontSize=6.5, leading=7.5, alignment=1, fontName='Helvetica-Bold', textColor=colors.black)
            h_sub = ParagraphStyle('HSub', parent=styles['Normal'], fontSize=5.5, leading=6.5, alignment=1, fontName='Helvetica', textColor=colors.black)
            h_title = ParagraphStyle('HTitle', parent=styles['Normal'], fontSize=7.5, leading=8.5, alignment=1, fontName='Helvetica-Bold', textColor=colors.black)
            
            cell_style = ParagraphStyle('CellStyle', parent=styles['Normal'], fontSize=5.5, leading=6.8, textColor=colors.black)
            cell_center = ParagraphStyle('CellCenter', parent=styles['Normal'], fontSize=5.5, leading=6.8, alignment=1, textColor=colors.black)
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
                    ('VALIGN', (0,0),
