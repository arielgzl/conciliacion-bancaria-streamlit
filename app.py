import streamlit as st
from conciliacion import conciliacion_excel

st.set_page_config(page_title="Conciliación Bancaria", layout="centered")

st.title("📊 Conciliación Bancaria")
st.write("Subí un archivo Excel con dos hojas: **extracto** y **contabilidad** (columnas: `fecha`, `importe`).")

archivo = st.file_uploader("Elegí el archivo Excel", type=["xlsx", "xls"])

if archivo:
    st.success("✅ Archivo cargado correctamente.")
    tolerancia = st.slider("Tolerancia de días para las fechas", 0, 10, 3)

    if st.button("Ejecutar conciliación"):
        try:
            resultado = conciliacion_excel(archivo, tolerancia_dias=tolerancia)
            st.success("Conciliación completada.")

            st.download_button(
                label="📥 Descargar resultado",
                data=resultado,
                file_name="reporte_conciliacion.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
        except Exception as e:
            st.error(f"Error: {e}")
