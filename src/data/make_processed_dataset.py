"""
make_processed_dataset.py

Lee rick_hist.csv (data/interim) y produce rick_eda_imput.csv aplicando:
  1. Imputación de valores faltantes con indicadores de imputación
  2. Feature engineering (variables de tiempo, compromiso de órganos, tipos de datos)
  3. Corrección de fechas con errores de captura

Uso:
    uv run python src/data/make_processed_dataset.py
"""

import numpy as np
import pandas as pd
from pathlib import Path
from scipy import stats


# =============================================================================
# Rutas
# =============================================================================

def _get_project_root() -> Path:
    for parent in Path(__file__).resolve().parents:
        if (parent / '.git').exists():
            return parent
    raise FileNotFoundError('No se encontró el directorio raíz del proyecto (.git)')


PROJ_ROOT   = _get_project_root()
INTERIM_DIR = PROJ_ROOT / 'data' / 'interim'
PROCESSED_DIR = PROJ_ROOT / 'data' / 'processed'
INPUT_FILE  = INTERIM_DIR / 'rick_hist.csv'
OUTPUT_FILE = PROCESSED_DIR / 'rick_eda_imput.csv'


# =============================================================================
# Mapas de estandarización de texto libre
# =============================================================================

_MAPA_CONTACTO_OTR = {
    # ── Sin contacto / negado ─────────────────────────────────────────────────
    'NEGADO':               'Sin contacto',
    'NEGATIVO':             'Sin contacto',
    'NO':                   'Sin contacto',
    'NIEGA PRESENCIA':      'Sin contacto',
    'NO HA VISTO':          'Sin contacto',
    'SE IGNORA':            'Sin contacto',
    'PACIENTESEDADO':       'Sin contacto',

    # ── Solo perros ───────────────────────────────────────────────────────────
    'PERRO':                'Perros',
    'PERRO ,':              'Perros',
    'CAN':                  'Perros',
    'CANES':                'Perros',
    'PERROS':               'Perros',
    '2 PERROS':             'Perros',
    '3 PERROS':             'Perros',
    '6 PERROS':             'Perros',
    '8 PERROS':             'Perros',
    '20 PERROS':            'Perros',
    'PERROS 9':             'Perros',
    'CUENTA CON 2 PERROS':  'Perros',
    'TIENE PERROS SU CASO': 'Perros',
    'PERROS EN SU CASA':    'Perros',
    'PERROS CALLEJEROS':    'Perros',

    # ── Perros con ectoparásitos ──────────────────────────────────────────────
    'PERRO PARASITADO':     'Perros con ectoparásitos',
    'PERRO  ECTOPARASITOS': 'Perros con ectoparásitos',
    'PERRO ECTOPARASITOS':  'Perros con ectoparásitos',
    'PERRO CON ECTOPARASI': 'Perros con ectoparásitos',
    'PERRO CON EXTOPARASI': 'Perros con ectoparásitos',
    'PERRO + ECTOPARASITO': 'Perros con ectoparásitos',
    'PERROS + ECTOPARASIT': 'Perros con ectoparásitos',
    'PERROS CON ECTOPARAS': 'Perros con ectoparásitos',
    'PERROS ECTOPARASITOS': 'Perros con ectoparásitos',
    '3 PERROS ECTOPARASIT': 'Perros con ectoparásitos',
    'PERRO C/ ECTOPARASIT': 'Perros con ectoparásitos',

    # ── Perros con garrapatas ─────────────────────────────────────────────────
    'PERROS CON GARRAPATA': 'Perros con garrapatas',
    'PERRO CON GARRAPATAS': 'Perros con garrapatas',
    'PERRO CON RICKETSIA':  'Perros con garrapatas',
    'PERROCON GARRAPATAS':  'Perros con garrapatas',
    'PERROS + GARRAPATAS':  'Perros con garrapatas',
    'PERROVECINOGARRAPATA': 'Perros con garrapatas',
    'CASA/PERRO GARRAPATA': 'Perros con garrapatas',

    # ── Perros y gatos ────────────────────────────────────────────────────────
    'PERRO Y GATO':         'Perros y gatos',
    'PERRO , GATO':         'Perros y gatos',
    'PERRO/GATOS':          'Perros y gatos',
    'PERRO Y GATOS':        'Perros y gatos',
    'GATOS Y PERROS':       'Perros y gatos',
    'PERROS Y GATOS':       'Perros y gatos',
    '5 PERROS Y 13 GATOS':  'Perros y gatos',
    'COCHIS,PERROS Y GATO': 'Perros y gatos',

    # ── Solo gatos ────────────────────────────────────────────────────────────
    'GATO':                 'Gatos',
    'GATOS':                'Gatos',

    # ── Roedores ─────────────────────────────────────────────────────────────
    'RATONES':              'Roedores',
    'RATAS':                'Roedores',
    'ROEDORES':             'Roedores',

    # ── Otros animales ────────────────────────────────────────────────────────
    'CONEJOS':              'Conejos',
    'PERROS CABALLOS':      'Perros y caballos',
    'TIENE MASCOTAS':       'Otros animales',

    # ── Garrapatas / insectos (sin animal específico) ─────────────────────────
    'PLAGA DE GARRAPATAS':  'Garrapatas',
    'GARRAPATA EN CASA':    'Garrapatas',
    'SE RETIRO GARRAPATA':  'Garrapatas',
    'PULGAS':               'Pulgas',
    'ARAÑAS':               'Arañas',
    'PICADURA DE INSECTO':  'Insectos no especificados',
    'NATURALEZA E INSECTO': 'Insectos no especificados',

    # ── Zoonosis ──────────────────────────────────────────────────────────────
    'ZOONOSIS':             'Zoonosis',
    'ZOONOSIS POSITIVA':    'Zoonosis',

    # ── Exposición ambiental ──────────────────────────────────────────────────
    'INTRADOMICILIARIO':    'Exposición ambiental',
    'DUERME EN EL PISO':    'Exposición ambiental',
}

