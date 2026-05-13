import pandas as pd
from sklearn.decomposition import PCA
from sklearn.preprocessing import MinMaxScaler

#def para aplicar los 3 pc
def aplicar_pca(df: pd.DataFrame) -> pd.DataFrame:
    #columnas de comportamiento para el pca
    columnas = [
        "monto", "gastos_mensuales", "ingresos", "puntos_lealtad",
        "edad", "lat", "lon",
        "monto", "id_tienda"
    ]

    #solo usar columnas que existan en el df
    columnas = [c for c in columnas if c in df.columns]

    #para eliminar filas con nulos en esas columnas
    df_pca = df[columnas].dropna()

    #pa que escale antes del pca
    scaler = MinMaxScaler()
    df_escalado = scaler.fit_transform(df_pca)

    #aplicar pca y reducir a 3 componentes
    pca = PCA(n_components=3)
    componentes = pca.fit_transform(df_escalado)

    #pa agregar los 3 componentes al df original
    df_resultado = df.loc[df_pca.index].copy()
    df_resultado["PC1"] = componentes[:, 0]
    df_resultado["PC2"] = componentes[:, 1]
    df_resultado["PC3"] = componentes[:, 2]

    #mostrar varianza explicada por cada componente
    varianza = pca.explained_variance_ratio_
    print(f"Varianza explicada:")
    print(f"  PC1: {varianza[0]:.2%}")
    print(f"  PC2: {varianza[1]:.2%}")
    print(f"  PC3: {varianza[2]:.2%}")
    print(f"  Total: {sum(varianza):.2%}")

    return df_resultado

#def para que jale al invocarlo
def ejecutar_pca(df: pd.DataFrame) -> pd.DataFrame:
    print("Paso 5 PCA")
    df_resultado = aplicar_pca(df)
    return df_resultado


if __name__ == "__main__":
    from extraccion import extraer_ventas_mysql, extraer_inventario_csv, extraer_perfiles_mongo
    from limpieza import ejecutar_limpieza
    from normalizacion import ejecutar_normalizacion
    from enriquecimiento import ejecutar_enriquecimiento
    from reglas_negocio import ejecutar_reglas_negocio

    df_ventas     = extraer_ventas_mysql()
    df_inventario = extraer_inventario_csv()
    df_perfiles   = extraer_perfiles_mongo()

    # ejecutar pasos anteriores
    limpios        = ejecutar_limpieza(df_ventas, df_inventario)
    normalizados   = ejecutar_normalizacion(limpios["ventas"], limpios["inventario"], df_perfiles)
    df_enriquecido = ejecutar_enriquecimiento(normalizados["ventas"], normalizados["perfiles"])
    df_reglas      = ejecutar_reglas_negocio(df_enriquecido)

    # aplicar pca
    df_final = ejecutar_pca(df_reglas)
