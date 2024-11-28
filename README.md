
# # API de Análisis de Incidencias

## Descripción

La API de Seguridad Ciudadana es un servicio web diseñado para proporcionar acceso a datos y modelos relacionados con la seguridad en la ciudad. Esta API permite a los desarrolladores integrar funcionalidades de análisis y predicción en sus aplicaciones, facilitando la toma de decisiones informadas basadas en datos históricos y modelos de machine learning.

## Funcionalidades

La API permite:

- **Entrenamiento de Modelos**: Permite entrenar un modelo de machine learning utilizando los datos proporcionados. Se pueden usar modelos como Random Forest, regresión lineal, y otros.
- **Predicciones**: Una vez entrenado un modelo, se pueden hacer predicciones sobre nuevos datos utilizando el modelo entrenado.
- **Generación de Informes**: Se generan informes gráficos en formato PDF, visualizando la importancia de las características y el rendimiento del modelo.


Esta API permite entrenar un modelo de machine learning utilizando datos históricos de incidencias y generar predicciones sobre futuros incidentes.

## Endpoints

### `/`
Proporciona información básica sobre la API y los endpoints disponibles.

### `/entrenar_modelo` (POST)
Recibe datos en formato JSON, entrena los modelos de machine learning (regresión y clasificación) y devuelve predicciones basadas en esos datos. Los modelos entrenados se guardan en archivos.

#### Datos esperados:
- **mes**: Mes del incidente.
- **dia**: Día del mes.
- **hora**: Hora del incidente en formato HH:MM.
- **cantidad**: Número de incidencias.
- **tipo_incidencia**: Tipo de incidencia (categoría).

### `/predicciones` (POST)
Recibe nuevos datos en formato JSON y genera predicciones sobre la cantidad y tipo de incidencias.


### Flujo Completo: Entrenamiento y Predicción

1. **Entrenamiento del Modelo**: Primero, debes entrenar tu modelo con datos históricos. Esto se hace una vez y luego se guarda el modelo.

2. **Obtención de Datos y Procesamiento**: Luego, obtienes los datos que deseas predecir, procesas esos datos y finalmente los envías a la API para obtener la predicción.


### Resumen del Flujo

1. **Entrenamiento del Modelo**: Se entrena un modelo con datos históricos y se guarda.
2. **Preparación de Datos**: Se preparan los datos que se quieren predecir.
3. **Envío de Solicitud**: Se envían los datos a la API mediante una solicitud POST.
4. **Recepción de Predicción**: Se recibe la respuesta con la predicción.

Este flujo asegura que los datos estén correctamente procesados y que el modelo esté listo para hacer predicciones basadas en nuevos datos.

**Modo local**:
###
      download_urls = {
         pdf_name1: storage_path+ "/" + pdf_name1,
         pdf_name2: storage_path + "/" + pdf_name2
      }
###

**Modo alojado**
###
      download_urls = {
         # pdf_name1: "Ruta del dominio de tu api/static/pdfs/" + pdf_name1,
         # pdf_name2: "Ruta del dominio de tu api/static/pdfs/" + pdf_name2
    
      }
###

## Requisitos
- Python 3.7+
- Librerías: Flask, pandas, seaborn, scikit-learn, matplotlib, joblib, etc.


## Instalación

1. Clona el repositorio:
   ```bash
   git clone <URL del repositorio>
   ```
2. Navega al directorio del proyecto:
   ```bash
   cd <nombre del proyecto>
   ```
3. Instala las dependencias:
   ```bash
   **instala entorno virtual en windows**
   python -m venv .venv

   **instala entorno virtual macOs o linux**
   python3 -m venv .venv

   **activa entorno virtual en windows**
   .venv\bin\activate

   **activa entorno virtual macOs o linux**
   source .venv/bin/activate
   ```
   ```bash
   
   pip install -r requirements.txt

   **desactivar entorno virtual**
     deactivate
   ```  
   ```
## Uso

Para iniciar la API, ejecuta el siguiente comando:
```bash
python app.py
```

La API estará disponible en `http://localhost:5000`. si deseas usar un puerto diferente no hay problemas

## Contribuciones

Las contribuciones son bienvenidas. Si deseas colaborar, por favor abre un issue o envía un pull request.

