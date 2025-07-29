import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from wqchartpy import triangle_piper, durvo, stiff, schoeller  # ← ahora incluye schoeller
import matplotlib.colors as mcolors

st.set_page_config(page_title="Geoquímica | Diagramas", layout="wide")
st.title("App de Geoquímica: Diagramas Piper, Durov, Stiff y Schoeller")
st.markdown("""
Autor: Daniel Osorio Álvarez (dosorioalv@gmail.com).  
Sube tu archivo **Excel (.xlsx)** con datos geoquímicos.  
Formato recomendado: columnas para Ca, Mg, Na, K, HCO3, CO3, Cl, SO4, pH, TDS, Sample, Label, etc.

Se utiliza la librería WQChartPy (Yang, J., Liu, H., Tang, Z., Peeters, L. and Ye, M. (2022), Visualization of Aqueous Geochemical Data Using Python and WQChartPy. Groundwater. https://doi.org/10.1111/gwat.13185)
""")


st.subheader("Ejemplo de formato de datos para cargar:")

template_path = "prueba_diagramas.xlsx"  # Asegúrate que esté en la misma carpeta
df_template = pd.read_excel(template_path)
st.dataframe(df_template.head(10), use_container_width=True)

with open(template_path, "rb") as file_template:
    st.download_button(
        label="Descargar archivo de ejemplo (template)",
        data=file_template,
        file_name="template_geoquimica.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )


file = st.file_uploader("Carga tu archivo Excel (.xlsx)", type=['xlsx'])

if file is not None:
    df = pd.read_excel(file)
    st.write("Vista previa de los datos cargados:")
    st.dataframe(df.head())

    # Definición de columnas esperadas
    col_piper = ['Ca', 'Mg', 'Na', 'K', 'HCO3', 'CO3', 'Cl', 'SO4']
    col_durvo = col_piper + ['pH', 'TDS']
    col_aux = ['Label', 'Color', 'Marker', 'Size', 'Alpha']
    col_stiff = ['Ca', 'Mg', 'Na', 'K', 'HCO3', 'Cl', 'SO4', 'Sample', 'Label']
    col_schoeller = col_piper

    # Completa columnas faltantes con valores por defecto
    for col in col_durvo:
        if col not in df.columns:
            df[col] = np.nan
    if 'Label' not in df.columns:
        df['Label'] = df['Sample'].astype(str) if 'Sample' in df.columns else df.index.astype(str)
    if 'Marker' not in df.columns:
        df['Marker'] = 'o'
    if 'Size' not in df.columns:
        df['Size'] = 40
    if 'Alpha' not in df.columns:
        df['Alpha'] = 1.0

    # Asigna colores automáticos a cada Label
    unique_labels = df['Label'].unique()
    cmap = plt.get_cmap('tab10')  # Cambia a 'tab20', 'Set2', etc. si tienes muchos grupos
    label_to_color = {label: mcolors.rgb2hex(cmap(i % cmap.N)) for i, label in enumerate(unique_labels)}
    df['Color_piper'] = df['Label'].map(label_to_color)
    df['Color_durvo'] = df['Label'].map(label_to_color)

    # Sidebar
    st.sidebar.title("Opciones de gráfico")
    tipo_diagrama = st.sidebar.selectbox("Selecciona el diagrama", ("Piper", "Durov", "Stiff", "Schoeller"))

    if tipo_diagrama == "Piper":
        df_piper = df[col_piper + ['Label', 'Color_piper', 'Marker', 'Size', 'Alpha']].copy()
        df_piper.rename(columns={'Color_piper': 'Color'}, inplace=True)
        df_piper_plot = df_piper.dropna(subset=col_piper)
        if not df_piper_plot.empty:
            plt.close('all')
            triangle_piper.plot(df_piper_plot)
            fig = plt.gcf()
            st.pyplot(fig)
        else:
            st.warning("No hay muestras completas para graficar Piper.")

    elif tipo_diagrama == "Durov":
        df_durvo = df[col_durvo + ['Label', 'Color_durvo', 'Marker', 'Size', 'Alpha']].copy()
        df_durvo.rename(columns={'Color_durvo': 'Color'}, inplace=True)
        df_durvo_plot = df_durvo.dropna(subset=col_durvo)
        if not df_durvo_plot.empty:
            plt.close('all')
            durvo.plot(df_durvo_plot)
            fig = plt.gcf()
            st.pyplot(fig)
        else:
            st.warning("No hay muestras completas para graficar Durov.")

    elif tipo_diagrama == "Stiff":
        df_stiff = df.copy()
        for col in col_stiff:
            if col not in df_stiff.columns:
                if col == 'Label' and 'Sample' in df_stiff.columns:
                    df_stiff['Label'] = df_stiff['Sample'].astype(str)
                else:
                    df_stiff[col] = np.nan
        df_stiff_plot = df_stiff.dropna(subset=['Ca', 'Mg', 'Na', 'K', 'HCO3', 'Cl', 'SO4', 'Sample'])
        if not df_stiff_plot.empty:
            plt.close('all')
            stiff.plot(df_stiff_plot)
            for fignum in plt.get_fignums():
                fig = plt.figure(fignum)
                st.pyplot(fig)
        else:
            st.warning("No hay muestras completas para graficar Stiff.")

    elif tipo_diagrama == "Schoeller":
        df_schoeller = df.copy()
        required_cols = ['Ca', 'Mg', 'Na', 'K', 'HCO3', 'CO3', 'Cl', 'SO4']
        for col in required_cols:
            if col not in df_schoeller.columns:
                df_schoeller[col] = np.nan
        if 'Label' not in df_schoeller.columns:
            df_schoeller['Label'] = df_schoeller['Sample'].astype(str) if 'Sample' in df_schoeller.columns else df_schoeller.index.astype(str)
        
        # Asigna colores si no existe columna Color
        if 'Color' not in df_schoeller.columns:
            df_schoeller['Color'] = df_schoeller['Label'].map(label_to_color)

        df_schoeller_plot = df_schoeller.dropna(subset=required_cols)
        if not df_schoeller_plot.empty:
            plt.close('all')
            schoeller.plot(df_schoeller_plot, unit='mg/L')
            fig = plt.gcf()
            st.pyplot(fig)
        else:
            st.warning("No hay muestras completas para graficar Schoeller.")

else:
    st.info("Carga un archivo Excel para comenzar.")
