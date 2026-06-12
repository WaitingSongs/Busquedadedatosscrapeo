import streamlit as st
import pandas as pd

st.set_page_config(page_title="GameSir Productos", layout="wide")

@st.cache_data
def cargar_datos():
    df = pd.read_csv("productos_gamesir.csv")
    df["categoria"] = df["nombre"].apply(
        lambda x: "🎮 Control" if "Controller" in str(x) else "🔧 Accesorio"
    )
    return df

df = cargar_datos()

st.title("🕹️ GameSir - Catálogo de Productos")

with st.sidebar:
    st.header("🔍 Filtros")
    busqueda = st.text_input("Buscar producto", placeholder="Ej: GameSir X5 Lite...")
    categoria_filtro = st.selectbox("Categoría", ["Todas", "🎮 Control", "🔧 Accesorio"])

filtro = df
if busqueda:
    filtro = filtro[filtro["nombre"].str.contains(busqueda, case=False, na=False)]
if categoria_filtro != "Todas":
    filtro = filtro[filtro["categoria"] == categoria_filtro]

st.write(f"{len(filtro)} producto(s) encontrado(s)")
st.divider()

for _, prod in filtro.iterrows():
    with st.container(border=True):
        cols = st.columns([1, 2])
        with cols[0]:
            st.subheader(prod["nombre"])
            st.caption(f"Categoría: {prod['categoria']}")
            st.write(f"**Precio:** {prod['precio']}")
            st.write(f"**Stock:** {prod['stock']}")
            if pd.notna(prod["colores"]) and prod["colores"]:
                st.write(f"**Colores:** {prod['colores']}")

        with cols[1]:
            if pd.notna(prod["descripcion"]) and prod["descripcion"]:
                with st.expander("📄 Descripción", expanded=True):
                    st.write(prod["descripcion"])
            if pd.notna(prod["detalles"]) and prod["detalles"]:
                with st.expander("📋 Detalles", expanded=True):
                    st.write(prod["detalles"])

        if pd.notna(prod["imagenes"]) and prod["imagenes"]:
            urls = [u.strip() for u in prod["imagenes"].split("|") if u.strip()]
            if urls:
                st.write("**📷 Imágenes:**")
                st.image(urls, width=180, caption=[f"Img {i+1}" for i in range(len(urls))])

        st.caption(f"[🔗 Ver producto]({prod['link']})")
