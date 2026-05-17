## Evaluación de Resultados

### Resultados obtenidos

| Modelo | Recall/Sensibilidad | Especificidad | AUC-ROC | F1-Score |
|---|---|---|---|---|
| SVM | 0.7551 | 0.7485 | 0.8262 | 0.5670 |
| Logistic Regression | 0.7244 | 0.8220 | 0.8347 | 0.6120 |
| Random Forest | 0.6428 | 0.8785 | 0.8364 | 0.6176 |
| Gradient Boosting | 0.4388 | 0.9435 | 0.7819 | 0.5341 |

Los umbrales objetivo establecidos para el proyecto eran: Recall ≥ 0.90, Especificidad ≥ 0.80, AUC-ROC ≥ 0.85 y F1 ≥ 0.85.

### ¿Los resultados son buenos?

En términos clínicos, **ningún modelo alcanza los umbrales objetivo de forma simultánea**, lo que significa que los resultados actuales no son suficientes para el uso clínico directo.

- **Recall:** El mejor valor es 0.7551 (SVM), lo que implica que aproximadamente 1 de cada 4 casos reales de rickettsiosis sería clasificado erróneamente como negativo. En el contexto clínico del proyecto —donde un falso negativo puede costar una vida— este resultado es insuficiente respecto al umbral ≥ 0.90.
- **Especificidad:** Solo Logistic Regression (0.8220) y Random Forest (0.8785) superan el umbral de 0.80. El SVM, que tiene el mejor Recall, tiene especificidad de apenas 0.7485, lo que generaría una carga operativa elevada por falsas alarmas.
- **AUC-ROC:** Los mejores valores rondan 0.83–0.84, por debajo del umbral ≥ 0.85. Esto indica una capacidad discriminativa moderada pero no suficiente.
- **F1-Score:** El mejor valor es 0.6176 (Random Forest), muy por debajo del objetivo ≥ 0.85.

Dicho esto, los resultados **no son malos para un problema de estas características**: dataset pequeño (~2,600 casos, con alta proporción de probables sin confirmación), alta dimensionalidad, y una tarea de clasificación donde la variable objetivo (resultado de laboratorio) no estaba disponible para todos los pacientes. Un AUC-ROC cercano a 0.84 sobre datos clínicos ruidosos con múltiples valores faltantes es un punto de partida válido.

Un aspecto crítico que no refleja la tabla es el **umbral de clasificación**. Los modelos usan 0.5 por defecto, pero bajando el umbral (por ejemplo, a 0.25–0.35) se puede incrementar el Recall a expensas de la especificidad, lo que podría ser aceptable clínicamente si la relación costo-beneficio lo justifica.

### ¿Hay resultados similares en la literatura?

La literatura disponible se concentra principalmente en modelos de apoyo para la **detección temprana** y en trabajos de **vigilancia epidemiológica** de enfermedades infecciosas. Sin embargo, se observa un número limitado de modelos clínicos específicos aplicados directamente a la **rickettsiosis**.

- **Aplicaciones de IA y Machine Learning en salud**: 
 Existen publicaciones recientes sobre el uso de **inteligencia artificial (IA)** y **machine learning** en el ámbito de enfermedades infecciosas y predicción de riesgos. Los principales enfoques incluyen: 
 - Vigilancia poblacional.
 - Detección temprana de brotes.
 - Evaluación de riesgo individual.
 Aunque estos trabajos no se centran exclusivamente en rickettsiosis, sí refuerzan la pertinencia de explorar modelos predictivos en este campo.

- **Rickettsiosis como enfermedad emergente**:
 Se identifican referencias que la catalogan como **emergente o reemergente de importancia epidemiológica**, lo que justifica su relevancia como área de investigación para el desarrollo de modelos predictivos.

- **Modelos diagnósticos existentes**:
 Sí se han reportado **algoritmos clínicos y guías diagnósticas** para rickettsiosis. No obstante, la evidencia predominante corresponde a otros más que a modelos de machine learning validados de manera amplia:

 - **Criterios clínicos**.
 - **Pruebas de laboratorio**.
 - **Guías diagnósticas**.

En conclusión, los resultados son **coherentes con lo reportado en problemas diagnósticos similares**. La brecha respecto a los umbrales objetivo sugiere que se requieren más datos, mejores features (p. ej., datos climáticos de CONAGUA ya descargados) o técnicas más avanzadas.

### ¿Por qué escoger un modelo sobre otro?

La elección depende de la prioridad clínica. Dado que el objetivo del proyecto es **minimizar falsos negativos**, el criterio primario debe ser el Recall:

- **SVM (recomendado para deploy inicial):** Mejor Recall (0.7551). Aunque su especificidad es la más baja de todos (0.7485), en este contexto una alerta falsa de doxiciclina tiene consecuencias menores que un caso perdido. Adicionalmente, SVM funciona razonablemente bien en espacios de alta dimensionalidad con clases desbalanceadas cuando se usa `class_weight='balanced'`.
- **Logistic Regression (recomendado para interpretabilidad):** Balance razonable entre Recall (0.7244) y Especificidad (0.8220, la única que supera el umbral), con el AUC-ROC más alto del grupo de modelos con especificidad aceptable (0.8347). Tiene la ventaja adicional de que los coeficientes son interpretables, lo que permite comunicar al médico qué variables pesan más —útil para validación clínica con expertos como la Dra. Pamela Romo.
- **Random Forest:** Mejor AUC-ROC (0.8364) y mejor F1 (0.6176), pero Recall de solo 0.6428. Útil si el umbral se ajusta a la baja para recuperar sensibilidad.
- **Gradient Boosting:** Descartado para este caso de uso clínico. Un Recall de 0.4388 implica que más de la mitad de los casos reales serían missed, lo que es inaceptable.

