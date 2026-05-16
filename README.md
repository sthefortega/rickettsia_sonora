# Machine Learning para diagnóstico de Rickettsiosis basado en casos 2022-2024 en Sonora

<a target="_blank" href="https://cookiecutter-data-science.drivendata.org/">
    <img src="https://img.shields.io/badge/CCDS-Project%20template-328F97?logo=cookiecutter" />
</a>

Modelo de diagnóstico de Rickettsiosis en el estado de Sonora

## Colaboradores
- Mario Castro

- Oscar Senday

- Esthefania Ortega

## Asesora experta:
- Dra. Pamela Romo

## ¿Que problema se plantea resolver?
Crear un modelo capaz de diagnosticar oportunamente casos de cualquier especie de Rickettsiosis, un grupo de enfermedades febriles, ocasionadas por bacterias del género Rickettsia, y tienen en común el ocasionar presencia de manchas en piel cuando se agudiza el cuadro clínico.
Como enfermedad infecciosa, la fiebre manchada (FMRR) o Rickettsiosis tiene un periodo de incubación que usualmente es de 4-7 días, pero puede abarcar un periodo desde 2 hasta 14 días y se considera de alta letalidad.

### ¿Cuál es el principal obstáculo en el diagnóstico actual?
La falta de sospecha por los pacientes y médicos de primer contacto. Se han hecho grandes esfuerzos por educar a la población en general para que sepan de la enfermedad y busquen atención ante cualquier sospecha, pero muchos pacientes confunden los signos con enfermedades virales comunes y no acuden a revisión en los primeros días del cuadro. Así mismo, muchos médicos de primer contacto no interrogan antecedentes epidemiológicos y por lo tanto no sospechan la enfermedad, permitiendo que el cuadro avance.

Los primeros 5 días son clave para disminuir la letalidad. La FMRR es causada por una bacteria, por lo que el inicio oportuno del antibiótico es clave para evitar la evolución de la enfermedad. Hay estudios que evidencían que la mortalidad aumenta considerablemente cuando el tratamiento antibiótico se inicia después del 5to día de síntomas. 

Por esta razón, **el usuario final objetivo es el médico de primer contacto**.  Dado que su acceso a resultados de laboratorio son limitados, se utilizaran únicamente variables clínicas, demográficas, epidemiológicas y comorbilidades.

Un modelo ligero que dispare una alerta de "sospecha de rickettsiosis, iniciar doxiciclina empírica" tiene el potencial de salvar más vidas por volumen de pacientes atendidos.


## ¿Porqué es un problema importante para la institución/organización/empresa/usuario?
Actualmente el diagnóstico se hace solo por medio del Laboratorio Estatal de Salud Pública, ya sea por PCR o IFI, pero el caso tiene que llegar a una unidad epidemiológica, ya sea en centro de salud u hospital para que se tomen las muestras. Es una enfermedad infradiagnosticada y que los datos reportados en su gran mayoría subestiman la carga de la enfermedad.

### Desde la perspectiva clínica y epidemiológica
El diagnóstico oportuno es el talón de Aquiles de la rickettsiosis en Sonora. La enfermedad debuta con un cuadro febril inespecífico —fiebre, cefalea, mialgias— que es prácticamente indistinguible de dengue, leptospirosis, o incluso una influenza en sus primeras 48-72 horas. Para cuando aparece el exantema, que sería la señal de alarma más característica, muchos pacientes ya están en un estado crítico o con daño multiorgánico establecido. Ese retraso diagnóstico se traduce directamente en muertes evitables.

### Desde la perspectiva institucional para Secretaria de Salud
La carga operativa en los municipios de mayor riesgo —Hermosillo, Caborca, la región de la costa— es real. Los médicos de primer contacto en unidades de salud rurales o suburbanas no siempre tienen el entrenamiento ni las herramientas para sospechar rickettsiosis tempranamente. Un modelo que apoye esa decisión clínica en el primer nivel de atención sería un cambio de paradigma.

