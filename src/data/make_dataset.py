# =========
# Librerias
# =========

import re
import time
from io import BytesIO, StringIO
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

import pandas as pd
import requests
import urllib3

# Debido a que algunos archivos no tienen certificado SSL válido, desactivamos las advertencias de seguridad
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# =============
# Configuración
# =============

def get_project_root():
    """Encontrar el directorio raíz del proyecto buscando el .git"""
    for parent in Path(__file__).resolve().parents:
        if (parent / ".git").exists():
            return parent
    return None

# -- Constantes generales --
PROJ_ROOT = get_project_root()
CARPETA = PROJ_ROOT / 'data/raw/datos_sonora_diario'
RAW_DATA_DIR = PROJ_ROOT / 'data/raw'
INTERIM_DATA_DIR = PROJ_ROOT / 'data/interim'
PROCESSED_DATA_DIR = PROJ_ROOT / 'data/processed'

# -- Constantes para Rickettsia --
URL_RICK = {
    '2022': 'https://datos.sonora.gob.mx/dataset/5494daa1-09ca-4750-aeac-2558553700e1/resource/4121cf57-1e4a-4fb0-b175-3805edffca2c/download/fiebre-manchada-2022.xlsx',
    '2023': 'https://datos.sonora.gob.mx/dataset/5494daa1-09ca-4750-aeac-2558553700e1/resource/30b18862-f126-41ac-b41f-ce7126f3ac9b/download/fiebre-manchada-2023.xlsx',
    '2024': 'https://datos.sonora.gob.mx/dataset/5494daa1-09ca-4750-aeac-2558553700e1/resource/cc6c566f-3088-41cd-b99f-169c5cf6090c/download/fiebre-manchada-2024.xlsx'
}

# -- Constantes de CONAGUA --
PATRON_URL = 'https://smn.conagua.gob.mx/tools/RESOURCES/Normales_Climatologicas/Diarios/son/dia{clave}.txt'
CLAVE_INICIO = 26001
CLAVE_FIN    = 26405
HEADERS = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}

# Patrones para extraer metadatos del encabezado
PATRONES_META = {
    'clave'    : r'ESTACI[OÓ]N\s*:\s*(\S+)',
    'nombre'   : r'NOMBRE\s*:\s*(.+)',
    'estado'   : r'ESTADO\s*:\s*(.+)',
    'municipio': r'MUNICIPIO\s*:\s*(.+)',
    'situacion': r'SITUACI[OÓ\xd3]N\s*:\s*(.+)',
    'latitud'  : r'LATITUD\s*:\s*([\-\d\.]+)',
    'longitud' : r'LONGITUD\s*:\s*([\-\d\.]+)',
    'altitud'  : r'ALTITUD\s*:\s*([\-\d\.]+)',
}


# ==============
# Funciones
# ==============

def lectura_excel(url):
    """Descarga un archivo Excel desde la URL dada y lo carga en un DataFrame de pandas."""
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"
    }
    try:
        response = requests.get(url, headers=headers, timeout=20)
        response.raise_for_status()
        df = pd.read_excel(BytesIO(response.content))
        print(f"Datos cargados exitosamente de: {url.split('/')[-1]}")
        return df
    except requests.exceptions.HTTPError as e:
        print(f"Error HTTP (Código {response.status_code}) en {url}: {e}")
    except requests.exceptions.RequestException as e:
        # Captura errores de red (timeouts, sin internet, rechazos de conexión)
        print(f"Error de conexión al intentar descargar {url}: {e}")
    except ValueError as e:
        # Captura el error si el archivo descargado está corrupto o no es un Excel
        print(f"Error procesando el archivo Excel (posible formato incorrecto): {e}")
    return None


