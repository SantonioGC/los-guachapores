import os
import re
import requests
import pandas as pd
import mysql.connector
from pymongo import MongoClient
from bs4 import BeautifulSoup

MYSQL_CONFIG = {
    "host":     "localhost",
    "user":     "root",
    "password": "251105",   #cambien la contra plebes sepa como la tienen
    "database": "retail_db"
}
MONGO_URI  = "mongodb://localhost:27017/"
MONGO_DB   = "retail_db"
MONGO_COL  = "perfiles_usuarios"

#rutas de los archivones ya me canse we
DATA_DIR   = "../data"
CSV_PATH   = os.path.join(DATA_DIR, "inventario.csv")
TXT_PATH   = os.path.join(DATA_DIR, "logs_servidor.txt")
XML_PATH   = os.path.join(DATA_DIR, "catalogos.xml")
XLSX_PATH  = os.path.join(DATA_DIR, "metas_anuales.xlsx")

#API de los tipos de cambio
API_URL    = "https://api.exchangerate-api.com/v4/latest/USD"

#def de extraccion de ventas
def extraer_ventas_mysql() -> pd.DataFrame:
    print(" Conectando a la db del mysql ahuevo -_-")
    conn   = mysql.connector.connect(**MYSQL_CONFIG)
    
    #extraccion
    query  = "SELECT * FROM ventas_historicas ORDER BY id_transaccion;"
    df     = pd.read_sql(query, conn)
    conn.close()
    
    print(f"[mysql] {len(df):} registros de ventas_historicas.")
    return df

#def de extraccion de perfiles del mongo we
def extraer_perfiles_mongo() -> pd.DataFrame:
    print("Conectando a la db de mongo yupii -_-")
    client = MongoClient(MONGO_URI)
    col    = client[MONGO_DB][MONGO_COL]
    
    docs   = list(col.find({}, {"_id": 0}))   # pa excluir _id de mongo
    client.close()
    
    df = pd.json_normalize(docs)
    
    #renombrar columnas de geolocalizacion
    df.rename(columns={
        "geolocalizacion.lat": "lat",
        "geolocalizacion.lon": "lon"
    }, inplace=True)
    
    print(f"[mongodb] {len(df):,} perfiles.")
    return df


#def de extraccion de inventario para num de nulos e duplicados we
def extraer_inventario_csv() -> pd.DataFrame:
    print(f"[csv] leyendo ahora el {CSV_PATH}...")
    df = pd.read_csv(CSV_PATH, encoding="utf-8")
    
    nulos      = df.isnull().sum().sum()
    duplicados = df.duplicated().sum()
    print(f"[csv] {len(df):,} filas | nulos: {nulos} | duplicados: {duplicados}")
    return df


#def de extraccion los logs
def extraer_logs_txt() -> pd.DataFrame:
    print(f"[txt] Parseando {TXT_PATH} con regex")
    
    #Patron regex para el formato apache log
    patron = re.compile(
        r'(?P<ip>\d+\.\d+\.\d+\.\d+)'          # IP
        r' - - \[(?P<timestamp>[^\]]+)\] '       # timestamp
        r'"(?P<metodo>\w+) (?P<endpoint>\S+) '   # método y endpoint
        r'HTTP/\d\.\d" '
        r'(?P<status>\d{3}) '                    # código HTTP
        r'(?P<size>\d+) '                        # tamaño respuesta
        r'(?P<tiempo>\d+\.\d+)s '               # tiempo de respuesta
        r'"(?P<user_agent>[^"]+)"'               # user agent
    )
    
    registros = []
    errores   = 0
    with open(TXT_PATH, "r", encoding="utf-8") as f:
        for linea in f:
            match = patron.search(linea.strip())
            if match:
                registros.append(match.groupdict())
            else:
                errores += 1
    
    df = pd.DataFrame(registros)
    df["status"]  = df["status"].astype(int)
    df["size"]    = df["size"].astype(int)
    df["tiempo"]  = df["tiempo"].astype(float)
    
    print(f"[txt] {len(df):,} lineas parseadas | Errores de formato: {errores}")
    return df


