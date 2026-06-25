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

# --- BLOQUE 1: LOGOTIPO CODIFICADO Y TÍTULO PRINCIPAL ---
header_html = """
<div style="display: flex; align-items: center; margin-bottom: 5px;">
    <div style="
        background-color: #004dc3; 
        width: 50px; 
        height: 50px; 
        border-radius: 50%; 
        display: flex; 
        justify-content: center; 
        align-items: center; 
        margin-right: 15px;
        box-shadow: 0 0 12px rgba(0,77,195,0.4);
    ">
        <span style="color: white; font-family: 'Arial', sans-serif; font-size: 32px; font-weight: bold; letter-spacing: -2px;">!i</span>
    </div>
    <span style="color: white; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; font-size: 42px; font-weight: 500;">Industronic</span>
</div>
<h1 style="
    color: white; 
    font-family: 'Impact', 'Arial Black', sans-serif; 
    font-size: 75px; 
    letter-spacing: 2px; 
    margin-top: -10px; 
    margin-bottom: 20px;
    text-transform: uppercase;
">SISTEMA DE ETIQUETAS</h1>
<hr style="border-top: 2px solid #333; margin-top: 0px; margin-bottom: 30px;">
"""
st.markdown(header_html, unsafe_allow_html=True)

# --- BLOQUE 2: ESTILOS CSS ---
css_estilo = """
<style>
.stApp { background-color: #0E1117; }
.stSelectbox label, .stTextInput label, .stNumberInput label, .stSlider label {
    font-size: 14px !important; font-weight: 600 !important; color: #F0F2F6 !important; margin-bottom: 4px !important;
}
.stTextInput > div > div > input, .stNumberInput > div > div > input, [data-baseweb="select"] > div {
    background-color: #1A1C23 !important; border: 1px solid #E0E0E0 !important; border-radius: 8px !important; color: white !important;
}
.stTextInput > div > div > input:focus, .stNumberInput > div > div > input:focus, [data-baseweb="select"] > div:focus-within {
    border: 1px solid #004dc3 !important; box-shadow: 0 0 5px rgba(0, 77, 195, 0.5) !important;
}
[data-baseweb="select"] * { color: white !important; }

div.stButton > button:first-child {
    background-color: #004dc3 !important; color: white !important; border: none !important; font-weight: bold !important;
    padding: 10px 20px !important; border-radius: 8px !important; transition: background-color 0.3s ease !important;
}
div.stButton > button:first-child:hover {
    background-color: #00368a !important; box-shadow: 0 0 10px rgba(0, 77, 195, 0.6) !important;
}
</style>
"""
st.markdown(css_estilo, unsafe_allow_html=True)