_MAPA_OTR_SERV_ATENCION = {
    # ── Epidemiología ─────────────────────────────────────────────────────────
    'EPIDEMIOLOGIA':                          'Epidemiologia',
    'EPIDEMIOLOGÍA':                          'Epidemiologia',
    'EPIDEMILOGIA':                           'Epidemiologia',
    'EPIDEMIOLGIA':                           'Epidemiologia',
    'EPIEDEMIOLOGIA':                         'Epidemiologia',
    'EPIDEMIPOLOGIA':                         'Epidemiologia',
    'PIDEMIOLOGIA':                           'Epidemiologia',
    'EPIDEMIOLOGICA':                         'Epidemiologia',
    'EPIDEMIOLOGICO':                         'Epidemiologia',
    'EPIDEMIOLOGO':                           'Epidemiologia',
    'DEPTO. EPIDEMIOLOGIA':                   'Epidemiologia',
    'SERVICIO EPIDEMIOLOGIA':                 'Epidemiologia',
    'CONSULTA EPIDEMIOLOGIA':                 'Epidemiologia',
    'CONSULTA EPIDEMIOLOGÍA':                 'Epidemiologia',
    'CONUSLTA EPIDEMIOLOGIA':                 'Epidemiologia',
    'EPIDEMIOLOGIA CLINICA':                  'Epidemiologia',
    'EPIDEMIOLOGIA UMF NO.1':                 'Epidemiologia',
    'EPIDEMIOLOGIA COORDINACION HUATABAMPO':  'Epidemiologia',
    'EPI':                                    'Epidemiologia',

    # ── Epidemiología + consulta externa ─────────────────────────────────────
    'EPIDEMIOLOGIA/MEDICINA FAMILIAR':        'Epidemiologia y consulta externa',
    'EPIDEMIOLOGIA CONSULTA EXTERNA':         'Epidemiologia y consulta externa',
    'CONSULTA EXTERNA EPIDEMIOLOGIA':         'Epidemiologia y consulta externa',
    'CONSULTA EXTERNA EPIDEMIOLOGÍA':         'Epidemiologia y consulta externa',

    # ── Consulta externa ──────────────────────────────────────────────────────
    'CONSULTA EXTERNA':                       'Consulta externa',
    'CONSULTA  EXTERNA':                      'Consulta externa',
    'CONSULTA EXTERA':                        'Consulta externa',
    'CONSULTA EXTERNA GENERAL':               'Consulta externa',
    'CONSULTA EXTERNA MG':                    'Consulta externa',
    'CONSULTA':                               'Consulta externa',

    # ── Medicina familiar ─────────────────────────────────────────────────────
    'MEDICINA FAMILIAR':                      'Medicina familiar',
    'MEDICINA FAMILAIR':                      'Medicina familiar',
    'MEDICO FAMILIAR':                        'Medicina familiar',
    'MEDIFICNA FAMILIAR':                     'Medicina familiar',
    'MF':                                     'Medicina familiar',
    'UMF 68':                                 'Medicina familiar',
    'CONSULTA EXTERNA FAMILIAR':              'Medicina familiar',
    'CONSULTA EXTERNA MEDICO FAMILIAR':       'Medicina familiar',
    'CONSULTA EXTERNA DE MEDICINA FAMILIAR':  'Medicina familiar',
    'CONSULTA MEDICINA FAMILIAR':             'Medicina familiar',

    # ── Medicina general ──────────────────────────────────────────────────────
    'MEDICINA GENERAL':                       'Medicina general',
    'MEDICO GENERAL':                         'Medicina general',
    'MEH':                                    'Medicina general',

    # ── Medicina preventiva ───────────────────────────────────────────────────
    'MEDICINA PREVENTIVA':                    'Medicina preventiva',
    'MEDCINA PREVENTIVA':                     'Medicina preventiva',

    # ── Infectología ──────────────────────────────────────────────────────────
    'INFECTOLOGIA':                           'Infectologia',
    'INFECTOLOGIA CAMA 209':                  'Infectologia',

    # ── Urgencias pediátricas ─────────────────────────────────────────────────
    'URGENCIAS PEDIATRICAS':                  'Urgencias pediatricas',
    'URGENCIAS PEDIÁTRICAS':                  'Urgencias pediatricas',
    'URG PEDIATRICAS':                        'Urgencias pediatricas',

    # ── Cuidados intensivos ───────────────────────────────────────────────────
    'UNIDAD DE CUIDADOS INTENSIVOS PEDIATRICOS': 'UCI pediatrica',

    # ── Brigada epidemiológica ────────────────────────────────────────────────
    'BRIGADA EPIDEMIOLOGICA':                 'Brigada epidemiologica',
    'BRIGADA EPIDEMIOLÓGICA DS5':             'Brigada epidemiologica',
    'BRIGADIA EPIDEMIOLOGIA':                 'Brigada epidemiologica',
    'BRIGADA DE SALUD EPIDEMIOLOGIA':         'Brigada epidemiologica',
    'BRIGADA DE SALUD EPIDEMIOLOGICA':        'Brigada epidemiologica',
    'BRIGADA DE SALUD':                       'Brigada epidemiologica',
    'BRIGADISTA DE SALUD':                    'Brigada epidemiologica',
    'BRIGADA':                                'Brigada epidemiologica',

    # ── Consulta privada / farmacia ───────────────────────────────────────────
    'MEDICO PARTICULAR':                      'Consulta privada',
    'CONSULTORIO PRIVADO':                    'Consulta privada',
    'FARMACIA':                               'Consulta en farmacia',
    'CONSULTORIO FARMACIA DEL AHORRO':        'Consulta en farmacia',
    'CONSULTA EN FARMACIA PARTICULAR':        'Consulta en farmacia',
    'ATENCION MEDICA EN FARMACIA BENAVIDES':  'Consulta en farmacia',
    'CONSULTORIO DE FARMACIA SIMILAR SANTA CLARA 1 COL VILLAS DEL SUR': 'Consulta en farmacia',

    # ── Hospital privado ──────────────────────────────────────────────────────
    'HOSPITAL SAN JOSÉ GUAYMAS':              'Hospital privado',
    'HOSPITAL SAN JOSE GUAYMAS':              'Hospital privado',

    # ── Atención continua ─────────────────────────────────────────────────────
    'ATENCION MEDICA CONTINUA':               'Atencion continua',
    'ATENCION CONTINUA':                      'Atencion continua',

    # ── SEMEFO ────────────────────────────────────────────────────────────────
    'SEMEFO':                                 'SEMEFO',

    # ── Sin atención médica ───────────────────────────────────────────────────
    'SIN ATENCION MEDICA':                    'Sin atencion medica',
}