#def de extraccion de los catalogos para la estructura 
def extraer_catalogos_xml() -> pd.DataFrame:
    print(f"[xml] Parseando {XML_PATH}")
    import xml.etree.ElementTree as ET
    
    tree = ET.parse(XML_PATH)
    root = tree.getroot()
    
    registros = []
    for cat in root.findall("categoria"):
        cat_id     = cat.get("id")
        cat_nombre = cat.get("nombre")
        for sub in cat.findall(".//subcategoria"):
            registros.append({
                "cat_id":      cat_id,
                "categoria":   cat_nombre,
                "sub_id":      sub.get("id"),
                "subcategoria": sub.get("nombre")
            })
    
    df = pd.DataFrame(registros)
    print(f"[xml] {len(df):,} subcategorias en {df['categoria'].nunique()} categorias.")
    return df


#def de extraccion de los excel
def extraer_metas_xlsx() -> pd.DataFrame:
    print(f"[xlsx] leyendo ahora {XLSX_PATH}")
    df = pd.read_excel(XLSX_PATH, sheet_name="Metas 2024", engine="openpyxl")
    print(f"[xlsx] {len(df):,} registros | Columnas: {list(df.columns)}")
    return df


#def para extraer monedas de cambio 
def extraer_tipos_cambio(monedas: list = None) -> pd.DataFrame:
    if monedas is None:
        monedas = ["MXN", "EUR", "CAD", "GBP", "JPY", "BRL", "ARS", "COP"]
    
    print(f"[api] Consultando tipos de cambio en {API_URL}")
    try:
        response = requests.get(API_URL, timeout=10)
        response.raise_for_status()
        data   = response.json()
        tasas  = data.get("rates", {})
        
        registros = [
            {"moneda": m, "tasa_respecto_usd": tasas[m]}
            for m in monedas if m in tasas
        ]
        df = pd.DataFrame(registros)
        print(f"[api] {len(df)} tipos de cambio")
        return df
    
    except requests.exceptions.RequestException as e:
        print(f"[api]  Error de conexion: {e}")
        print("[api] Usando tasas de respaldo (hardcoded)")
        fallback = {
            "MXN": 17.15, "EUR": 0.92, "CAD": 1.36,
            "GBP": 0.79,  "JPY": 149.5,"BRL": 4.97,
            "ARS": 823.0, "COP": 3920.0
        }
        df = pd.DataFrame([
            {"moneda": k, "tasa_respecto_usd": v}
            for k, v in fallback.items()
            if k in monedas
        ])
        print(f"[api] {len(df)} tasas de respaldo cargadas padrino")
        return df


