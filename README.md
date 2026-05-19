# Analisis retail y comportamiento del cliente
**Materia:** Programacion para el procesamiento de datos

Pipeline ETL que integra fuentes de datos para centralizar informacion de retail y generar analisis estadístico con visualizaciones.

---

## Requisitos

- Python
- MySQL con MySQL workbench
- MongoDB con MongoDB compass
- Jupyter notebook

---

## Instalacion

**1. Clona el repositorio**
```bash
git clone https://github.com/SantonioGC/los-guachapores.git
cd los-guachapores
```

**2. Instala las dependencias**
```bash
pip install -r requirements.txt
```

---

## Configuración de bases de datos

**MySQL**
1. Abre MySQL Workbench
2. Ve a `File -> Open SQL Script`
3. Selecciona `db/ventas_historicas.sql`
4. Ejecuta el script
5. Verifica con:
```sql
SELECT COUNT(*) FROM retail_db.ventas_historicas;
-- tiene que salir 7500
```

**MongoDB**
1. Abre MongoDB compass y conectate a `mongodb://localhost:27017`
2. Crea la base de datos `retail_db` con la coleccion `perfiles_usuarios`
3. Entra a la coleccion → `ADD DATA → Import JSON or CSV file`
4. Selecciona `db/perfiles_usuarios.json` e importa
5. Verifica que aparezcan 1,500 documentos

---

## Configuracion

En `src/extraccion.py` cambia la contraseña de MySQL:
```python
MYSQL_CONFIG = {
    "host":     "localhost",
    "user":     "root",
    "password": "tu_password",  # ← cambia esto
    "database": "retail_db"
}
```

---

## Estructura del proyecto

```
proyecto/
├── data/
│   ├── inventario.csv
│   ├── logs_servidor.txt
│   ├── catalogos.xml
│   └── metas_anuales.xlsx
├── db/
│   ├── ventas_historicas.sql
│   └── perfiles_usuarios.json
├── src/
│   ├── extraccion.py
│   ├── limpieza.py
│   ├── normalizacion.py
│   ├── enriquecimiento.py
│   ├── reglas_negocio.py
│   ├── pca.py
│   ├── main.py
│   └── visualizaciones.ipynb
├── output/
├── diccionario_datos.md
└── requirements.txt
```

---

## Ejecucion

**Opcion 1 — ejecutar el pipeline completo**
```bash
cd src
python main.py
```
El archivo final se guarda en `output/data_final.csv`

**Opcion 2 — Ver las visualizaciones**
```bash
jupyter notebook src/visualizaciones.ipynb
```
Corre las celdas de arriba hacia abajo y las gráficas aparecen directo en el notebook.

---

## Equipo — Los Guachapores

| Nombre | 
|---|
| Jesus Arturo Carrillo Avilez |
| Sergio Antonio Gomez Cazares |
| Carlos Alberto Romero Corral |
| Santiago Jassiel Tapia Valdez |
