from extraccion import extraer_todo
from limpieza import ejecutar_limpieza
from normalizacion import ejecutar_normalizacion
from enriquecimiento import ejecutar_enriquecimiento
from reglas_negocio import ejecutar_reglas_negocio
from pca import ejecutar_pca

#def para llamar todo paso a paso
def main():
    #paso 1 extraer todas las fuentes
    datos = extraer_todo()

    #paso 2 limpiar ventas e inventario
    limpios = ejecutar_limpieza(datos["ventas"], datos["inventario"])

    #paso 3 normalizar fechas y escalar variables
    normalizados = ejecutar_normalizacion(limpios["ventas"], limpios["inventario"], datos["perfiles"])

    #paso 4 left join entre ventas y perfiles
    df_enriquecido = ejecutar_enriquecimiento(normalizados["ventas"], normalizados["perfiles"])

    #paso 5 crear columna segmento_cliente con reglas de negocio
    df_reglas = ejecutar_reglas_negocio(df_enriquecido)

    #paso 6 reduccion de dimensionalidad con pca
    df_final = ejecutar_pca(df_reglas)

    #guardar resultado final
    df_final.to_csv("output/data_final.csv", index=False)
    df_final.to_parquet("output/data_final.parquet", index=False)
    print("Archivo final guardado en output/")


if __name__ == "__main__":
    main()
