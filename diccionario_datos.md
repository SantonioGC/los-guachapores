# Diccionario de datos clave
**Proyecto:** Analisis Global de Retail y Comportamiento del Cliente
**Materia:** Programacion para el Procesamiento de Datos

## Customer_ID
Es el identificador unico de cada cliente. Lo usamos como llave principal para poder unir la información de ventas de mysql con los perfiles de usuario en mongodb sin este campo no podriamos saber que cliente hizo que compra.

- **Campo:** `id_cliente`
- **Tipo:** int
- **Ejemplo:** 873

## Timestamp
Son las fechas registradas en las distintas fuentes, pero el problema es que cada una las guarda en un formato diferente. Por eso necesitamos normalizarlas todas a un mismo formato antes de analizarlas.

- **Formatos que encontramos:**
  - MySQL → `2023-07-15`
  - inventario.csv → `15/07/2023`
  - logs_servidor.txt → `15/Jul/2023:08:32:10`
- **Lo que hacemos:** convertirlas todas a `datetime64` con pandas

## Features numericas
Son variables numericas que vienen de distintas fuentes y tienen escalas muy diferentes entre sí. Esto es un problema para el PCA, porque una variable con valores de hasta 80,000 va a dominar sobre una que va de 0 a 5,000. Por eso aplicamos escalado min-max o z-score para que todas estén en el mismo rango.

- `ingresos` de 5,000 a 80,000 MXN
- `gastos_mensuales` de 200 a 8,000 MXN
- `puntos_lealtad` de 0 a 5,000 puntos
- `monto` de 50 a 5,000 MXN

## Categorias
Son campos de texto que deberían tener un solo valor estándar, pero en los datos aparecen escritos de muchas formas distintas. Si no los limpiamos, el sistema los trata como categorias diferentes y los análisis salen mal.

- **Ejemplo del campo `pais`:** 
  `"México"`, `"mx"`, `"MEX"`, `"Mexico"`, `"MEXICO"` → todos deberían ser `"México"`
- **Lo que hacemos:** estandarizar el texto con `.strip()` y mapeo de valores