_SIN_COMPROMISO = {
    'NO', 'NO POR EL MOMENTO', 'NINGUNO APARENTE', 'NINGUNO',
    'NEGATIVO', 'NEGADOS', 'NEGAGO', '2',
}

_CON_COMPROMISO = {
    'PULMONAR', 'FALLA MULTIORGANICA', 'RIÑON', 'INSUFICIENCIA RENAL AGUDA',
    'FALLA RENAL', 'HEMATOMA EPIDURAL', 'PACIENTE GRAVE', 'HEPATICA Y RENAL',
    'RENAL', 'FALLA ORGANICA MULTIPLE', 'ESTADO DE CHOQUE',
    'ESTETATOSIS HEPATICA GRADO 1', 'INSUFICIENCIA RENAL', 'EL CEREBRO',
    'RENAL, HEPATICO', 'LRA', 'DEL SISTEMA NERVIOSO',
    'HECES FECALES CON SANGRE', 'MO', 'LESION RENAL AGUDA',
    'RENAL Y RESPIRATORIO', '1 FALLA RENAL', 'INSUFICIENCIA HEPATICA',
    'ETV', 'FALLA HEMATOLOGICA, RENAL Y HEPATICA', 'ERITEMA',
    'SI', '1',
}


# =============================================================================
# Funciones auxiliares
# =============================================================================

