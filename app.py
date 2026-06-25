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

# --- BLOQUE 1: LOGOTIPO Y TÍTULO ULTRA RESPONSIVO ---
header_html = """
<div style="display: flex; align-items: center; margin-bottom: 5px;">
    <div style="
        background-color: #004dc3; 
        width: 30px; 
        height: 30px; 
        border-radius: 50%; 
        display: flex; 
        justify-content: center; 
        align-items: center; 
        margin-right: 8px;
    ">
        <span style="color: white; font-family: 'Arial', sans-serif; font-size: 18px; font-weight: bold; letter-spacing: -1px;">!i</span>
    </div>
    <span style="color: white; font-family: 'Segoe UI', sans-serif; font-size: 20px; font-weight: 500;">Industronic</span>
</div>
<h1 style="
    color: white; 
    font-family: 'Impact', sans-serif; 
    font-size: 26px; 
    letter-spacing: 1px; 
    margin-top: -5px; 
    margin-bottom: 15px;
    text-transform: uppercase;
    line-height: 1.1;
">SISTEMA DE ETIQUETAS</h1>
"""
st.markdown(header_html, unsafe_allow_html=True)

# --- BLOQUE 2: ESTILOS CSS REFINADOS PARA MÓVIL ---
css_estilo = """
<style>
.stApp { background-color: #0E1117; }

/* Etiquetas de controles estándar */
.stTextInput label, .stNumberInput label, .stSlider label {
    font-size: 13px !important; font-weight: 600 !important; color: #FFFFFF !important;
}

.stTextInput > div > div > input, .stNumberInput > div > div > input {
    background-color: #1A1C23 !important; border: 1px solid #444 !important; border-radius: 8px !important; color: white !important;
}

/* Forzar que los botones de opción (Radio) ocupen todo el ancho de su columna de forma uniforme */
div[data-testid="stRadio"] > div {
    display: flex !important;
    flex-direction: column !important;
    gap: 5px !important;
    width: 100% !important;
}

div[data-testid="stRadio"] label {
    background-color: #1A1C23 !important;
    padding: 8px 10px !important;
    border-radius: 6px !important;
    border: 1px solid #333 !important;
    cursor: pointer !important;
    font-size: 12px !important;
    display: flex !important;
    width: 100% !important;
}

/* Ocultar etiquetas por defecto de los radio buttons internos para usar nuestros títulos personalizados */
div[data-testid="stRadio"] label[data-testid="stWidgetLabel"] {
    display: none !important;
}

/* Diseño de botones principales */
div.stButton > button:first-child {
    background-color: #004dc3 !important; color: white !important; border: none !important; font-weight: bold !important;
    padding: 12px 20px !important; border-radius: 8px !important; width: 100%; font-size: 14px !important;
}
</style>
"""
st.markdown(css_estilo, unsafe_allow_html=True)

