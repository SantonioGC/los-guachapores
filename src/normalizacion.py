import pandas as pd
from sklearn.preprocessing import MinMaxScaler

#def para normalizar fechas a datetime64
def normalizar_fechas(df_ventas: pd.DataFrame, df_inventario: pd.DataFrame) -> dict:
    print("Normalizando fechas")

    #en ventas fecha viene como YYYY-MM-DD de mysql
    df_ventas["fecha"] = pd.to_datetime(df_ventas["fecha"])
    print(f"  ventas fecha: {df_ventas['fecha'].dtype}")

    #en inventario fecha viene como DD/MM/YYYY del csv
    df_inventario["fecha_entrada"] = pd.to_datetime(df_inventario["fecha_entrada"], dayfirst=True)
    print(f"  inventario fecha_entrada: {df_inventario['fecha_entrada'].dtype}")

    return {
        "ventas":     df_ventas,
        "inventario": df_inventario
    }


#def para escalar variables con min-max
def escalar_numericas(df_perfiles: pd.DataFrame) -> pd.DataFrame:
    print("Escalando variables con Min-Max")

    columnas = ["ingresos", "puntos_lealtad", "gastos_mensuales"]
    scaler   = MinMaxScaler()

    df_perfiles[columnas] = scaler.fit_transform(df_perfiles[columnas])
    print(f"columnas escaladas: {columnas}")

    return df_perfiles

#def para que jale al invocarlo
def ejecutar_normalizacion(df_ventas: pd.DataFrame, df_inventario: pd.DataFrame, df_perfiles: pd.DataFrame) -> dict:
    print("Paso 3 NORMALIZACION")

    resultado_fechas = normalizar_fechas(df_ventas, df_inventario)
    df_perfiles      = escalar_numericas(df_perfiles)

    return {
        "ventas":     resultado_fechas["ventas"],
        "inventario": resultado_fechas["inventario"],
        "perfiles":   df_perfiles
    }


if __name__ == "__main__":
    from extraccion import extraer_ventas_mysql, extraer_inventario_csv, extraer_perfiles_mongo
    from limpieza   import ejecutar_limpieza

    df_ventas     = extraer_ventas_mysql()
    df_inventario = extraer_inventario_csv()
    df_perfiles   = extraer_perfiles_mongo()

    limpios  = ejecutar_limpieza(df_ventas, df_inventario)
    resultado = ejecutar_normalizacion(limpios["ventas"], limpios["inventario"], df_perfiles)
