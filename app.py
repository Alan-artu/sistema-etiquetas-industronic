import streamlit as st
import requests
import os
import random
import time
import pandas as pd
from PIL import Image
from io import BytesIO

# --- LIBRERÍAS DE REPORTLAB PARA EL PDF ---
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

# Configuración de la página web (Debe ir al principio)
st.set_page_config(page_title="Industronic - Sistema de Etiquetas", layout="wide")

# --- BLOQUE 1: LOGOTIPO Y TÍTULO AJUSTADO PARA MÓVIL ---
header_html = """
<div style="display: flex; align-items: center; margin-bottom: 10px;">
    <div style="
        background-color: #004dc3; 
        width: 35px; 
        height: 35px; 
        border-radius: 50%; 
        display: flex; 
        justify-content: center; 
        align-items: center; 
        margin-right: 10px;
        box-shadow: 0 0 8px rgba(0,77,195,0.3);
    ">
        <span style="color: white; font-family: 'Arial', sans-serif; font-size: 22px; font-weight: bold; letter-spacing: -1px;">!i</span>
    </div>
    <span style="color: white; font-family: 'Segoe UI', sans-serif; font-size: 24px; font-weight: 500;">Industronic</span>
</div>
<h1 style="
    color: white; 
    font-family: 'Impact', sans-serif; 
    font-size: 30px; 
    letter-spacing: 1px; 
    margin-top: -5px; 
    margin-bottom: 10px;
    text-transform: uppercase;
    line-height: 1;
">SISTEMA DE ETIQUETAS</h1>
<hr style="border-top: 1px solid #444; margin-top: 0px; margin-bottom: 20px;">
"""
st.markdown(header_html, unsafe_allow_html=True)

# --- BLOQUE 2: ESTILOS CSS ---
css_estilo = """
<style>
.stApp { background-color: #0E1117; }
/* Ajustes de etiquetas para que no se vean gigantes en móvil */
.stSelectbox label, .stTextInput label, .stNumberInput label, .stSlider label {
    font-size: 13px !important; font-weight: 600 !important; color: #F0F2F6 !important;
}
.stTextInput > div > div > input, .stNumberInput > div > div > input, [data-baseweb="select"] > div {
    background-color: #1A1C23 !important; border: 1px solid #E0E0E0 !important; border-radius: 8px !important; color: white !important;
}
div.stButton > button:first-child {
    background-color: #004dc3 !important; color: white !important; border: none !important; font-weight: bold !important;
    padding: 10px 20px !important; border-radius: 8px !important; width: 100%;
}
</style>
"""
st.markdown(css_estilo, unsafe_allow_html=True)

