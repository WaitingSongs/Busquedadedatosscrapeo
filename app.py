import streamlit as st
import pandas as pd

st.set_page_config(page_title="GameSir Productos", layout="wide")

EMOJIS_TIPO = {
    "Control": "🎮 Control",
    "Accesorio": "🔧 Accesorio",
    "Cable": "🔌 Cable",
    "Enfriamiento": "❄️ Enfriamiento",
}

COLUMNAS = [
    "nombre", "precio_final", "en_oferta", "stock", "colores",
    "n_colores", "tipo_producto", "gama", "descripcion", "detalles",
    "productos_relacionados", "imagenes", "link",
]

@st.cache_data(show_spinner=False)
def cargar_datos():
    try:
        df = pd.read_csv("productos_limpios.csv")
    except FileNotFoundError:
        df = pd.DataFrame(columns=COLUMNAS)
    df["categoria"] = df["tipo_producto"].map(EMOJIS_TIPO)
    return df

df = cargar_datos()

st.title("🕹️ GameSir - Catálogo de Productos")

with st.sidebar:
    st.header("🔍 Filtros")
    busqueda = st.text_input("Buscar producto", placeholder="Ej: GameSir X5 Lite...")
    tipos = ["Todas"] + list(EMOJIS_TIPO.values())
    categoria_filtro = st.selectbox("Tipo", tipos)
    gama_filtro = st.selectbox(
        "Gama", ["Todas", "Economica", "Media", "Alta", "Premium"]
    )

    st.divider()
    if st.button("🔄 Actualizar datos desde la web", type="primary", use_container_width=True):
        from Libraries.scraper import gamesir_scraper
        from Libraries.limpieza import DataCleaner

        with st.spinner("Scrapeando productos..."):
            gamesir_scraper.nuevocsvdeproductos()
        with st.spinner("Limpiando datos..."):
            DataCleaner().ejecutar()
        st.success("Datos actualizados correctamente")
        st.cache_data.clear()
        st.rerun()

filtro = df
if busqueda:
    filtro = filtro[filtro["nombre"].str.contains(busqueda, case=False, na=False)]
if categoria_filtro != "Todas":
    tipo_sel = [k for k, v in EMOJIS_TIPO.items() if v == categoria_filtro][0]
    filtro = filtro[filtro["tipo_producto"] == tipo_sel]
if gama_filtro != "Todas":
    filtro = filtro[filtro["gama"] == gama_filtro]

st.write(f"{len(filtro)} producto(s) encontrado(s)")
st.divider()

for _, prod in filtro.iterrows():
    with st.container(border=True):
        cols = st.columns([1, 2])
        with cols[0]:
            st.subheader(prod["nombre"])
            st.caption(f"{prod['categoria']} · Gama {prod['gama']}")
            badge_oferta = " 🏷️ Oferta" if prod["en_oferta"] else ""
            st.write(f"**Precio:** ${prod['precio_final']:.2f}{badge_oferta}")
            st.write(f"**Stock:** {prod['stock']}")
            if prod["colores"] != "Sin variante de color":
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