def _clasificar_compromiso(valor) -> int:
    """Devuelve 1=Sí, 2=No, 0=Ambiguo/desconocido."""
    if pd.isna(valor):
        return 0
    valor = str(valor).strip().upper()
    if valor in _SIN_COMPROMISO:
        return 2
    if valor in _CON_COMPROMISO:
        return 1
    return 0


def _convertir_fechas(rick: pd.DataFrame) -> pd.DataFrame:
    cols_fecha = [col for col in rick.columns if col.startswith(('fec_', 'fecha'))]
    for col in cols_fecha:
        rick[col] = pd.to_datetime(rick[col], errors='coerce')
    return rick


def _calcular_tiempos(rick: pd.DataFrame) -> pd.DataFrame:
    """Recalcula todas las variables de tiempo derivadas de fechas."""
    rick['tiempo_res_hosp'] = (rick['fec_ini_estudio'] - rick['fec_sol_aten']).dt.days
    rick['dias_estudio'] = (rick['fec_fin_estudio'] - rick['fec_ini_estudio']).dt.days
    rick['demora_pac'] = (rick['fec_sol_aten'] - rick['fec_ini_signos_sint']).dt.days
    rick['demora_pac_fiebre'] = (rick['fec_sol_aten'] - rick['fec_ini_fiebre']).dt.days
    rick['demora_pac_signos_alarma'] = (rick['fec_sol_aten'] - rick['fec_ini_signos_alarma']).dt.days
    return rick


# =============================================================================
# Pasos del pipeline
# =============================================================================

