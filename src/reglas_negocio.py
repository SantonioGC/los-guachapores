import numpy as np
import pandas as pd

def aplicar_segmento_cliente(df: pd.DataFrame) -> pd.DataFrame:
    #crear columna segmento_cliente con np.where segun gasto y edad
    df["segmento_cliente"] = np.where(
        (df["gastos_mensuales"] > 0.5) & (df["edad"] < 30), "Premium Joven",
        np.where(
            (df["gastos_mensuales"] > 0.5) & (df["edad"] >= 30), "Premium Adulto",
            np.where(
                (df["gastos_mensuales"] <= 0.5) & (df["edad"] < 30), "Regular Joven",
                "Regular Adulto"
            )
        )
    )
    print(f"Segmentos generados:")
    print(df["segmento_cliente"].value_counts().to_string())
    return df

#def para que jale al invocarlo
def ejecutar_reglas_negocio(df: pd.DataFrame) -> pd.DataFrame:
    print("Paso 5 REGLAS DE NEGOCIO")
    df = aplicar_segmento_cliente(df)
    return df


if __name__ == "__main__":
    from extraccion import extraer_ventas_mysql, extraer_inventario_csv, extraer_perfiles_mongo
    from limpieza import ejecutar_limpieza
    from normalizacion import ejecutar_normalizacion
    from enriquecimiento import ejecutar_enriquecimiento

    df_ventas     = extraer_ventas_mysql()
    df_inventario = extraer_inventario_csv()
    df_perfiles   = extraer_perfiles_mongo()

    #ejecutar 
    limpios        = ejecutar_limpieza(df_ventas, df_inventario)
    normalizados   = ejecutar_normalizacion(limpios["ventas"], limpios["inventario"], df_perfiles)
    df_enriquecido = ejecutar_enriquecimiento(normalizados["ventas"], normalizados["perfiles"])

    #aplicar reglas de negocio
    df_final = ejecutar_reglas_negocio(df_enriquecido)