def get_rickettsia_data(urls: dict[str, str]) -> pd.DataFrame | None:
    """Descarga y procesa los datasets de rickettsia de Sonora con sistema de reintentos."""
    dfs_rick = []
    max_reintentos = 4
    
    for year, url in urls.items():
        df = None # Reiniciamos la variable para cada año
        
        # --- BUCLE DE REINTENTOS ---
        for intento in range(max_reintentos):
            print(f"\r⏳ Descargando {year}... (Intento {intento + 1}/{max_reintentos})", end="", flush=True)
            df = lectura_excel(url)
            
            if df is not None:
                print(f"\n✅ ¡Descarga exitosa para {year}!")
                break  # El archivo se descargó, salimos del bucle de reintentos
            else:
                if intento < max_reintentos - 1:
                    # Hacemos una pausa de 2 segundos antes del próximo intento
                    time.sleep(2) 
        
        # --- PROCESAMIENTO ---
        # Si después de los 4 intentos logramos tener el DataFrame, lo procesamos
        if df is not None:
            df = normalizar_fechas(df)  # Recuerda reasignar la variable
            df.to_csv(RAW_DATA_DIR / f"rick_{year}.csv", index=False, encoding='utf-8-sig')
            dfs_rick.append(df)
        else:
            print(f"\n❌ Se agotaron los {max_reintentos} intentos. Omitiendo año {year}.")

    # --- CONCATENACIÓN FINAL ---
    if dfs_rick:
        return pd.concat(dfs_rick, ignore_index=True)
    return None


def normalizar_fechas(df):
    """Convierte a formato datetime todas las columnas que parezcan contener fechas."""
    cols_fecha = [col for col in df.columns if col.startswith(('fec_', 'fecha'))]
    for col in cols_fecha:
        df[col] = pd.to_datetime(
            df[col].astype(str).str.split(' ').str[0],
            errors='coerce'
        )
    return df


def procesar_clave(clave, sesion):
    """Función de trabajo para cada hilo"""
    nombre_archivo = f'dia{clave}.txt'
    ruta_local     = CARPETA / nombre_archivo
    url            = PATRON_URL.format(clave=clave)

    if ruta_local.exists():
        return ('omitidos', clave)

    try:
        r = sesion.get(url, headers=HEADERS, verify=False, timeout=20)
        
        if r.status_code == 200:
            ruta_local.write_bytes(r.content)
            return ('descargados', clave)
        elif r.status_code == 404:
            return ('no_existen', clave)
        else:
            return ('errores', {'clave': clave, 'status': r.status_code})

    except requests.RequestException as e:
        return ('errores', {'clave': clave, 'status': str(e)})


def parsear_estacion(ruta: Path) -> pd.DataFrame | None:
    """
    Lee un TXT del SMN y devuelve un DataFrame con columnas:
    clave, nombre, estado, municipio, situacion,
    latitud, longitud, altitud, fecha, precip, evap, tmax, tmin
    """
    try:
        contenido = ruta.read_text(encoding='utf-8')
        lineas    = contenido.splitlines()

        #Extraer metadatos
        meta = {k: None for k in PATRONES_META}
        meta['clave'] = ruta.stem.replace('dia', '')   # fallback desde nombre de archivo

        datos_inicio = None
        for i, linea in enumerate(lineas):
            # Buscar metadatos
            for campo, patron in PATRONES_META.items():
                m = re.search(patron, linea, re.IGNORECASE)
                if m:
                    meta[campo] = m.group(1).strip()

            # Detectar primera línea de datos: empieza con YYYY-MM-DD
            if re.match(r'^\d{4}-\d{2}-\d{2}', linea.strip()):
                datos_inicio = i
                break

        if datos_inicio is None:
            return None   # archivo sin datos

        # Convertir lat/lon/alt a float
        for campo in ('latitud', 'longitud', 'altitud'):
            try:
                meta[campo] = float(meta[campo]) if meta[campo] else None
            except (ValueError, TypeError):
                meta[campo] = None

        #Leer bloque de datos
        # El archivo tiene dos líneas de cabecera antes de los datos:
        #   FECHA  PRECIP  EVAP  TMAX  TMIN
        #          (mm)    (mm)  (°C)  (°C)    ← esta línea la saltamos
        # Para evitar problemas, leemos solo las líneas que empiecen con fecha
        lineas_datos = [
            l for l in lineas[datos_inicio:]
            if re.match(r'^\d{4}-\d{2}-\d{2}', l.strip())
        ]

        df = pd.read_csv(
            StringIO('\n'.join(lineas_datos)),
            sep       = r'\t',
            header    = None,
            names     = ['fecha', 'precip', 'evap', 'tmax', 'tmin'],
            engine    = 'python',
            na_values = ['NULO', 'nulo', '', ' ', '-'],
        )

        # Convertir tipos
        df['fecha'] = pd.to_datetime(df['fecha'], errors='coerce')
        for col in ['precip', 'evap', 'tmax', 'tmin']:
            df[col] = pd.to_numeric(df[col], errors='coerce')

        #Agregar metadatos como columnas
        for campo in ['clave', 'nombre', 'estado', 'municipio',
                      'situacion', 'latitud', 'longitud', 'altitud']:
            df.insert(df.columns.get_loc('fecha'), campo, meta[campo])

        return df

    except Exception as e:
        print(f'{ruta.name}: {e}')
        return None