def imputar(rick: pd.DataFrame) -> pd.DataFrame:
    """Imputa valores faltantes y crea columnas indicadoras de imputación."""

    # des_cual_lengua — nulos → 'Otro'
    rick['des_cual_lengua_imput'] = rick['des_cual_lengua'].isnull().astype('category')
    rick['des_cual_lengua'] = rick['des_cual_lengua'].fillna('Otro')

    # es_indigena — código 9 es error de captura; se corrige a 2 (No indígena)
    rick.loc[rick['es_indigena'] == 9, 'es_indigena'] = 2

    # otros_especifique — nulos → 'No'
    rick['otros_especifique_imput'] = rick['otros_especifique'].isnull().astype('category')
    rick['otros_especifique'] = rick['otros_especifique'].fillna('No')

    # contacto_otr — estandarizar texto libre, luego nulos → 'Sin contacto'
    rick['contacto_otr'] = rick['contacto_otr'].map(_MAPA_CONTACTO_OTR)
    rick['contacto_otr_imput'] = rick['contacto_otr'].isnull().astype('category')
    rick['contacto_otr'] = rick['contacto_otr'].fillna('Sin contacto')

    # otro_sintoma — nulos → 'NO', 'NINGUNO' → 'NO'
    rick['otro_sintoma_imput'] = rick['otro_sintoma'].isnull().astype('category')
    rick['otro_sintoma'] = rick['otro_sintoma'].fillna('NO')
    rick['otro_sintoma'] = rick['otro_sintoma'].str.replace('NINGUNO', 'NO', regex=False)

    # otr_serv_atencion — estandarizar texto libre, luego nulos → 'Se ignora'
    rick['otr_serv_atencion'] = rick['otr_serv_atencion'].map(_MAPA_OTR_SERV_ATENCION)
    rick['otr_serv_atencion_imput'] = rick['otr_serv_atencion'].isna().astype('category')
    rick['otr_serv_atencion'] = rick['otr_serv_atencion'].fillna('Se ignora')

    # temperatura — eliminar outliers extremos (|z| > 3) antes de imputar con mediana
    # Límites clínicos: 24–43 °C (NIH); z-score captura valores imposibles fuera de ese rango
    temp_valida = rick['temperatura'].dropna()
    z_scores = pd.Series(stats.zscore(temp_valida), index=temp_valida.index)
    rick.loc[abs(z_scores) > 3, 'temperatura'] = np.nan
    rick['temperatura_imput'] = rick['temperatura'].isnull().astype('category')
    rick['temperatura'] = rick['temperatura'].fillna(rick['temperatura'].median())

    return rick


def feature_engineering(rick: pd.DataFrame) -> pd.DataFrame:
    """Aplica tipos de datos, elimina redundancias y crea nuevas variables."""

    rick = _convertir_fechas(rick)

    # Columnas categóricas (índices definidos tras exploración del dataset)
    cat_cols = (
        list(rick.columns[0:2])    +
        list(rick.columns[3:15])   +
        list(rick.columns[18:24])  +
        list(rick.columns[27:39])  +
        list(rick.columns[40:121]) +
        list(rick.columns[122:138])+
        list(rick.columns[139:142])+
        list(rick.columns[147:149])+
        list(rick.columns[150:151])+
        list(rick.columns[152:154])+
        list(rick.columns[157:158])+
        list(rick.columns[160:162])+
        list(rick.columns[164:166])+
        list(rick.columns[167:169])+
        list(rick.columns[171:173])
    )
    rick[cat_cols] = rick[cat_cols].astype('category')

    # des_diag_probable es redundante con des_diag_final
    rick = rick.drop('des_diag_probable', axis=1)

    # Binarizar compromiso_organos (1=Sí, 2=No, 0=Desconocido)
    rick['compromiso_organos_binario'] = (
        rick['compromiso_organos'].apply(_clasificar_compromiso).astype('category')
    )

    rick = _calcular_tiempos(rick)

    return rick


