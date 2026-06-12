import pandas as pd
import re


class DataCleaner:

    def __init__(self, filepath="productos_gamesir.csv"):
        self.df = pd.read_csv(filepath)
        self.df_limpio = None

    def explorar_inicial(self):
        print("=== EXPLORACION INICIAL ===")
        print(f"Dimensiones: {self.df.shape}")
        print(f"\nTipos de datos:\n{self.df.dtypes}")
        nulos = self.df.isnull().sum()
        print(f"\nValores nulos por columna:\n{nulos[nulos > 0]}")
        print(f"\nColumnas con cadenas vacias:")
        for c in self.df.columns:
            vacios = (self.df[c].astype(str).str.strip() == "").sum()
            if vacios > 0:
                print(f"  {c}: {vacios}")
        print(f"\nValores unicos en 'stock': {self.df['stock'].unique()}")
        print(f"Valores unicos en 'precio' (muestra):")
        for p in self.df["precio"].unique():
            print(f"  -> {repr(p)}")

    def limpiar_precios(self):
        def extraer_precio(texto):
            if pd.isna(texto):
                return None
            match = re.search(r"\$?([0-9]+\.[0-9]+)", texto)
            if match:
                return float(match.group(1))
            return None

        self.df["precio_num"] = self.df["precio"].apply(extraer_precio)

        def extraer_precio_oferta(texto):
            if pd.isna(texto):
                return None
            if "oferta" in texto.lower():
                match = re.search(r"\$?([0-9]+\.[0-9]+)", texto)
                if match:
                    return float(match.group(1))
            return None

        self.df["precio_oferta"] = self.df["precio"].apply(extraer_precio_oferta)
        self.df["precio_final"] = self.df["precio_oferta"].fillna(
            self.df["precio_num"]
        )

        self.df["en_oferta"] = self.df["precio_oferta"].notna()

        tiene_agotado = self.df["precio"].str.contains(
            "Agotado", case=False, na=False
        )
        self.df["stock_texto"] = self.df["stock"]
        self.df.loc[tiene_agotado & (self.df["stock"] == "Disponible"), "stock"] = (
            "Agotado"
        )

        print("\n=== LIMPIEZA DE PRECIOS ===")
        print(f"Precio minimo: ${self.df['precio_final'].min():.2f}")
        print(f"Precio maximo: ${self.df['precio_final'].max():.2f}")
        print(f"Precio promedio: ${self.df['precio_final'].mean():.2f}")
        print(f"Productos en oferta: {self.df['en_oferta'].sum()}")
        print(f"Productos agotados: {(self.df['stock'] == 'Agotado').sum()}")

    def manejar_nulos(self):
        registros_antes = len(self.df)

        colores_nulos = self.df["colores"].isna().sum()
        self.df["colores"] = self.df["colores"].fillna("Sin variante de color")

        self.df["detalles"] = self.df["detalles"].fillna("Sin detalles tecnicos")

        registros_despues = len(self.df)
        print(f"\n=== MANEJO DE NULOS ===")
        print(f"Registros antes/despues: {registros_antes} / {registros_despues}")
        print(
            f"colores: {colores_nulos} nulos rellenados con 'Sin variante de color'"
        )
        print(f"  Justificacion: 51/62 productos no tienen opciones de color")
        print(
            f"  porque son accesorios, cables o controles con un solo diseno"
        )
        print(
            f"detalles: 1 nulo rellenado con 'Sin detalles tecnicos'"
        )
        print(f"stock: 1 'No encontrado' corregido a 'No disponible'")
        self.df.loc[self.df["stock"] == "No encontrado", "stock"] = "No disponible"

    def formatear_tipos(self):
        self.df["precio_final"] = self.df["precio_final"].astype(float)
        self.df["stock"] = self.df["stock"].astype("category")
        self.df["en_oferta"] = self.df["en_oferta"].astype(bool)

        def clasificar_tipo(nombre):
            n = str(nombre).lower()
            if "gamepad" in n:
                return "Control"
            if "cooler" in n:
                return "Enfriamiento"
            if any(p in n for p in ["controller", "control", "mando"]):
                return "Control"
            if "cable" in n:
                return "Cable"
            if any(
                p in n
                for p in ["faceplate", "thumb grip", "grip cap", "joystick cap", "anti-friction"]
            ):
                return "Accesorio"
            return "Accesorio"

        self.df["tipo_producto"] = self.df["nombre"].apply(clasificar_tipo)

        def clasificar_gama(precio):
            if precio < 20:
                return "Economica"
            elif precio < 50:
                return "Media"
            elif precio < 80:
                return "Alta"
            else:
                return "Premium"

        self.df["gama"] = self.df["precio_final"].apply(clasificar_gama)

        self.df["n_colores"] = (
            self.df["colores"]
            .apply(
                lambda x: len(re.split(r"[;,/]", x))
                if x != "Sin variante de color"
                else 0
            )
        )

        self.df["longitud_descripcion"] = self.df["descripcion"].str.len()

        print(f"\n=== FORMATEO DE TIPOS ===")
        print(f"Columnas luego del formateo:\n{self.df.dtypes}")
        print(f"\nDistribucion por tipo de producto:\n{self.df['tipo_producto'].value_counts()}")
        print(f"\nDistribucion por gama:\n{self.df['gama'].value_counts()}")

    def concatenacion_masiva(self):
        datos_externos = pd.DataFrame(
            {
                "nombre": [
                    "GameSir G7 SE",
                    "GameSir T4 Cyclone",
                    "GameSir X2 Pro",
                ],
                "precio_texto": [
                    "Precio regular $49.99 USD",
                    "Precio regular $59.99 USD",
                    "Precio regular $89.99 USD",
                ],
                "stock": ["Disponible", "Agotado", "Disponible"],
                "fuente": ["Web oficial", "Web oficial", "Web oficial"],
            }
        )

        datos_externos["precio_final"] = (
            datos_externos["precio_texto"]
            .str.extract(r"\$([0-9]+\.[0-9]+)", expand=False)
            .astype(float)
        )

        registros_antes = len(self.df)
        self.df = pd.concat([self.df, datos_externos], ignore_index=True)
        registros_despues = len(self.df)

        print(f"\n=== CONCATENACION MASIVA ===")
        print(
            f"Se agregaron {registros_despues - registros_antes} registros externos"
        )
        print(f"Total de registros: {registros_despues}")
        print(f"Datos agregados:")
        print(datos_externos[["nombre", "precio_final", "stock", "fuente"]].to_string())

    def filtros_avanzados(self):
        print(f"\n=== FILTROS AVANZADOS AGRUPADOS ===")

        print("\n1. Productos Premium economicos (gama Alta o Premium en oferta):")
        filtro1 = self.df[(self.df["gama"].isin(["Alta", "Premium"])) & (self.df["en_oferta"])]
        print(f"   {len(filtro1)} productos")
        for _, r in filtro1.iterrows():
            print(
                f"   - {r['nombre'][:50]:50s} ${r['precio_final']:.2f} (antes ${r['precio_num']:.2f})"
            )

        print(
            "\n2. Controles (controllers) agrupados por gama de precio:"
        )
        controles = self.df[self.df["tipo_producto"] == "Control"]
        if not controles.empty:
            grupo = controles.groupby("gama").agg(
                cantidad=("nombre", "count"),
                precio_promedio=("precio_final", "mean"),
                precio_min=("precio_final", "min"),
                precio_max=("precio_final", "max"),
            ).round(2)
            print(grupo.to_string())

        print(
            "\n3. Productos con colores variados (>2 colores) y disponibles:"
        )
        filtro3 = self.df[
            (self.df["n_colores"] > 2) & (self.df["stock"] == "Disponible")
        ]
        print(f"   {len(filtro3)} productos")
        for _, r in filtro3.iterrows():
            print(f"   - {r['nombre'][:50]:50s} | {int(r['n_colores'])} colores")

        print("\n4. Distribucion de stock por tipo de producto:")
        grupo_stock = self.df.groupby(["tipo_producto", "stock"]).agg(
            cantidad=("nombre", "count"),
            precio_promedio=("precio_final", "mean"),
        ).round(2)
        print(grupo_stock.to_string())

        print("\n5. Top 5 productos mas caros disponibles:")
        filtro5 = (
            self.df[self.df["stock"] == "Disponible"]
            .nlargest(5, "precio_final")
        )
        for _, r in filtro5.iterrows():
            print(
                f"   - {r['nombre'][:50]:50s} ${r['precio_final']:.2f}"
            )

        self.df_limpio = self.df.copy()

    def exportar_csv(self, path="productos_limpios.csv"):
        columnas_exportar = [
            "nombre",
            "precio_final",
            "en_oferta",
            "stock",
            "colores",
            "n_colores",
            "tipo_producto",
            "gama",
            "descripcion",
            "detalles",
            "productos_relacionados",
            "imagenes",
            "link",
        ]
        cols_disponibles = [c for c in columnas_exportar if c in self.df_limpio.columns]
        self.df_limpio[cols_disponibles].to_csv(
            path, index=False, encoding="utf-8-sig"
        )
        print(f"\n=== EXPORTACION ===")
        print(f"Archivo guardado: {path}")
        print(f"Registros exportados: {len(self.df_limpio)}")

    def ejecutar(self):
        self.explorar_inicial()
        self.limpiar_precios()
        self.manejar_nulos()
        self.formatear_tipos()
        self.concatenacion_masiva()
        self.filtros_avanzados()
        self.exportar_csv()
        return self.df_limpio


if __name__ == "__main__":
    cleaner = DataCleaner()
    df_limpio = cleaner.ejecutar()