**Recomendación operativa:** entrenar Logistic Regression o SVM con búsqueda de umbral óptimo sobre la curva ROC, fijando Recall ≥ 0.90 como restricción y maximizando la especificidad resultante.

### ¿El modelo final podría ponerse en producción?

**No en su estado actual**, pero sí como herramienta piloto con supervisión médica. Los obstáculos concretos son:

1. **Recall insuficiente:** Con 0.75 de sensibilidad, el modelo perdería ~1 de cada 4 casos reales. El umbral clínicamente aceptable mínimo es 0.90.
2. **Falta de validación externa:** El modelo fue entrenado y evaluado sobre el mismo conjunto de datos histórico de Sonora 2022–2024. Requiere validación prospectiva con nuevos casos y, de ser posible, en otros estados endémicos.
3. **Desbalance de clases no resuelto completamente:** La alta proporción de casos "Probables" (sin confirmación de laboratorio) contamina el target; esto limita la calidad de la señal de entrenamiento.
4. **Requisitos regulatorios:** En México, un software de apoyo diagnóstico requiere evaluación por COFEPRIS si se comercializa como dispositivo médico. Para uso interno en la Secretaría de Salud de Sonora, el proceso es diferente, pero igualmente requiere un protocolo de validación clínica formal.

**Camino hacia producción:**

- Ajuste de umbral para garantizar Recall ≥ 0.90 en datos de validación
- Incorporación de datos climáticos y variables de temporalidad
- Validación prospectiva con al menos una temporada epidemiológica completa (2025)
- Interfaz simple para el médico de primer contacto (probabilidad + síntomas detonantes)
- Auditoría y monitoreo continuo del desempeño en campo

## ¿Justifica el uso de un LLM?

Para la **tarea central del proyecto** —clasificación binaria de diagnóstico a partir de variables clínicas tabulares— un LLM **no es necesario ni el enfoque más adecuado**. Los modelos de ML clásicos son más interpretables, reproducibles, auditables y eficientes computacionalmente para datos estructurados. Un LLM entrenado de forma general no tiene ventaja sobre Random Forest o Regresión Logística en una tabla de síntomas binarios.

Sin embargo, hay escenarios específicos donde un LLM sí **agrega valor real al sistema completo**:

1. **Recolección estructurada de anamnesis:** Un LLM puede conducir una entrevista clínica en lenguaje natural con el médico de primer contacto (o incluso con el paciente), traducir las respuestas a las variables binarias que el modelo de ML necesita, y reducir los errores de captura. Esto resuelve uno de los principales cuellos de botella operativos: llenar un formulario de 150+ variables.

2. **Explicación del resultado al médico:** El ML produce una probabilidad; el LLM puede generar una justificación clínica en lenguaje natural: *"El modelo identifica como factores de riesgo el contacto con perros con ectoparásitos, la fiebre de 5 días de evolución y el municipio de Hermosillo. Se recomienda iniciar doxiciclina empírica."*

3. **Manejo de notas clínicas no estructuradas:** Si en el futuro se integran expedientes en texto libre, un LLM puede extraer features para alimentar el clasificador.

4. **Apoyo en la interpretación epidemiológica a nivel jurisdiccional:** Síntesis de alertas, generación de reportes automáticos para la Secretaría de Salud.

### ¿Qué modelo LLM?

Si se decide incorporar un LLM, el perfil óptimo para este proyecto es:

| Criterio | Relevancia para el proyecto |
|---|---|
| Capacidad en español médico | Alta — usuarios y expedientes en español |
| Manejo seguro de información sensible | Alta — datos de salud de pacientes |
| Capacidad de razonamiento clínico | Alta — justificación de alertas |
| Costo de inferencia en producción | Alta — uso en primer nivel de atención con recursos limitados |
| Disponibilidad como API | Alta — integración con sistema existente |

**Advertencia importante:** En ningún escenario el LLM debe actuar como diagnóstico autónomo. Debe operar como asistente de recolección y explicación, con el modelo de ML siendo el responsable de la clasificación y el médico siendo el responsable de la decisión clínica final.

---

### 🔗 Referencias relevantes

- Petri, W. A. (2024). *Generalidades sobre las rickettsiosis y las infecciones relacionadas*. MSD Manuals. 
 [Enlace al recurso](https://www.msdmanuals.com/es/professional/enfermedades-infecciosas/rickettsias-y-microorganismos-relacionados/generalidades-sobre-las-rickettsiosis-y-las-infecciones-relacionadas)

- Estrada-Peña, A. (2024). *Machine learning algorithms for the evaluation of risk by tick-borne pathogens in Europe*. *Annals of Medicine*. 
 [Enlace al recurso](https://www.tandfonline.com/doi/full/10.1080/07853890.2024.2405074#abstract)
