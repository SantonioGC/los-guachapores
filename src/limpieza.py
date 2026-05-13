import pandas as pd

#def para limpiar y revisar el df tipo ghostbuster aca
def limpiar_inventario(df: pd.DataFrame) -> pd.DataFrame:
    print(f"Filas antes de limpiar: {len(df):,}")

    nulos = df.isnull().sum()
    nulos = nulos[nulos > 0]
    print("Nulos encontrados:")
    for col, n in nulos.items():
        print(f"    - {col}: {n} nulos")

    campos_clave = ["precio_unitario", "stock", "categoria", "marca"]
    antes = len(df)
    df = df.dropna(subset=campos_clave)
    print(f"\nFilas eliminadas por nulos: {antes - len(df)}")

    antes = len(df)
    df = df.drop_duplicates()
    print(f"Filas eliminadas por duplicados: {antes - len(df)}")

    print(f"Filas despues de limpiar: {len(df):,}")
    return df.reset_index(drop=True)

#df lo mismo que de arriba pero ventas del mysql
def limpiar_ventas(df: pd.DataFrame) -> pd.DataFrame:
    print(f"Registros antes de limpiar: {len(df):,}")

    antes = len(df)
    df = df.drop_duplicates()
    print(f"Duplicados eliminados: {antes - len(df)}")

    antes = len(df)
    df = df[df["monto"] > 0]
    print(f"Registros con monto invalido eliminados: {antes - len(df)}")

    print(f"Registros despues de limpiar: {len(df):,}")
    return df.reset_index(drop=True)

#def para que jale al invocarlo
def ejecutar_limpieza(df_ventas: pd.DataFrame, df_inventario: pd.DataFrame) -> dict:
    print("Paso 2 LIMPIEZA")

    ventas_limpias    = limpiar_ventas(df_ventas)
    inventario_limpio = limpiar_inventario(df_inventario)

    return {
        "ventas":     ventas_limpias,
        "inventario": inventario_limpio
    }


if __name__ == "__main__":
    from extraccion import extraer_ventas_mysql, extraer_inventario_csv

    df_ventas     = extraer_ventas_mysql()
    df_inventario = extraer_inventario_csv()

    resultado = ejecutar_limpieza(df_ventas, df_inventario)