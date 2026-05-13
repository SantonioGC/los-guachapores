import pandas as pd

#def para hacer el left join aca tipo espejo 
def enriquecer_ventas(df_ventas: pd.DataFrame, df_perfiles: pd.DataFrame) -> pd.DataFrame:
    #left join entre ventas y perfiles usando id_cliente
    df = df_ventas.merge(df_perfiles, on="id_cliente", how="left")
    print(f"Registros tras el join: {len(df):,}")
    print(f"Columnas resultantes: {list(df.columns)}")
    return df

#def para que jale cuando se invoque
def ejecutar_enriquecimiento(df_ventas: pd.DataFrame, df_perfiles: pd.DataFrame) -> pd.DataFrame:
    print("Paso 4 ENRIQUECIMIENTO")
    df_enriquecido = enriquecer_ventas(df_ventas, df_perfiles)
    return df_enriquecido


if __name__ == "__main__":
    from extraccion import extraer_ventas_mysql, extraer_inventario_csv, extraer_perfiles_mongo
    from limpieza import ejecutar_limpieza
    from normalizacion import ejecutar_normalizacion

    df_ventas     = extraer_ventas_mysql()
    df_inventario = extraer_inventario_csv()
    df_perfiles   = extraer_perfiles_mongo()

    #para ejecutar los def 
    limpios        = ejecutar_limpieza(df_ventas, df_inventario)
    normalizados   = ejecutar_normalizacion(limpios["ventas"], limpios["inventario"], df_perfiles)
    df_enriquecido = ejecutar_enriquecimiento(normalizados["ventas"], normalizados["perfiles"])