def corregir_fechas(rick: pd.DataFrame) -> pd.DataFrame:
    """Corrige fechas con errores de captura identificados en EDA.

    Estrategia:
      - Errores de dedo: se corrige con la fecha lógica revisada caso a caso.
      - Fechas de estudio (ini/fin) atípicas: se reemplazan con fecha de toma
        y recepción de muestra de rickettsia en sangre.
      - Las correcciones se documentan con columnas indicadoras '_corr'.
    """

    # ── Indicadores de corrección ─────────────────────────────────────────────
    rick['fec_ini_estudio_corr']      = False
    rick['fec_fin_estudio_corr']      = False
    rick['fec_sol_aten_corr']         = False
    rick['fec_ini_signos_alarma_corr']= False
    rick['fec_ini_signos_sint_corr']  = False
    rick['fec_ini_fiebre_corr']       = False

    # ── Ronda 1: errores de dedo en fec_ini_estudio ───────────────────────────
    # tiempo_res_hosp negativo → fec_ini_estudio capturada antes de fec_sol_aten
    corr_ini_estudio_r1 = {
        970873:  '2022-09-27',
        1017888: '2023-04-12',
        1910384: '2024-12-25',
        1839284: '2024-11-12',
        1417033: '2024-06-26',
        1404541: '2024-06-17',
        1353224: '2024-04-01',
        1900790: '2024-12-10',
        1040641: '2023-06-29',
    }
    for ide_id, fecha in corr_ini_estudio_r1.items():
        rick.loc[rick['ide_id'] == ide_id, 'fec_ini_estudio'] = pd.to_datetime(fecha)
        rick.loc[rick['ide_id'] == ide_id, 'fec_ini_estudio_corr'] = True

    # ── Ronda 1: errores de dedo en fec_fin_estudio ───────────────────────────
    # dias_estudio negativo → fec_fin_estudio capturada antes de fec_ini_estudio
    corr_fin_estudio_r1 = {
        929600:  '2022-01-24',
        1580676: '2024-09-04',
        1910384: '2025-01-02',
        1900790: '2024-12-10',
    }
    for ide_id, fecha in corr_fin_estudio_r1.items():
        rick.loc[rick['ide_id'] == ide_id, 'fec_fin_estudio'] = pd.to_datetime(fecha)
        rick.loc[rick['ide_id'] == ide_id, 'fec_fin_estudio_corr'] = True

    # ── Ronda 1: errores de dedo en fec_sol_aten ─────────────────────────────
    # demora_pac negativa → fec_sol_aten capturada antes de fec_ini_signos_sint
    corr_sol_aten_r1 = {
        945783:  '2022-06-22',
        955534:  '2022-08-11',
        969775:  '2022-09-25',
        1219037: '2023-10-18',
        1060641: '2023-07-18',
        1056168: '2023-07-25',
        1899284: '2024-12-08',
        1456970: '2024-07-14',
        1467071: '2024-07-24',
    }
    for ide_id, fecha in corr_sol_aten_r1.items():
        rick.loc[rick['ide_id'] == ide_id, 'fec_sol_aten'] = pd.to_datetime(fecha)
        rick.loc[rick['ide_id'] == ide_id, 'fec_sol_aten_corr'] = True

    # Correcciones adicionales que afectan múltiples columnas de fecha
    rick.loc[rick['ide_id'] == 969775,  'fec_ini_estudio'] = pd.to_datetime('2022-09-25')
    rick.loc[rick['ide_id'] == 969775,  'fec_ini_estudio_corr'] = True

    rick.loc[rick['ide_id'] == 1456970, 'fec_ini_estudio'] = pd.to_datetime('2024-07-22')
    rick.loc[rick['ide_id'] == 1456970, 'fec_fin_estudio'] = pd.to_datetime('2024-07-22')
    rick.loc[rick['ide_id'] == 1456970, 'fec_ini_estudio_corr'] = True
    rick.loc[rick['ide_id'] == 1456970, 'fec_fin_estudio_corr'] = True

    # ── Ronda 1: error en fec_ini_signos_alarma ───────────────────────────────
    # demora_pac_signos_alarma extremadamente negativa → error de captura
    rick.loc[rick['ide_id'] == 1426998, 'fec_ini_signos_alarma'] = pd.to_datetime('2024-07-01')
    rick.loc[rick['ide_id'] == 1426998, 'fec_ini_signos_alarma_corr'] = True

    rick = _calcular_tiempos(rick)

    # ── Ronda 2: reemplazar fechas de estudio con fechas de muestra ───────────
    # tiempo_res_hosp negativo por fechas invertidas (ini_estudio < sol_aten);
    # se usa la fecha de toma/recepción de muestra como proxy más confiable
    ids_ini_r2 = [955541, 959270, 962575, 966432, 990983, 1894148, 1722741, 1515092, 1467071]
    ids_fin_r2 = [955541, 962575, 966432, 990983, 1894148, 1722741, 1515092, 1467071]

    rick.loc[rick['ide_id'].isin(ids_ini_r2), 'fec_ini_estudio'] = \
        rick.loc[rick['ide_id'].isin(ids_ini_r2), 'fecha_toma_rickett_sangre']
    rick.loc[rick['ide_id'].isin(ids_fin_r2), 'fec_fin_estudio'] = \
        rick.loc[rick['ide_id'].isin(ids_fin_r2), 'fecha_recep_rickett_sangre']
    rick.loc[rick['ide_id'].isin(ids_ini_r2), 'fec_ini_estudio_corr'] = True
    rick.loc[rick['ide_id'].isin(ids_fin_r2), 'fec_fin_estudio_corr'] = True

    rick = _calcular_tiempos(rick)

    # ── Ronda 3: outliers por z-score en variables de tiempo ──────────────────
    # Casos con tiempos extremos (días de estudio o espera muy altos);
    # se reemplazan fechas de estudio con fechas de toma/recepción de muestra
    ids_ini_r3 = [1037630, 937372]
    ids_fin_r3 = [
        1037630, 937372, 1001883, 1478718, 1485017, 1807300, 1846472,
        1850357, 1383006, 1668847, 1036510, 1273603, 929233, 1014803,
        963689, 972017, 949579, 996911,
    ]

    rick.loc[rick['ide_id'].isin(ids_ini_r3), 'fec_ini_estudio'] = \
        rick.loc[rick['ide_id'].isin(ids_ini_r3), 'fecha_toma_rickett_sangre']
    rick.loc[rick['ide_id'].isin(ids_fin_r3), 'fec_fin_estudio'] = \
        rick.loc[rick['ide_id'].isin(ids_fin_r3), 'fecha_recep_rickett_sangre']
    rick.loc[rick['ide_id'].isin(ids_ini_r3), 'fec_ini_estudio_corr'] = True
    rick.loc[rick['ide_id'].isin(ids_fin_r3), 'fec_fin_estudio_corr'] = True

    # Corrección de fec_ini_signos_sint y fec_ini_fiebre para ide_id 1391525
    rick.loc[rick['ide_id'] == 1391525, 'fec_ini_signos_sint'] = pd.to_datetime('2024-06-03')
    rick.loc[rick['ide_id'] == 1391525, 'fec_ini_signos_sint_corr'] = True
    rick.loc[rick['ide_id'] == 1391525, 'fec_ini_fiebre'] = pd.to_datetime('2024-06-03')
    rick.loc[rick['ide_id'] == 1391525, 'fec_ini_fiebre_corr'] = True
    rick.loc[rick['ide_id'] == 1391525, 'fec_ini_estudio_corr'] = True

    # Corrección de fec_sol_aten para ide_id 933961
    rick.loc[rick['ide_id'] == 933961, 'fec_sol_aten'] = pd.to_datetime('2024-06-03')
    rick.loc[rick['ide_id'] == 933961, 'fec_sol_aten_corr'] = True

    rick = _calcular_tiempos(rick)

    return rick


# =============================================================================
# Main
# =============================================================================

def main() -> None:
    print(f'Leyendo: {INPUT_FILE}')
    rick = pd.read_csv(INPUT_FILE)
    print(f'  Dataset cargado: {rick.shape[0]:,} filas × {rick.shape[1]} columnas')

    rick = imputar(rick)
    print('  Imputación completada.')

    rick = feature_engineering(rick)
    print('  Feature engineering completado.')

    rick = corregir_fechas(rick)
    print('  Corrección de fechas completada.')

    rick.to_csv(OUTPUT_FILE, index=False)
    print(f'\nArchivo exportado: {OUTPUT_FILE}')
    print(f'  Shape final: {rick.shape[0]:,} filas x {rick.shape[1]} columnas')


if __name__ == '__main__':
    main()