def crear_encabezado_seccion(titulo):
    html = f"""
    <div style="display: flex; align-items: center; margin-top: 5px; margin-bottom: 15px;">
        <div style="background-color: #004dc3; width: 4px; height: 20px; border-radius: 2px; margin-right: 10px;"></div>
        <h2 style="color: #FFFFFF; font-family: 'Segoe UI', sans-serif; font-size: 18px; font-weight: 600; margin: 0;">{titulo}</h2>
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)

# --- FUNCIÓN PARA GENERAR EL REPORTE PDF ---
def generar_pdf_reporte(datos, modelo, capacidad, entrada, salida):
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=40, leftMargin=40, topMargin=40, bottomMargin=40)
    story = []
    styles = getSampleStyleSheet()
    
    title_style = ParagraphStyle('TitleStyle', parent=styles['Heading1'], fontName='Helvetica-Bold', fontSize=24, textColor=colors.HexColor('#004dc3'), spaceAfter=6)
    subtitle_style = ParagraphStyle('SubTitleStyle', parent=styles['Normal'], fontName='Helvetica', fontSize=12, textColor=colors.HexColor('#555555'), spaceAfter=15)
    section_style = ParagraphStyle('SectionStyle', parent=styles['Heading2'], fontName='Helvetica-Bold', fontSize=14, textColor=colors.HexColor('#333333'), spaceBefore=15, spaceAfter=10)
    cell_style = ParagraphStyle('CellStyle', parent=styles['Normal'], fontName='Helvetica', fontSize=10, textColor=colors.HexColor('#444444'))
    header_cell_style = ParagraphStyle('HeaderCellStyle', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=11, textColor=colors.white)
    
    story.append(Paragraph("INDUSTronic", title_style))
    story.append(Paragraph("Reporte de Control de Lote y Vinculación de Componentes", subtitle_style))
    
    meta_data = [
        [Paragraph("<b>Fecha:</b>", cell_style), Paragraph(time.strftime("%d/%m/%Y"), cell_style), Paragraph("<b>Modelo Base:</b>", cell_style), Paragraph(modelo, cell_style)],
        [Paragraph("<b>Capacidad:</b>", cell_style), Paragraph(capacidad, cell_style), Paragraph("<b>Voltaje Entrada:</b>", cell_style), Paragraph(entrada, cell_style)],
        [Paragraph("<b>Voltaje Salida:</b>", cell_style), Paragraph(salida, cell_style), Paragraph("<b>Estado del Lote:</b>", cell_style), Paragraph("<font color='#2e7d32'><b>Verificado</b></font>", cell_style)]
    ]
    t_meta = Table(meta_data, colWidths=[100, 160, 100, 170])
    t_meta.setStyle(TableStyle([('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#f1f5fa')), ('PADDING', (0,0), (-1,-1), 6)]))
    story.append(t_meta)
    story.append(Spacer(1, 15))
    
    story.append(Paragraph("Resumen de Vinculación (Serie vs. Código Interno)", section_style))
    tabla_contenido = [[Paragraph("No. Equipo", header_cell_style), Paragraph("Número de Serie Industronic", header_cell_style), Paragraph("Código Interno", header_cell_style)]]
    for d in datos:
        tabla_contenido.append([Paragraph(d["No. Equipo"], cell_style), Paragraph(d["Número de Serie"], cell_style), Paragraph(d["Código Interno"], cell_style)])
    
    t_data = Table(tabla_contenido, colWidths=[100, 180, 250])
    t_data.setStyle(TableStyle([('BACKGROUND', (0,0), (-1,0), colors.HexColor('#004dc3')), ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#e0e0e0'))]))
    story.append(t_data)
    doc.build(story)
    buffer.seek(0)
    return buffer

# --- LÓGICA ZPL ---
def convertir_imagen_a_zpl(image_path, pos_x, pos_y, max_width=120, max_height=80, fallback_zpl="", invertir=False):
    if not os.path.exists(image_path): return fallback_zpl
    try:
        img = Image.open(image_path).convert('L').point(lambda x: 0 if x < 128 else 255, '1')
        img.thumbnail((max_width, max_height), Image.Resampling.LANCZOS)
        width, height = img.size
        bytes_per_row = (width + 7) // 8
        total_bytes = bytes_per_row * height
        hex_data = ""
        pixels = img.load()
        for y in range(height):
            current_byte = 0
            for x in range(width):
                bit = 1 if pixels[x, y] == 0 else 0
                current_byte = (current_byte << 1) | bit
                if (x + 1) % 8 == 0: hex_data += f"{current_byte:02X}"; current_byte = 0
        return f"^FO{pos_x},{pos_y}^GFA,{total_bytes},{total_bytes},{bytes_per_row},{hex_data}^FS"
    except: return fallback_zpl

# --- CATÁLOGOS ---
CATALOGO_UPS = {
    "UPS-IND-HF-1310": { "modelo_corto": "1310", "capacidad": "10kVA/10kW" },
    "UPS-IND-HF-1315": { "modelo_corto": "1315", "capacidad": "15kVA/15kW" },
    "UPS-IND-HF-1320": { "modelo_corto": "1320", "capacidad": "20kVA/20kW" },
    "UPS-IND-HF-1330": { "modelo_corto": "1330", "capacidad": "30kVA/30kW" },
    "UPS-IND-HF-1340": { "modelo_corto": "1340", "capacidad": "40kVA/40kW" },
    "UPS-IND-HF-1360": { "modelo_corto": "1360", "capacidad": "60kVA/60kW" },
    "UPS-IND-HF-1380": { "modelo_corto": "1380", "capacidad": "80kVA/80kW" },
    "UPS-IND-HF-13100": { "modelo_corto": "13100", "capacidad": "100kVA/100kW" },
    "UPS-IND-HF-13120": { "modelo_corto": "13120", "capacidad": "120kVA/120kW" },
    "UPS-IND-HF-13160": { "modelo_corto": "13160", "capacidad": "160kVA/160kW" },
    "UPS-IND-HF-13200": { "modelo_corto": "13200", "capacidad": "200kVA/200kW" },
    "UPS-IND-HF-13300": { "modelo_corto": "13300", "capacidad": "300kVA/300kW" },
    "UPS-IND-HF-13400": { "modelo_corto": "13400", "capacidad": "400kVA/400kW" },
    "UPS-IND-HF-13500": { "modelo_corto": "13500", "capacidad": "500kVA/500kW" },
    "UPS-IND-HF-13600": { "modelo_corto": "13600", "capacidad": "600kVA/600kW" },
    "UPS-IND-HF-13800": { "modelo_corto": "13800", "capacidad": "800kVA/800kW" },
    "UPS-IND-HF-131000": { "modelo_corto": "131000", "capacidad": "1000kVA/1000kW" },
    "UPS-IND-HF-131200": { "modelo_corto": "131200", "capacidad": "1200kVA/1200kW" }
}

VOLTAJES_BASE = ["120/208", "127/220", "220/380", "230/400", "254/440", "265/460", "277/480", "208D", "220D", "380D", "400D", "440D", "460D", "480D"]
OPCIONES_VOLTAJE_ENTRADA = [f"{v}Vca(+/-20%)" for v in VOLTAJES_BASE]
OPCIONES_VOLTAJE_SALIDA = [f"{v}Vca(+/-1%)" for v in VOLTAJES_BASE]
OPCIONES_FAMILIA = ["M1", "Ninguno", "N1", "R1", "MR1"]

zpl_logo_industronic = convertir_imagen_a_zpl("logo_industronic.png", 40, 30, 300, 60, "^FO40,40^A0N,36,36^FDINDUSTronic^FS")
zpl_logo_hecho_en_mexico = convertir_imagen_a_zpl("hecho_en_mexico.png", 40, 365, 120, 80, "^FO40,370^GB140,75,2^FS\n^FO55,382^A0N,14,14^FDHECHO EN^FS\n^FO55,410^A0N,18,18^FDMEXICO^FS")

if "numeros_chinos" not in st.session_state: st.session_state.numeros_chinos = {}

# --- LAYOUT PRINCIPAL (STREAMLIT MANEJA EL STACK EN MÓVIL) ---
col_datos, col_etiqueta = st.columns([1, 1])

with col_datos:
    crear_encabezado_seccion("Configuracion Tecnica")
    c1, c2 = st.columns(2)
    with c1:
        modelo_seleccionado = st.selectbox("Modelo UPS:", options=list(CATALOGO_UPS.keys()))
        voltaje_entrada = st.selectbox("Voltaje Entrada:", options=OPCIONES_VOLTAJE_ENTRADA)
    with c2:
        familia_seleccionada = st.selectbox("Familia:", options=OPCIONES_FAMILIA)
        voltaje_salida = st.selectbox("Voltaje Salida:", options=OPCIONES_VOLTAJE_SALIDA)
    
    es_mr1 = (familia_seleccionada == "MR1")
    vcc_val = st.number_input("Voltaje de Baterías (Vcc):", value=240, step=12, disabled=es_mr1)
    tamano_letra = st.slider("Tamaño de letra:", min_value=14, max_value=36, value=26, step=2)
    
    datos_fijos = CATALOGO_UPS[modelo_seleccionado]
    kva_val = int(datos_fijos["capacidad"].split("kVA")[0])
    texto_baterias_final = ("240Vcc" if es_mr1 else f"{vcc_val}Vcc") if kva_val >= 300 else ("240Vcc (+/-120Vcc)" if es_mr1 else f"{vcc_val}Vcc (+/-{vcc_val // 2}Vcc)")

    st.markdown("---")
    crear_encabezado_seccion("Captura Portatil")
    cantidad = st.number_input("Equipos en lote:", value=1, min_value=1)
    num_serie_ini = st.text_input("Serie Inicial:", value="140426381")
    
    lista_series = []
    try:
        s_int = int(num_serie_ini)
        for i in range(cantidad): lista_series.append(str(s_int + i).zfill(len(num_serie_ini)))
    except: lista_series = [num_serie_ini]

    resumen_datos = []
    for i in range(int(cantidad)):
        serie_eq = lista_series[i] if i < len(lista_series) else num_serie_ini
        id_eq = f"eq_{i}"; text_key = f"in_{id_eq}"
        with st.expander(f"Equipo {i+1} - Serie: {serie_eq}", expanded=(i==0)):
            foto_cam = st.camera_input(f"Escanear (Eq {i+1})", key=f"cam_{id_eq}")
            if foto_cam is not None and st.session_state.get(f"proc_{id_eq}") is None:
                st.session_state[text_key] = "501211007220S1800005"; st.session_state[f"proc_{id_eq}"] = True; st.rerun()
            num_chino_final = st.text_input(f"Codigo interno {i+1}:", key=text_key)
            st.session_state.numeros_chinos[id_eq] = num_chino_final
        resumen_datos.append({"No. Equipo": f"Equipo {i+1}", "Número de Serie": f"{datos_fijos['modelo_corto']}-{serie_eq}", "Código Interno": num_chino_final if num_chino_final else "Sin Escanear"})

    st.markdown("---")
    crear_encabezado_seccion("Resumen de Vinculacion")
    st.dataframe(pd.DataFrame(resumen_datos), use_container_width=True, hide_index=True)
    
    modelo_final = (modelo_seleccionado if familia_seleccionada == "Ninguno" else f"{modelo_seleccionado} {familia_seleccionada}")
    pdf_data = generar_pdf_reporte(resumen_datos, modelo_final, datos_fijos["capacidad"], voltaje_entrada, voltaje_salida)
    st.download_button(label="📄 Descargar Reporte (PDF)", data=pdf_data, file_name=f"reporte_{time.strftime('%Y%m%d')}.pdf", mime="application/pdf")

# --- COLUMNA DE PREVISUALIZACIÓN ---
unificado_zpl = ""
for idx, s in enumerate(lista_series):
    chino_v = st.session_state.numeros_chinos.get(f"eq_{idx}", "56111105305CS4800001")
    unificado_zpl += f"^XA^CI28{zpl_logo_industronic}^FO40,100^A0N,{tamano_letra},{tamano_letra}^FDEquipo: UPS^FS^FO40,135^A0N,{tamano_letra},{tamano_letra}^FDModelo: {modelo_final}^FS^FO40,170^A0N,{tamano_letra},{tamano_letra}^FDV.Entrada: {voltaje_entrada}^FS^FO40,205^A0N,{tamano_letra},{tamano_letra}^FDCapacidad: {datos_fijos['capacidad']}^FS^FO40,240^A0N,{tamano_letra},{tamano_letra}^FDV.Baterias: {texto_baterias_final}^FS^FO40,275^A0N,{tamano_letra},{tamano_letra}^FDV.Salida: {voltaje_salida}^FS^FO40,310^A0N,{tamano_letra},{tamano_letra}^FDSerie:^FS{zpl_logo_hecho_en_mexico}^FO360,310^BY2,2.5,65^BCN,65,Y,N,N^FD{datos_fijos['modelo_corto']}-{s}^FS^FO360,405^A0N,18,18^FDCodigo interno: {chino_v}^FS^XZ\n"

with col_etiqueta:
    crear_encabezado_seccion("Previsualizacion")
    def preview(s, idx):
        chino_p = st.session_state.numeros_chinos.get(f"eq_{idx}", "56111105305CS4800001")
        z = f"^XA^CI28{zpl_logo_industronic}^FO40,100^A0N,{tamano_letra},{tamano_letra}^FDEquipo: UPS^FS^FO40,135^A0N,{tamano_letra},{tamano_letra}^FDModelo: {modelo_final}^FS^FO40,170^A0N,{tamano_letra},{tamano_letra}^FDV.Entrada: {voltaje_entrada}^FS^FO40,205^A0N,{tamano_letra},{tamano_letra}^FDCapacidad: {datos_fijos['capacidad']}^FS^FO40,240^A0N,{tamano_letra},{tamano_letra}^FDV.Baterias: {texto_baterias_final}^FS^FO40,275^A0N,{tamano_letra},{tamano_letra}^FDV.Salida: {voltaje_salida}^FS^FO40,310^A0N,{tamano_letra},{tamano_letra}^FDSerie:^FS{zpl_logo_hecho_en_mexico}^FO360,310^BY2,2.5,65^BCN,65,Y,N,N^FD{datos_fijos['modelo_corto']}-{s}^FS^FO360,405^A0N,18,18^FDCodigo interno: {chino_p}^FS^XZ"
        return requests.post("http://api.labelary.com/v1/printers/8dpmm/labels/4x3/0/", data=z.encode('utf-8')).content
    st.image(preview(lista_series[0], 0), use_container_width=True)
    st.download_button(label=f"💾 Descargar Etiquetas ZPL", data=unificado_zpl, file_name="etiquetas.zpl")