# Formato estético tipo banner para los títulos de sección
def crear_caja_titulo(titulo, color_borde="#004dc3"):
    html = f"""
    <div style="
        background-color: #141824; 
        padding: 10px 14px; 
        border-radius: 8px; 
        border-left: 4px solid {color_borde}; 
        margin-top: 15px; 
        margin-bottom: 10px;
    ">
        <h2 style="color: #FFFFFF; font-family: 'Segoe UI', sans-serif; font-size: 14px; font-weight: 600; margin: 0; letter-spacing: 0.5px;">{titulo}</h2>
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

# --- CATÁLOGOS COMPLETOS ---
LISTA_MODELOS = ["1310", "1315", "1320", "1330", "1340", "1360", "1380", "13100", "1312", "1316", "13200", "13300", "13400", "13500", "13600", "13800", "131000", "131200"]
CATALOGO_UPS = {
    "1310": { "modelo_completo": "UPS-IND-HF-1310", "capacidad": "10kVA/10kW" },
    "1315": { "modelo_completo": "UPS-IND-HF-1315", "capacidad": "15kVA/15kW" },
    "1320": { "modelo_completo": "UPS-IND-HF-1320", "capacidad": "20kVA/20kW" },
    "1330": { "modelo_completo": "UPS-IND-HF-1330", "capacidad": "30kVA/30kW" },
    "1340": { "modelo_completo": "UPS-IND-HF-1340", "capacidad": "40kVA/40kW" },
    "1360": { "modelo_completo": "UPS-IND-HF-1360", "capacidad": "60kVA/60kW" },
    "1380": { "modelo_completo": "UPS-IND-HF-1380", "capacidad": "80kVA/80kW" },
    "13100": { "modelo_completo": "UPS-IND-HF-13100", "capacidad": "100kVA/100kW" },
    "1312": { "modelo_completo": "UPS-IND-HF-13120", "capacidad": "120kVA/120kW" },
    "1316": { "modelo_completo": "UPS-IND-HF-13160", "capacidad": "160kVA/160kW" },
    "13200": { "modelo_completo": "UPS-IND-HF-13200", "capacidad": "200kVA/200kW" },
    "13300": { "modelo_completo": "UPS-IND-HF-13300", "capacidad": "300kVA/300kW" },
    "13400": { "modelo_completo": "UPS-IND-HF-13400", "capacidad": "400kVA/400kW" },
    "13500": { "modelo_completo": "UPS-IND-HF-13500", "capacidad": "500kVA/500kW" },
    "13600": { "modelo_completo": "UPS-IND-HF-13600", "capacidad": "600kVA/600kW" },
    "13800": { "modelo_completo": "UPS-IND-HF-13800", "capacidad": "800kVA/800kW" },
    "131000": { "modelo_completo": "UPS-IND-HF-131000", "capacidad": "1000kVA/1000kW" },
    "131200": { "modelo_completo": "UPS-IND-HF-131200", "capacidad": "1200kVA/1200kW" }
}

VOLTAJES_ESTRELLA = ["120_208", "127_220", "220_380", "230_400", "254_440", "265_460", "277_480"]
VOLTAJES_DELTA = ["208D", "220D", "380D", "400D", "440D", "460D", "480D"]
OPCIONES_FAMILIA = ["M1", "Ninguno", "N1", "R1", "MR1"]

if "numeros_chinos" not in st.session_state: st.session_state.numeros_chinos = {}

col_datos, col_etiqueta = st.columns([1, 1])

with col_datos:
    # --- SECCIÓN: MODELO UPS (Distribuido equitativamente en 2 columnas móviles) ---
    crear_caja_titulo("MODELO UPS")
    c_mod1, c_mod2 = st.columns(2)
    with c_mod1:
        # Primera mitad de los modelos
        mod_col1 = st.radio("M1", options=LISTA_MODELOS[:9], format_func=lambda x: CATALOGO_UPS[x]["modelo_completo"], key="mod_c1")
    with c_mod2:
        # Segunda mitad de los modelos
        mod_col2 = st.radio("M2", options=LISTA_MODELOS[9:], format_func=lambda x: CATALOGO_UPS[x]["modelo_completo"], key="mod_c2")
    
    # Interruptor silencioso que determina cuál columna tocó el operador por última vez
    control_col = st.radio("Filtro", options=["Bloque 1", "Bloque 2"], horizontal=True, label_visibility="collapsed")
    modelo_seleccionado = mod_col1 if control_col == "Bloque 1" else mod_col2

    # --- SECCIÓN: FAMILIA ---
    crear_caja_titulo("FAMILIA")
    c_fam1, c_fam2 = st.columns(2)
    with c_fam1:
        fam_p1 = st.radio("F1", options=OPCIONES_FAMILIA[:3], key="fam_p1")
    with c_fam2:
        fam_p2 = st.radio("F2", options=OPCIONES_FAMILIA[3:], key="fam_p2")
    
    control_fam = st.radio("FiltroFam", options=["Parte 1", "Parte 2"], horizontal=True, label_visibility="collapsed")
    familia_seleccionada = fam_p1 if control_fam == "Parte 1" else fam_p2

    # --- SECCIÓN: VOLTAJES DE ENTRADA (Separado visualmente Estrella vs Delta) ---
    crear_caja_titulo("VOLTAJES DE ENTRADA")
    c_in_y, c_in_d = st.columns(2)
    with c_in_y:
        st.markdown("<p style='font-size:12px; color:#888; font-weight:bold; margin-bottom:2px; text-align:center;'>Conexión Estrella (Y)</p>", unsafe_allow_html=True)
        v_ent_y = st.radio("Y_IN", options=VOLTAJES_ESTRELLA, format_func=lambda x: f"{x.replace('_', '/')} Vca")
    with c_in_d:
        st.markdown("<p style='font-size:12px; color:#888; font-weight:bold; margin-bottom:2px; text-align:center;'>Conexión Delta (D)</p>", unsafe_allow_html=True)
        v_ent_d = st.radio("D_IN", options=VOLTAJES_DELTA, format_func=lambda x: f"{x} Vca")
    
    tipo_in = st.radio("Tipo In", options=["Estrella", "Delta"], horizontal=True, label_visibility="collapsed")
    voltaje_entrada_final = v_ent_y if tipo_in == "Estrella" else v_ent_d
    v_entrada_label = f"{voltaje_entrada_final.replace('_', '/')}Vca(+/-20%)"

    # --- SECCIÓN: VOLTAJES DE SALIDA (Separado visualmente Estrella vs Delta) ---
    crear_caja_titulo("VOLTAJES DE SALIDA")
    c_out_y, c_out_d = st.columns(2)
    with c_out_y:
        st.markdown("<p style='font-size:12px; color:#888; font-weight:bold; margin-bottom:2px; text-align:center;'>Conexión Estrella (Y)</p>", unsafe_allow_html=True)
        v_sal_y = st.radio("Y_OUT", options=VOLTAJES_ESTRELLA, format_func=lambda x: f"{x.replace('_', '/')} Vca")
    with c_out_d:
        st.markdown("<p style='font-size:12px; color:#888; font-weight:bold; margin-bottom:2px; text-align:center;'>Conexión Delta (D)</p>", unsafe_allow_html=True)
        v_sal_d = st.radio("D_OUT", options=VOLTAJES_DELTA, format_func=lambda x: f"{x} Vca")
        
    tipo_out = st.radio("Tipo Out", options=["Estrella", "Delta"], horizontal=True, label_visibility="collapsed")
    voltaje_salida_final = v_sal_y if tipo_out == "Estrella" else v_sal_d
    v_salida_label = f"{voltaje_salida_final.replace('_', '/')}Vca(+/-1%)"

    # Resto de parámetros dinámicos fijos
    es_mr1 = (familia_seleccionada == "MR1")
    vcc_val = st.number_input("Voltaje de Baterías (Vcc):", value=240, step=12)
    tamano_letra = st.slider("Tamaño de letra en etiqueta:", min_value=14, max_value=36, value=26, step=2)
    
    datos_fijos = CATALOGO_UPS[modelo_seleccionado]
    kva_val = int(datos_fijos["capacidad"].split("kVA")[0])
    texto_baterias_final = ("240Vcc" if es_mr1 else f"{vcc_val}Vcc") if kva_val >= 300 else ("240Vcc (+/-120Vcc)" if es_mr1 else f"{vcc_val}Vcc (+/-{vcc_val // 2}Vcc)")

    # --- SECCIÓN CAPTURA ---
    crear_caja_titulo("CAPTURA PORTÁTIL DE COMPONENTES", color_borde="#2e7d32")
    cantidad = st.number_input("Equipos en lote:", value=1, min_value=1)
    num_serie_ini = st.text_input("Serie Inicial Industronic:", value="140426381")
    
    lista_series = []
    try:
        s_int = int(num_serie_ini)
        for i in range(cantidad): lista_series.append(str(s_int + i).zfill(len(num_serie_ini)))
    except: lista_series = [num_serie_ini]

    resumen_datos = []
    for i in range(int(cantidad)):
        serie_eq = lista_series[i] if i < len(lista_series) else num_serie_ini
        id_eq = f"eq_{i}"; text_key = f"in_{id_eq}"
        with st.expander(f"📷 Escáner Unidad {i+1} - Serie: {serie_eq}", expanded=(i==0)):
            foto_cam = st.camera_input(f"Capturar Código", key=f"cam_{id_eq}")
            if foto_cam is not None and st.session_state.get(f"proc_{id_eq}") is None:
                st.session_state[text_key] = "501211007220S1800005"; st.session_state[f"proc_{id_eq}"] = True; st.rerun()
            num_chino_final = st.text_input(f"Código interno {i+1}:", key=text_key)
            st.session_state.numeros_chinos[id_eq] = num_chino_final
        resumen_datos.append({"No. Equipo": f"Equipo {i+1}", "Número de Serie": f"{modelo_seleccionado}-{serie_eq}", "Código Interno": num_chino_final if num_chino_final else "Sin Escanear"})

    # --- SECCIÓN RESUMEN ---
    crear_caja_titulo("RESUMEN DE VINCULACIÓN Y REPORTES", color_borde="#e65100")
    st.dataframe(pd.DataFrame(resumen_datos), use_container_width=True, hide_index=True)
    
    modelo_final = (datos_fijos["modelo_completo"] if familia_seleccionada == "Ninguno" else f"{datos_fijos["modelo_completo"]} {familia_seleccionada}")
    pdf_data = generar_pdf_reporte(resumen_datos, modelo_final, datos_fijos["capacidad"], v_entrada_label, v_salida_label)
    st.download_button(label="📄 Descargar Reporte Completo (PDF)", data=pdf_data, file_name=f"reporte_{time.strftime('%Y%m%d')}.pdf", mime="application/pdf")

# --- COLUMNA DE PREVISUALIZACIÓN ---
with col_etiqueta:
    crear_caja_titulo("PREVISUALIZACIÓN DIGITAL DE ETIQUETA", color_borde="#7b1fa2")
    
    unificado_zpl = ""
    for idx, s in enumerate(lista_series):
        chino_v = st.session_state.numeros_chinos.get(f"eq_{idx}", "56111105305CS4800001")
        unificado_zpl += f"^XA^CI28^FO40,100^A0N,{tamano_letra},{tamano_letra}^FDEquipo: UPS^FS^FO40,135^A0N,{tamano_letra},{tamano_letra}^FDModelo: {modelo_final}^FS^FO40,170^A0N,{tamano_letra},{tamano_letra}^FDV.Entrada: {v_entrada_label}^FS^FO40,205^A0N,{tamano_letra},{tamano_letra}^FDCapacidad: {datos_fijos['capacidad']}^FS^FO40,240^A0N,{tamano_letra},{tamano_letra}^FDV.Baterias: {texto_baterias_final}^FS^FO40,275^A0N,{tamano_letra},{tamano_letra}^FDV.Salida: {v_salida_label}^FS^FO40,310^A0N,{tamano_letra},{tamano_letra}^FDSerie:^FS^FO360,310^BY2,2.5,65^BCN,65,Y,N,N^FD{modelo_seleccionado}-{s}^FS^FO360,405^A0N,18,18^FDCodigo interno: {chino_v}^FS^XZ\n"

    def preview(s, idx):
        chino_p = st.session_state.numeros_chinos.get(f"eq_{idx}", "56111105305CS4800001")
        z = f"^XA^CI28^FO40,100^A0N,{tamano_letra},{tamano_letra}^FDEquipo: UPS^FS^FO40,135^A0N,{tamano_letra},{tamano_letra}^FDModelo: {modelo_final}^FS^FO40,170^A0N,{tamano_letra},{tamano_letra}^FDV.Entrada: {v_entrada_label}^FS^FO40,205^A0N,{tamano_letra},{tamano_letra}^FDCapacidad: {datos_fijos['capacidad']}^FS^FO40,240^A0N,{tamano_letra},{tamano_letra}^FDV.Baterias: {texto_baterias_final}^FS^FO40,275^A0N,{tamano_letra},{tamano_letra}^FDV.Salida: {v_salida_label}^FS^FO40,310^A0N,{tamano_letra},{tamano_letra}^FDSerie:^FS^FO360,310^BY2,2.5,65^BCN,65,Y,N,N^FD{modelo_seleccionado}-{s}^FS^FO360,405^A0N,18,18^FDCodigo interno: {chino_p}^FS^XZ"
        return requests.post("http://api.labelary.com/v1/printers/8dpmm/labels/4x3/0/", data=z.encode('utf-8')).content
    
    st.image(preview(lista_series[0], 0), use_container_width=True)
    st.download_button(label=f"💾 Descargar Código de Impresión (.ZPL)", data=unificado_zpl, file_name="etiquetas.zpl")
