import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split, GridSearchCV, cross_val_score
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score
from sklearn.preprocessing import LabelEncoder


class GamaPredictor:

    def __init__(self, filepath="productos_limpios.csv"):
        self.df = pd.read_csv(filepath)
        self.model = None
        self.le_gama = LabelEncoder()
        self.feature_names = None
        self.best_params = None
        self.cv_score_before = None
        self.cv_score_after = None
        self.test_score = None

    def preparar_datos(self):
        self.df_filtrado = self.df.dropna(subset=["gama"]).copy()
        df = self.df_filtrado

        df["en_oferta"] = df["en_oferta"].astype(int)
        df["n_colores"] = df["n_colores"].fillna(0).astype(int)
        df["longitud_descripcion"] = df["descripcion"].fillna("").str.len()

        stock_map = {"Disponible": 0, "Agotado": 1, "No disponible": 2}
        df["stock_cod"] = df["stock"].map(stock_map).fillna(0)

        tipo_dummies = pd.get_dummies(df["tipo_producto"], prefix="tipo")

        cols_num = ["n_colores", "en_oferta", "longitud_descripcion", "stock_cod"]
        X = pd.concat([df[cols_num].reset_index(drop=True), tipo_dummies.reset_index(drop=True)], axis=1)
        y = self.le_gama.fit_transform(df["gama"])

        self.feature_names = X.columns.tolist()
        return X, y

    def ejecutar(self):
        print("=== MODELADO PREDICTIVO: PREDICCION DE GAMA ===")
        print(f"\nCargados {len(self.df)} registros")

        X, y = self.preparar_datos()
        print(f"Features: {self.feature_names}")
        print(f"Clases: {dict(enumerate(self.le_gama.classes_))}")
        print(f"Distribucion: {pd.Series(y).value_counts().to_dict()}")

        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.25, random_state=42, stratify=y
        )
        print(f"\nTrain: {len(X_train)} | Test: {len(X_test)}")

        modelo_base = RandomForestClassifier(random_state=42)
        self.cv_score_before = cross_val_score(
            modelo_base, X_train, y_train, cv=5, scoring="accuracy"
        )
        print(f"\n--- Modelo Base (sin optimizar) ---")
        print(f"Cross-Validation Accuracy: {self.cv_score_before.mean():.4f} (+/- {self.cv_score_before.std():.4f})")

        modelo_base.fit(X_train, y_train)
        y_pred_base = modelo_base.predict(X_test)
        acc_base = accuracy_score(y_test, y_pred_base)
        print(f"Test Accuracy (base): {acc_base:.4f}")

        param_grid = {
            "n_estimators": [50, 100, 200],
            "max_depth": [None, 10, 20],
            "min_samples_split": [2, 5],
            "min_samples_leaf": [1, 2],
        }

        print(f"\n--- Busqueda de hiperparametros (GridSearchCV) ---")
        print(f"Grid: {param_grid}")
        print(f"Folders CV: 5")

        rf = RandomForestClassifier(random_state=42)
        grid = GridSearchCV(
            rf,
            param_grid,
            cv=5,
            scoring="accuracy",
            n_jobs=1,
            verbose=0,
        )
        grid.fit(X_train, y_train)

        self.best_params = grid.best_params_
        self.model = grid.best_estimator_
        self.cv_score_after = grid.best_score_

        print(f"\nMejores hiperparametros: {grid.best_params_}")
        print(f"Mejor CV Accuracy: {grid.best_score_:.4f}")

        mejora = (grid.best_score_ - self.cv_score_before.mean()) / self.cv_score_before.mean() * 100
        print(f"Mejora respecto al base: {mejora:+.2f}%")

        y_pred = grid.predict(X_test)
        self.test_score = accuracy_score(y_test, y_pred)
        print(f"\nTest Accuracy (optimizado): {self.test_score:.4f}")

        print(f"\n=== REPORTE DE CLASIFICACION ===")
        print(classification_report(y_test, y_pred, target_names=self.le_gama.classes_))

        print(f"\n=== MATRIZ DE CONFUSION ===")
        cm = confusion_matrix(y_test, y_pred)
        print(pd.DataFrame(cm, index=self.le_gama.classes_, columns=self.le_gama.classes_).to_string())

        importancia = pd.DataFrame({
            "feature": self.feature_names,
            "importance": self.model.feature_importances_
        }).sort_values("importance", ascending=False)
        print(f"\n=== IMPORTANCIA DE FEATURES ===")
        print(importancia.to_string(index=False))

        self.mostrar_predicciones(X)

        return self.model

    def mostrar_predicciones(self, X_full):
        y_pred = self.model.predict(X_full)
        gamas_pred = self.le_gama.inverse_transform(y_pred)
        gamas_real = self.df_filtrado["gama"].values

        resultados = pd.DataFrame({
            "Producto": self.df_filtrado["nombre"].values,
            "Gama real": gamas_real,
            "Gama predicha": gamas_pred,
        })
        resultados["Acierto"] = resultados["Gama real"] == resultados["Gama predicha"]
        self.resultados = resultados

        print(f"\n=== PREDICCIONES POR PRODUCTO ===")
        aciertos = resultados["Acierto"].sum()
        total = len(resultados)
        print(f"Acertados: {aciertos}/{total} ({aciertos/total*100:.1f}%)")
        print()
        for _, r in resultados.iterrows():
            marca = "✅" if r["Acierto"] else "❌"
            print(f"  {marca} {r['Producto'][:55]:55s} | Real: {r['Gama real']:10s} | Pred: {r['Gama predicha']:10s}")

    def predecir(self, datos):
        if self.model is None:
            raise ValueError("Ejecuta .ejecutar() primero")
        return self.le_gama.inverse_transform(self.model.predict(datos))


if __name__ == "__main__":
    predictor = GamaPredictor()
    predictor.ejecutar()