# =================================
# Descarga y procesamiento de datos
# =================================

RAW_DATA_DIR.mkdir(parents=True, exist_ok=True)
INTERIM_DATA_DIR.mkdir(parents=True, exist_ok=True)
PROCESSED_DATA_DIR.mkdir(parents=True, exist_ok=True)
CARPETA.mkdir(parents=True, exist_ok=True)

# -- Descarga de datasets de Rickettisas Sonora --
rick = get_rickettsia_data(URL_RICK)

# -- Descarga de dataset CONAGUA --
# Variables de conteo (se actualizarán conforme terminen los hilos)
resultados = {
    'descargados': [],
    'omitidos': [],
    'no_existen': [],
    'errores': []
}

print(f'Carpeta de salida : {CARPETA.resolve().relative_to(PROJ_ROOT)}')
claves = range(CLAVE_INICIO, CLAVE_FIN + 1)
total = len(claves)
procesados = 0

# requests.Session() para reutilizar las conexiones TCP
with requests.Session() as sesion:
    # max_workers para balance con el servidor
    with ThreadPoolExecutor(max_workers=5) as executor:
        futuros = {executor.submit(procesar_clave, clave, sesion): clave for clave in claves}
        
        for futuro in as_completed(futuros):
            procesados += 1
            categoria, dato = futuro.result()
            
            if categoria == 'errores':
                resultados[categoria].append(dato)
            else:
                resultados[categoria].append(dato)

            # Imprimir progreso cada 50 o al final
            print(f'\r ⏳ Descargando: {procesados}/{total} | Éxito: {len(resultados["descargados"])} | Vacíos: {len(resultados["no_existen"])} | Errores: {len(resultados["errores"])}', end='', flush=True)
            # if procesados % 50 == 0 or procesados == total:
                #print(f'  {procesados}/{total} — descargados: {len(resultados["descargados"])}, sin archivo: {len(resultados["no_existen"])}, errores: {len(resultados["errores"])}')
        print()  # Nueva línea al finalizar
print(f'\nDescargados  : {len(resultados["descargados"])}')
print(f'Ya existían  : {len(resultados["omitidos"])}')
print(f'Sin archivo  : {len(resultados["no_existen"])}')
print(f'Errores      : {len(resultados["errores"])}')

if resultados["errores"]:
    print('\nDetalle de errores:')
    for e in resultados["errores"]:
        print(f"  clave {e['clave']}: {e['status']}")

# -- Procesamiento de datos CONAGUA --
# Procesar todos los archivos 
archivos = sorted(CARPETA.glob('dia*.txt'))
total    = len(archivos)
print(f'Archivos a parsear: {len(archivos)}')

dfs = []
for i, ruta in enumerate(archivos, 1):
    df = parsear_estacion(ruta)
    if df is not None:
        dfs.append(df)

    if i % 50 == 0 or i == total:
        print(f'  {i}/{total} archivos parseados...')

df_total = pd.concat(dfs, ignore_index=True)
print(f'\n DataFrame final: {df_total.shape[0]:,} filas × {df_total.shape[1]} columnas')

# --Concatenación de datos de estaciones --
df_meta = (
    df_total
    .drop_duplicates(subset='clave')
    [['clave', 'nombre', 'municipio', 'situacion', 'latitud', 'longitud', 'altitud']]
    .reset_index(drop=True)
)

print(f'Estaciones parseadas  : {len(df_meta)}')
print(f'Sin latitud           : {df_meta["latitud"].isna().sum()}')
print(f'Sin longitud          : {df_meta["longitud"].isna().sum()}')
print(f'Sin municipio         : {df_meta["municipio"].isna().sum()}')

# ===================
# Exportación de Datos
# ===================

# Casos de Rickettsia en Sonora de 2022 a 2024
rick.to_csv( INTERIM_DATA_DIR / 'rick_hist.csv', index=False)
# Normales climatológicas diarias de Sonora
df_total.to_csv(INTERIM_DATA_DIR / 'clima_diario.csv', index=False, encoding='utf-8-sig')
# Catálogo de estaciones climatológicas
df_meta.to_csv(INTERIM_DATA_DIR / 'catalogo_estaciones.csv', index=False, encoding='utf-8-sig')