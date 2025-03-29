# API de Análisis de Incidencias - Seguridad Ciudadana

## Descripción

La API de Seguridad Ciudadana es un servicio web diseñado para proporcionar análisis y predicciones sobre incidencias de seguridad en la ciudad. Esta API se integra con un sistema web PHP (CodeIgniter) y proporciona funcionalidades de machine learning para el análisis de datos y generación de reportes.

## Funcionalidades

La API permite:

- **Entrenamiento de Modelos**:

  - Modelo de Regresión para predecir cantidad de incidencias
  - Modelo de Clasificación para predecir tipo de incidencias
  - Análisis de Componentes Principales (PCA) para reducción de dimensionalidad

- **Generación de Reportes**:

  - Reporte de Gráficas (reporte_graficas.pdf)
  - Reporte de Predicciones (reporte_predicciones.pdf)
  - Patrones por Barrio (patrones_barrios.pdf)
  - Patrones por Tipo (patrones_tipos.pdf)

- **Análisis de Datos**:
  - Distribución de incidentes por día, mes y hora
  - Análisis de patrones por barrio y tipo de incidencia
  - Matrices de correlación
  - Predicciones basadas en machine learning

## Requisitos

- Python 3.11.5
- Entorno virtual (venv)
- Librerías Python (ver requirements.txt):
  - Flask==3.0.3
  - pandas==2.2.3
  - joblib==1.4.2
  - scikit-learn==1.5.2
  - matplotlib==3.9.2
  - seaborn==0.13.2
  - flask-cors==5.0.0
  - gunicorn==23.0.0
  - requests==2.25.1
  - GitPython==3.1.24
  - numpy==1.26.4
  - python-dateutil==2.8.2
  - pytz==2024.1
  - six==1.16.0
  - typing-extensions==4.9.0

## Instalación

1. Navega al directorio del proyecto:

```bash
cd C:\xampp\htdocs\Seguridad_Ciudadana\ml_scripts
```

2. Crea y activa el entorno virtual:

```bash
python -m venv venv
.\venv\Scripts\activate
```

3. Instala las dependencias:

```bash
pip install -r requirements.txt
```

## Configuración

1. Asegúrate de que el servidor Flask esté configurado para escuchar en el puerto 5001:

```python
if __name__ == '__main__':
    app.run(debug=True, port=5001)
```

2. Verifica que CORS esté habilitado:

```python
from flask_cors import CORS
app = Flask(__name__)
CORS(app)
```

3. En el controlador PHP (Panel.php), la URL de la API debe apuntar a:

```php
$apiUrl = 'http://127.0.0.1:5001/entrenar_modelo';
```

## Uso

1. Activa el entorno virtual:

```bash
.\venv\Scripts\activate
```

2. Inicia el servidor Flask:

```bash
python app.py
```

3. La API estará disponible en `http://127.0.0.1:5001`

## Endpoints

### `/`

Proporciona información básica sobre la API y los endpoints disponibles.

### `/entrenar_modelo` (POST)

Recibe datos en formato JSON y:

- Entrena los modelos de machine learning
- Genera reportes PDF
- Devuelve predicciones

#### Datos esperados:

- **mes**: Mes del incidente (1-12)
- **dia**: Día del mes (1-31)
- **hora**: Hora del incidente (HH:MM)
- **cantidad**: Número de incidencias
- **tipo_incidencia**: Tipo de incidencia
- **barrio**: Barrio donde ocurrió la incidencia

### `/static/<filename>` (GET)

Permite descargar los archivos PDF generados.

## Estructura de Archivos

```
ml_scripts/
├── app.py              # Servidor Flask principal
├── requirements.txt    # Dependencias del proyecto
├── venv/              # Entorno virtual
├── modelo_regresion.pkl
├── modelo_clasificacion.pkl
├── modelo_pca.pkl
├── modelo_le.pkl
├── columnas.pkl
├── reporte_graficas.pdf
├── reporte_predicciones.pdf
├── patrones_barrios.pdf
└── patrones_tipos.pdf
```

## Notas Importantes

1. El servidor Flask debe estar corriendo para que el sistema PHP pueda comunicarse con la API.
2. Los archivos PDF generados se guardan en la carpeta `ml_scripts`.
3. Los modelos entrenados se guardan como archivos .pkl para su reutilización.
4. Asegúrate de tener los permisos necesarios en la carpeta `ml_scripts` para la escritura de archivos.

## Solución de Problemas

1. Si el puerto 5001 está ocupado:

   - Busca el proceso: `netstat -ano | findstr :5001`
   - Termina el proceso: `taskkill /PID <número_del_proceso> /F`

2. Si hay problemas de permisos:

   - Verifica los permisos de la carpeta `ml_scripts`
   - Asegúrate de que el usuario que ejecuta Flask tenga permisos de escritura

3. Si hay problemas de CORS:
   - Verifica que CORS esté habilitado en Flask
   - Asegúrate de que la URL en el controlador PHP sea correcta
