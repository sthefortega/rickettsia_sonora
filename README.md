# Machine Learning para diagnóstico de Rickettsiosis basado en casos 2022-2024 en Sonora

<a target="_blank" href="https://cookiecutter-data-science.drivendata.org/">
    <img src="https://img.shields.io/badge/CCDS-Project%20template-328F97?logo=cookiecutter" />
</a>

Modelo de diagnóstico de Rickettsiosis y predicción de letalidad en el estado de Sonora

## ¿Que problema se plantea resolver?
Crear un modelo capaz de diagnosticar oportunamente casos de cualquier especie de Rickettsiosis, un grupo de enfermedades febriles, ocasionadas por bacterias del género Rickettsia, y tienen en común el ocasionar presencia de manchas en piel cuando se agudiza el cuadro clínico.
Además, se buscará crear un modelo secundario capaz de predecir la letalidad del caso basado en características demográficas, clínicas y tiempo de respuesta. 

Se plantean dos usuarios distintos para dos momentos clínicos:

- **Usuario 1** — Médico de primer contacto (variables clínicas + demográficas + epidemiológicas + comorbilidades)
Con fiebre, cefalea, antecedente de exposición a garrapatas o zona endémica, y algunas variables básicas de laboratorio general accesibles en clínica. Un modelo ligero que dispare una alerta de "sospecha de rickettsiosis, iniciar doxiciclina empírica" salvaría más vidas por volumen de pacientes atendidos.

- **Usuario 2** — Médico hospitalario o epidemiólogo de jurisdicción (variables completas incluyendo PCR, bioquímica avanzada, líquidos en cavidades) Con el panel completo disponible, un modelo más robusto podría predecir letalidad y orientar decisiones de manejo intensivo, traslado, o notificación prioritaria.

## ¿Porqué es un problema importante para la institución/organización/empresa/usuario?
### Desde la perspectiva clínica y epidemiológica
El diagnóstico oportuno es el talón de Aquiles de la rickettsiosis en Sonora. La enfermedad debuta con un cuadro febril inespecífico —fiebre, cefalea, mialgias— que es prácticamente indistinguible de dengue, leptospirosis, o incluso una influenza en sus primeras 48-72 horas. Para cuando aparece el exantema, que sería la señal de alarma más característica, muchos pacientes ya están en un estado crítico o con daño multiorgánico establecido. Ese retraso diagnóstico se traduce directamente en muertes evitables.
### Desde la perspectiva institucional para Secretaria de Salud
La carga operativa en los municipios de mayor riesgo —Hermosillo, Caborca, la región de la costa— es real. Los médicos de primer contacto en unidades de salud rurales o suburbanas no siempre tienen el entrenamiento ni las herramientas para sospechar rickettsiosis tempranamente. Un modelo que apoye esa decisión clínica en el primer nivel de atención sería un cambio de paradigma.
### Desde la perspectiva de la mortalidad
Sonora históricamente ha reportado tasas de letalidad que superan la media nacional, y sabemos que la mayoría de esas muertes ocurren en pacientes que llegaron tarde al diagnóstico o que no recibieron doxiciclina a tiempo.

## ¿Que problema de aprendizaje implica resolver?
- Clasificación entre caso positivo a Rickettsiosis o negativo. 
- Clasificación entre caso letal o no letal. 

## ¿Qué métricas permiten medir la calidad del modelo de aprendizaje? ¿Cuales son sus valores deseables?
Se busca minimizar los falsos negativos, priorizando el Recall, ya que en rickettsiosis, un falso negativo cuesta una vida. Un falso positivo cuesta un ciclo de doxiciclina y quizás una hospitalización innecesaria.

**Para el modelo diagnóstico**
| Métrica | Importancia | Valor deseable |
|---|---|---|
| **Sensibilidad (Recall)**| No perder casos reales | ≥ 0.90 |
| **Especificidad**| No saturar el sistema con falsas alarmas| ≥ 0.80 |
| **AUC-ROC** | Capacidad discriminativa general| ≥ 0.85 |
| **F1-Score** | Balance precision-recall | ≥ 0.85|