#def para simular el scraping de una tabla html con el beautifulSoup
def extraer_precios_scraping() -> pd.DataFrame:
    print("[scraping] Parseando tabla HTML de precios competencia")
    
    #HTML simulado
    html_simulado = """
    <html><body>
    <table id="precios-competencia">
      <thead>
        <tr>
          <th>Producto</th><th>Categoria</th>
          <th>Precio_Competencia</th><th>Moneda</th>
        </tr>
      </thead>
      <tbody>
        <tr><td>Smartphone Pro X</td><td>Electrónica</td><td>12499.00</td><td>MXN</td></tr>
        <tr><td>Laptop UltraSlim</td><td>Electrónica</td><td>22999.00</td><td>MXN</td></tr>
        <tr><td>Televisor 55" 4K</td><td>Electrónica</td><td>9999.00</td><td>MXN</td></tr>
        <tr><td>Audífonos Wireless</td><td>Electrónica</td><td>1899.00</td><td>MXN</td></tr>
        <tr><td>Cámara DSLR</td><td>Electrónica</td><td>15499.00</td><td>MXN</td></tr>
        <tr><td>Tenis Running</td><td>Deportes</td><td>1299.00</td><td>MXN</td></tr>
        <tr><td>Bicicleta MTB</td><td>Deportes</td><td>7800.00</td><td>MXN</td></tr>
        <tr><td>Pesas Ajustables</td><td>Deportes</td><td>2450.00</td><td>MXN</td></tr>
        <tr><td>Playera Deportiva</td><td>Ropa</td><td>349.00</td><td>MXN</td></tr>
        <tr><td>Chamarra Invierno</td><td>Ropa</td><td>1150.00</td><td>MXN</td></tr>
        <tr><td>Jeans Slim Fit</td><td>Ropa</td><td>699.00</td><td>MXN</td></tr>
        <tr><td>Licuadora 1000W</td><td>Hogar</td><td>899.00</td><td>MXN</td></tr>
        <tr><td>Cafetera Espresso</td><td>Hogar</td><td>3299.00</td><td>MXN</td></tr>
        <tr><td>Aspiradora Ciclónica</td><td>Hogar</td><td>2799.00</td><td>MXN</td></tr>
        <tr><td>Set de Maquillaje</td><td>Belleza</td><td>549.00</td><td>MXN</td></tr>
        <tr><td>Perfume 100ml</td><td>Belleza</td><td>1199.00</td><td>MXN</td></tr>
        <tr><td>Crema Facial SPF50</td><td>Belleza</td><td>349.00</td><td>MXN</td></tr>
        <tr><td>Leche Entera 1L</td><td>Alimentos</td><td>28.50</td><td>MXN</td></tr>
        <tr><td>Cereal Integral</td><td>Alimentos</td><td>89.00</td><td>MXN</td></tr>
        <tr><td>Agua Mineral 1.5L</td><td>Alimentos</td><td>18.00</td><td>MXN</td></tr>
        <tr><td>LEGO Creator</td><td>Juguetes</td><td>1499.00</td><td>MXN</td></tr>
        <tr><td>Muñeca Colección</td><td>Juguetes</td><td>599.00</td><td>MXN</td></tr>
        <tr><td>Auto Radio Control</td><td>Juguetes</td><td>799.00</td><td>MXN</td></tr>
        <tr><td>Tablet Infantil</td><td>Juguetes</td><td>2199.00</td><td>MXN</td></tr>
        <tr><td>Rompecabezas 1000pz</td><td>Juguetes</td><td>349.00</td><td>MXN</td></tr>
      </tbody>
    </table>
    </body></html>
    """
    
    soup   = BeautifulSoup(html_simulado, "html.parser")
    tabla  = soup.find("table", {"id": "precios-competencia"})
    
    headers = [th.text.strip() for th in tabla.find("thead").find_all("th")]
    filas   = []
    for tr in tabla.find("tbody").find_all("tr"):
        celdas = [td.text.strip() for td in tr.find_all("td")]
        if celdas:
            filas.append(dict(zip(headers, celdas)))
    
    df = pd.DataFrame(filas)
    df.columns = ["producto", "categoria", "precio_competencia", "moneda"]
    df["precio_competencia"] = df["precio_competencia"].astype(float)
    
    print(f"[scraping] {len(df)} precios de competencia extraidos")
    return df


#def para llamar a todo padrino
def extraer_todo() -> dict:
    print("Paso 1 EXTRACCION")
    
    datos = {}
    
    datos["ventas"]      = extraer_ventas_mysql()
    datos["perfiles"]    = extraer_perfiles_mongo()
    datos["inventario"]  = extraer_inventario_csv()
    datos["logs"]        = extraer_logs_txt()
    datos["catalogos"]   = extraer_catalogos_xml()
    datos["metas"]       = extraer_metas_xlsx()
    datos["tipo_cambio"] = extraer_tipos_cambio()
    datos["competencia"] = extraer_precios_scraping()
    
    print("EXTRACCION COMPLETA")
    for nombre, df in datos.items():
        print(f"  {nombre:<15} -> {len(df):>6,} registros  |  {df.shape[1]} columnas")
    
    return datos

if __name__ == "__main__":
    datos = extraer_todo()