### Desde la perspectiva de la mortalidad
Sonora históricamente ha reportado tasas de letalidad que superan la media nacional, y sabemos que la mayoría de esas muertes ocurren en pacientes que llegaron tarde al diagnóstico o que no recibieron doxiciclina a tiempo.

## ¿Que problema de aprendizaje implica resolver?
- Clasificación entre caso positivo o negativo a Rickettsiosis. 

## ¿Qué métricas permiten medir la calidad del modelo de aprendizaje? ¿Cuales son sus valores deseables?
Se busca minimizar los falsos negativos, priorizando el Recall, ya que en rickettsiosis, un falso negativo cuesta una vida. Un falso positivo cuesta un ciclo de doxiciclina y quizás una hospitalización innecesaria.

**Para el modelo diagnóstico**
| Métrica | Importancia | Valor deseable |
|---|---|---|
| **Sensibilidad (Recall)**| No perder casos reales | ≥ 0.90 |
| **Especificidad**| No saturar el sistema con falsas alarmas| ≥ 0.80 |
| **AUC-ROC** | Capacidad discriminativa general| ≥ 0.85 |
| **F1-Score** | Balance precision-recall | ≥ 0.85|


## ¿Como están alineadas las métricas de la calidad del modelo con los objetivos de la institución/organización/empresa/usuario?
El diagnóstico humano en rickettsiosis tiene un desempeño sorprendentemente bajo, especialmente en primer nivel.
Algunos puntos de referencia reales:

- A finales de 2025, Sonora reportaba 140 casos y una incidencia de 4.4 casos por 100 mil habitantes, con una letalidad del 38%, posicionándose en el primer lugar nacional de mayor cantidad de casos por 100 mil habitantes.
- Se plantea una mortalidad mayor al 65% sin tratamiento adecuado o en tiempo para FMRR a nivel nacional acorde a CENAPRECE.

Considerando la Secretaría de Salud y el médico de primer contacto como usuarios: 

**Modelo de diagnóstico**
| Métrica | Objetivo institucional alineado |
|---|---|
| Sensibilidad ≥ 0.90 | Reducir muertes por diagnóstico tardío |
| Especificidad ≥ 0.80 | Uso racional de doxiciclina y recursos hospitalarios |
| AUC-ROC ≥ 0.85 | Confianza institucional en la herramienta para política pública |
| F1-Score ≥ 0.85 | Balance operativo para el médico de primer contacto | 


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
│   └── 2.2-macl-EDA.ipynb       <- Continuación de análisis exploratorio y procesamiento de datos final.
│
├── pyproject.toml     <- Project configuration file with package metadata for 
│                         rickettsia_sonora and configuration for tools like black
│
├── references                     <- Data dictionaries, manuals, and all other explanatory materials.
│   ├── catalogo.xlsx              <- Catalogo para especie, servicio y motivo de rechazo de muestra, descargado de Datos Abiertos.
│   ├── diccionario_ricket_1.csv   <- Diccionario de variables de datos, descargado de Datos Abiertos.
│   └── 
│
├── reports                         <- Generated analysis as HTML, PDF, LaTeX, etc.
│   ├── figures                     <- Gráficos generados y figuras a usarse en reportes
│   └── SWEETVIZ_REPORT.html        <- Reporte de AutoEDA con SweetViz.
│
├── src            
│   └── data        
│       └── make_dataset.py     <- Pipeline de descarga de datos crudos.
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

## Referencias
https://pmc.ncbi.nlm.nih.gov/articles/PMC12928218/
http://www.cenaprece.salud.gob.mx/programas/interior/vectores/descargas/pdf/Induccion_Atencionhumanorickett17.pdf
https://salud.sonora.gob.mx/media/attachments/2026/01/20/informe-fmrr-se-01.2026-.pdf 
https://salud.sonora.gob.mx/media/attachments/2026/05/15/informe-fmrr-se-18-2026.pdf
--------