**Para el modelo de letalidad**
| Métrica | Importancia | Valor deseable |
|---|---|---|
| **Sensibilidad (Recall)** | Detectar pacientes críticos para intervenir | ≥ 0.85 |
| **AUC-ROC** | Discriminación general | ≥ 0.80 |

## ¿Como están alineadas las métricas de la calidad del modelo con los objetivos de la institución/organización/empresa/usuario?
El diagnóstico humano en rickettsiosis tiene un desempeño sorprendentemente bajo, especialmente en primer nivel.
Algunos puntos de referencia reales:

- Estudios en México documentan que el diagnóstico clínico no apoyado por herramientas tiene sensibilidades de 50-65% en primer contacto, precisamente porque el cuadro inicial es inespecífico.
- El retraso diagnóstico promedio reportado en Sonora ha sido de 4-7 días desde inicio de síntomas.
- Muchos casos se diagnostican post-mortem o retrospectivamente.

Considerando la Secretaría de Salud y el médico de primer contacto como usuarios: 

**Modelo de diagnóstico**
| Métrica | Objetivo institucional alineado |
|---|---|
| Sensibilidad ≥ 0.90 | Reducir muertes por diagnóstico tardío |
| Especificidad ≥ 0.80 | Uso racional de doxiciclina y recursos hospitalarios |
| AUC-ROC ≥ 0.85 | Confianza institucional en la herramienta para política pública |
| F1-Score ≥ 0.85 | Balance operativo para el médico de primer contacto | 

**Modelo de letalidad**
| Métrica | Objetivo institucional alineado |
|---|---|
| Sensibilidad ≥ 0.85 | Identificar pacientes que requieren manejo intensivo o traslado urgente |
| AUC-ROC ≥ 0.80 | Apoyo a decisiones de triaje hospitalario (priorizacion de casos acorde a gravedad) y asignación de recursos de UCI |


## Estructura del proyecto

```
├── LICENSE            <- Open-source license if one is chosen
├── Makefile           <- Makefile with convenience commands like `make data` or `make train`
├── README.md          <- The top-level README for developers using this project.
├── data
│   ├── external       <- 
│   ├── interim        <- Datos transformados en procesos intermedios
│   ├── processed      <- Datos finales para modelado
│   └── raw            <- Datos directamente descargados de su fuente
│
├── docs               <- A default mkdocs project; see www.mkdocs.org for details
│
├── models             <- Trained and serialized models, model predictions, or model summaries
│
├── notebooks          
│   ├── 1.0-eot-ETL.ipynb        <- Descarga de datos crudos a raw/ con mínimo preprocesamiento
│   ├── 2.0-eot-autoEDA.ipynb    <- Análisis exploratorio automático con SweetViz
│   ├── 2.1-eot-EDA_PCA.ipynb    <- Análisis exploratorio, procesamiento intermedio y PCA.
│   └── 
│
├── pyproject.toml     <- Project configuration file with package metadata for 
│                         rickettsia_sonora and configuration for tools like black
│
├── references         <- Data dictionaries, manuals, and all other explanatory materials.
│   ├── catalogo.xlsx              <- Catalogo para especie, servicio y motivo de rechazo de muestra, descargado de Datos Abiertos.
│   ├── diccionario_ricket_1.csv   <- Diccionario de variables de datos, descargado de Datos Abiertos.
│   └── 
│
├── reports            <- Generated analysis as HTML, PDF, LaTeX, etc.
│   ├── figures        <- Gráficos generados y figuras a usarse en reportes
│   └── SWEETVIZ_REPORT.html        <- Reporte de AutoEDA con SweetViz.
│
├── requirements.txt   <- The requirements file for reproducing the analysis environment, e.g.
│                         generated with `pip freeze > requirements.txt`
│
├── setup.cfg          <- Configuration file for flake8
│
└── rickettsia_sonora   <- Source code for use in this project.
    │
    ├── __init__.py             <- Makes rickettsia_sonora a Python module
    │
    ├── config.py               <- Store useful variables and configuration
    │
    ├── dataset.py              <- Scripts to download or generate data
    │
    ├── features.py             <- Code to create features for modeling
    │
    ├── modeling                
    │   ├── __init__.py 
    │   ├── predict.py          <- Code to run model inference with trained models          
    │   └── train.py            <- Code to train models
    │
    └── plots.py                <- Code to create visualizations
```

--------