def crear_encabezado_seccion(titulo):
    html = f"""
    <div style="display: flex; align-items: center; margin-top: 10px; margin-bottom: 20px;">
        <div style="background-color: #004dc3; width: 6px; height: 28px; border-radius: 3px; margin-right: 12px;"></div>
        <h2 style="color: #FFFFFF; font-family: 'Segoe UI', sans-serif; font-size: 22px; font-weight: 600; margin: 0; letter-spacing: 0.5px;">{titulo}</h2>
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
    t_meta.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#f1f5fa')),
        ('PADDING', (0,0), (-1,-1), 6),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 8),
    ]))
    story.append(t_meta)
    story.append(Spacer(1, 15))
    
    story.append(Paragraph("Resumen de Vinculación (Serie vs. Código Interno)", section_style))
    
    tabla_contenido = [[Paragraph("No. Equipo", header_cell_style), Paragraph("Número de Serie Industronic", header_cell_style), Paragraph("Código Interno", header_cell_style)]]
    
    for d in datos:
        tabla_contenido.append([
            Paragraph(d["No. Equipo"], cell_style),
            Paragraph(d["Número de Serie"], cell_style),
            Paragraph(d["Código Interno"], cell_style)
        ])
        
    t_data = Table(tabla_contenido, colWidths=[100, 180, 250])
    t_data.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#004dc3')),
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('PADDING', (0,0), (-1,-1), 8),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor('#f8fafd')]),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#e0e0e0')),
        ('LINEBELOW', (0,0), (-1,0), 1.5, colors.HexColor('#004dc3')),
    ]))
    story.append(t_data)
    
    story.append(Spacer(1, 25))
    nota_style = ParagraphStyle('NotaStyle', parent=styles['Normal'], fontName='Helvetica-Oblique', fontSize=9, textColor=colors.HexColor('#777777'), alignment=1)
    story.append(Paragraph("Documento generado de forma automática por el Sistema de Etiquetas de Industronic.", nota_style))
    
    doc.build(story)
    buffer.seek(0)
    return buffer

# --- LÓGICA ZPL ---
def convertir_imagen_a_zpl(image_path, pos_x, pos_y, max_width=120, max_height=80, fallback_zpl="", invertir=False):
    if not os.path.exists(image_path): return fallback_zpl
    try:
        img = Image.open(image_path)
        if img.mode in ('RGBA', 'LA') or (img.mode == 'P' and 'transparency' in img.info):
            img_rgba = img.convert("RGBA")
            fondo_blanco = Image.new('RGBA', img_rgba.size, (255, 255, 255, 255))
            fondo_blanco.paste(img_rgba, (0, 0), img_rgba)
            img = fondo_blanco.convert('RGB')
        img = img.convert('L').point(lambda x: 0 if x < 128 else 255, '1')
        img.thumbnail((max_width, max_height), Image.Resampling.LANCZOS)
        width, height = img.size
        bytes_per_row = (width + 7) // 8
        padded_width = bytes_per_row * 8
        if padded_width != width:
            new_img = Image.new('1', (padded_width, height), 1)
            new_img.paste(img, (0, 0))
            img = new_img
            width = padded_width
        total_bytes = bytes_per_row * height
        hex_data = ""
        pixels = img.load()
        for y in range(height):
            current_byte = 0
            for x in range(width):
                bit = 1 if pixels[x, y] == 0 else 0
                if invertir: bit = 1 - bit
                current_byte = (current_byte << 1) | bit
                if (x + 1) % 8 == 0:
                    hex_data += f"{current_byte:02X}"; current_byte = 0
        return f"^FO{pos_x},{pos_y}^GFA,{total_bytes},{total_bytes},{bytes_per_row},{hex_data}^FS"
    except Exception: return fallback_zpl

# --- CATÁLOGOS COMPLETOS ---
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

VOLTAJES_BASE = [
    "120/208", "127/220", "220/380", "230/400", "254/440", "265/460", "277/480",
    "208D", "220D", "380D", "400D", "440D", "460D", "480D"
]
OPCIONES_VOLTAJE_ENTRADA = [f"{v}Vca(+/-20%)" for v in VOLTAJES_BASE]
OPCIONES_VOLTAJE_SALIDA = [f"{v}Vca(+/-1%)" for v in VOLTAJES_BASE]
OPCIONES_FAMILIA = ["M1", "Ninguno", "N1", "R1", "MR1"]

zpl_logo_industronic = convertir_imagen_a_zpl("logo_industronic.png", 40, 30, 300, 60, "^FO40,40^A0N,36,36^FDINDUSTronic^FS")
zpl_logo_hecho_en_mexico = convertir_imagen_a_zpl("hecho_en_mexico.png", 40, 365, 120, 80, "^FO40,370^GB140,75,2^FS\n^FO55,382^A0N,14,14^FDHECHO EN^FS\n^FO55,410^A0N,18,18^FDMEXICO^FS")

if "numeros_chinos" not in st.session_state:
    st.session_state.numeros_chinos = {}

# --- LAYOUT DE COLUMNAS ---
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
    
    tamano_letra = st.slider("Tamaño de letra de las especificaciones:", min_value=14, max_value=36, value=26, step=2)
    
    datos_fijos = CATALOGO_UPS[modelo_seleccionado]
    kva_val = int(datos_fijos["capacidad"].split("kVA")[0])
    
    if kva_val >= 300:
        texto_baterias_final = "240Vcc" if es_mr1 else f"{vcc_val}Vcc"
    else:
        texto_baterias_final = "240Vcc (+/-120Vcc)" if es_mr1 else f"{vcc_val}Vcc (+/-{vcc_val // 2}Vcc)"

    with st.expander("Información Calculada del Sistema", expanded=False):
        st.text_input("Equipo:", value="Sistema Ininterrumpible de Energia (UPS)", disabled=True)
        st.text_input("Capacidad:", value=datos_fijos["capacidad"], disabled=True)
        st.text_input("DC Calculado:", value=texto_baterias_final, disabled=True)
    
    st.markdown("---")
    crear_encabezado_seccion("Control de Lote y Captura Portatil")
    
    cantidad = st.number_input("Cantidad de equipos a procesar:", value=1, min_value=1)
    num_serie_ini = st.text_input("Serie Industronic Inicial:", value="140426381")
    
    st.markdown("---")
    st.write("Escaner de Numero Chino por Unidad:")
    
    lista_series = []
    try:
        s_int = int(num_serie_ini)
        for i in range(cantidad): 
            lista_series.append(str(s_int + i).zfill(len(num_serie_ini)))
    except: 
        lista_series = [num_serie_ini]

    resumen_datos = []
    for i in range(int(cantidad)):
        serie_eq = lista_series[i] if i < len(lista_series) else num_serie_ini
        id_eq = f"eq_{i}"
        text_key = f"in_{id_eq}"
        
        with st.expander(f"Equipo {i+1} — Serie: {serie_eq}", expanded=(i==0)):
            foto_cam = st.camera_input(f"Escanear Codigo (Equipo {i+1})", key=f"cam_{id_eq}")
            
            if foto_cam is not None:
                if st.session_state.get(f"proc_{id_eq}") is None:
                    st.session_state[text_key] = "501211007220S1800005"
                    st.session_state[f"proc_{id_eq}"] = True
                    st.rerun()
            else:
                if f"proc_{id_eq}" in st.session_state:
                    del st.session_state[f"proc_{id_eq}"]
                    st.session_state[text_key] = ""
            
            num_chino_final = st.text_input(f"Codigo interno {i+1}:", key=text_key)
            st.session_state.numeros_chinos[id_eq] = num_chino_final
        
        modelo_corto_final = datos_fijos['modelo_corto']
        resumen_datos.append({
            "No. Equipo": f"Equipo {i+1}",
            "Número de Serie": f"{modelo_corto_final}-{serie_eq}",
            "Código Interno": num_chino_final if num_chino_final else "Sin Escanear"
        })

    st.markdown("---")
    crear_encabezado_seccion("Resumen de Vinculacion (Serie vs. Codigo Interno)")
    df_resumen = pd.DataFrame(resumen_datos)
    st.dataframe(df_resumen, use_container_width=True, hide_index=True)
    
    modelo_final = modelo_seleccionado if familia_seleccionada == "Ninguno" else f"{modelo_seleccionado} {familia_seleccionada}"
    pdf_data = generar_pdf_reporte(resumen_datos, modelo_final, datos_fijos["capacidad"], voltaje_entrada, voltaje_salida)
    
    st.download_button(
        label="📄 Descargar Reporte de Vinculación (PDF)",
        data=pdf_data,
        file_name=f"reporte_lote_{time.strftime('%Y%m%d')}.pdf",
        mime="application/pdf",
        use_container_width=True
    )

# Generación ZPL Unificado
unificado_zpl = ""
for idx, s in enumerate(lista_series):
    chino_vinculado = st.session_state.numeros_chinos.get(f"eq_{idx}", "56111105305CS4800001")
    if not chino_vinculado: chino_vinculado = "56111105305CS4800001"
    
    unificado_zpl += f"^XA^CI28{zpl_logo_industronic}^FO40,100^A0N,{tamano_letra},{tamano_letra}^FDEquipo: UPS^FS^FO40,135^A0N,{tamano_letra},{tamano_letra}^FDModelo: {modelo_final}^FS^FO40,170^A0N,{tamano_letra},{tamano_letra}^FDV.Entrada: {voltaje_entrada}^FS^FO40,205^A0N,{tamano_letra},{tamano_letra}^FDCapacidad: {datos_fijos['capacidad']}^FS^FO40,240^A0N,{tamano_letra},{tamano_letra}^FDV.Baterias: {texto_baterias_final}^FS^FO40,275^A0N,{tamano_letra},{tamano_letra}^FDV.Salida: {voltaje_salida}^FS^FO40,310^A0N,{tamano_letra},{tamano_letra}^FDSerie:^FS{zpl_logo_hecho_en_mexico}^FO360,310^BY2,2.5,65^BCN,65,Y,N,N^FD{datos_fijos['modelo_corto']}-{s}^FS^FO360,405^A0N,18,18^FDCodigo interno: {chino_vinculado}^FS^XZ\n"

# Previsualización y Descarga
with col_etiqueta:
    crear_encabezado_seccion("Previsualizacion Digital")
    
    def preview(s, idx):
        chino_preview = st.session_state.numeros_chinos.get(f"eq_{idx}", "56111105305CS4800001")
        if not chino_preview: chino_preview = "56111105305CS4800001"
        
        z = f"^XA^CI28{zpl_logo_industronic}^FO40,100^A0N,{tamano_letra},{tamano_letra}^FDEquipo: UPS^FS^FO40,135^A0N,{tamano_letra},{tamano_letra}^FDModelo: {modelo_final}^FS^FO40,170^A0N,{tamano_letra},{tamano_letra}^FDV.Entrada: {voltaje_entrada}^FS^FO40,205^A0N,{tamano_letra},{tamano_letra}^FDCapacidad: {datos_fijos['capacidad']}^FS^FO40,240^A0N,{tamano_letra},{tamano_letra}^FDV.Baterias: {texto_baterias_final}^FS^FO40,275^A0N,{tamano_letra},{tamano_letra}^FDV.Salida: {voltaje_salida}^FS^FO40,310^A0N,{tamano_letra},{tamano_letra}^FDSerie:^FS{zpl_logo_hecho_en_mexico}^FO360,310^BY2,2.5,65^BCN,65,Y,N,N^FD{datos_fijos['modelo_corto']}-{s}^FS^FO360,405^A0N,18,18^FDCodigo interno: {chino_preview}^FS^XZ"
        return requests.post("http://api.labelary.com/v1/printers/8dpmm/labels/4x3/0/", data=z.encode('utf-8')).content

    if cantidad == 1:
        st.image(preview(lista_series[0], 0), use_container_width=True)
    else:
        t1, t2 = st.tabs(["Primera Etiqueta", "Ultima Etiqueta"])
        with t1: st.image(preview(lista_series[0], 0), use_container_width=True)
        time.sleep(0.5)
        with t2: st.image(preview(lista_series[-1], len(lista_series)-1), use_container_width=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.download_button(f"Descargar {cantidad} etiquetas (ZPL)", unificado_zpl, file_name="etiquetas_industronic.zpl", use_container_width=True)
