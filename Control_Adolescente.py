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
st.markdown("**Registro para el Control del Adolescente - Formato HIS MINSA (A4 Vertical - Día al lado izquierdo del DNI)**")

if "lista_pacientes" not in st.session_state:
    st.session_state.lista_pacientes = []

# --- DICCIONARIO DE PROFESIONALES Y ESTABLECIMIENTOS ---
# Formato: "DNI": {"nombre": "...", "establecimiento": "..."}
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
with col5:
    lista_dnis = [""] + list(PROFESIONALES_DATA.keys())
    dni_seleccionado = st.selectbox("DNI del Profesional", lista_dnis)

# Obtener datos automáticos según el DNI seleccionado
info_profesional = PROFESIONALES_DATA.get(dni_seleccionado, {"nombre": "", "establecimiento": "C.S. Belen"})
nombre_sugerido = info_profesional["nombre"]
establecimiento_sugerido = info_profesional["establecimiento"]

with col2:
    # Índice por defecto para el centro de salud asociado
    try:
        idx_est = LISTA_ESTABLECIMIENTOS.index(establecimiento_sugerido)
    except ValueError:
        idx_est = 0
    centro_salud = st.selectbox("Centro de Salud / IPRESS", LISTA_ESTABLECIMIENTOS, index=idx_est)

with col6:
    nombres_profesional = st.text_input("Nombres del Profesional", value=nombre_sugerido, placeholder="Apellidos y Nombres")

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
        dni_prof_limpio = re.sub(r'\D', '', dni_seleccionado)

        if not dni_prof_limpio or len(dni_prof_limpio) != 8:
            st.error("⚠️ Por favor, seleccione o ingrese un DNI del Profesional válido de 8 dígitos.")
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
                "dia_atencion": fecha_atencion.strftime("%d"),
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
        "nro": p["nro"], "dia": p["dia_atencion"], "dni": p["dni"], "nombres": p["nombres"], "edad": p["edad"], "sex
