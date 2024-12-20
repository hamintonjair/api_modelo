
# Importaciones estándar de Python
import json
import os
import sys
import warnings

# Importaciones de terceros
import joblib
import matplotlib
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
from sklearn.decomposition import PCA
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from matplotlib.backends.backend_pdf import PdfPages
# import requests
import base64

matplotlib.use('Agg') 
app = Flask(__name__)
CORS(app)

# Definir variables de entorno y rutas
base_path = os.path.dirname(__file__)  # Ruta base del proyecto en Render o local
# storage_path = '../storage'  # Ruta de almacenamiento
base_path_two = os.getcwd()
storage_path = os.path.join(base_path_two, 'static', 'pdfs')
storage_path_models = os.path.join(base_path_two, 'static', 'pdfs')   # Ruta de almacenamiento

# Configuración del entorno

pdf_name1 = 'pdf_reporte_graficas.pdf'  # Nombre del primer PDF
pdf_name2 = 'pdf_predictions.pdf'  # Nombre del segundo PDF
pdf_path1 = os.path.join(storage_path, pdf_name1)  # Ruta completa al primer archivo PDF
pdf_path2 = os.path.join(storage_path, pdf_name2)  # Ruta completa al segundo archivo PDF
branch_name = 'main'  # Rama a la que quieres subir el archivo
download_urls = {
    # pdf_name2: "https://apimodelo.yoyler.dev/static/pdfs/" + pdf_name2
     pdf_name1: storage_path+ "/" + pdf_name1,
     pdf_name2: storage_path + "/" + pdf_name2
}

if not os.path.exists(storage_path):
    os.makedirs(storage_path)



@app.route('/')
def home():
    return jsonify({
        "mensaje": "Bienvenido a la API de análisis de incidencias",
        "endpoints": {
            "/entrenar_modelo": "Entrena el modelo con los datos actuales",
            "/predicciones": "Genera predicciones basadas en el modelo entrenado"
        },
        "descripcion": "Esta API permite entrenar un modelo de machine learning con datos de incidencias y generar predicciones basadas en ese modelo."
    })

@app.route('/static/<path:filename>', methods=['GET'])
def serve_static_file(filename):
    return send_from_directory('static', filename, as_attachment=True)
@app.route('/entrenar_modelo', methods=['POST'])
def entrenar_modelo():

    data = pd.DataFrame(request.get_json())
    print(type(data))
    print(data)


    # Convertir columnas 'mes' y 'dia' a numéricas
    data['mes'] = pd.to_numeric(data['mes'], errors='coerce')
    data['dia'] = pd.to_numeric(data['dia'], errors='coerce')

    # Extraer la hora y los minutos desde la columna original
    data['hora_original'] = data['hora']
    data['hora'] = data['hora_original'].str.split(':').str[0].astype(int)    # Extraer la hora como entero
    data['minutos'] = data['hora_original'].str.split(':').str[1].astype(int) # Extraer los minutos como entero

    # Unificar hora y minutos en una sola columna con formato entero HHMM
    data['hora_unificada'] = data['hora'] * 100 + data['minutos']

    # Definir la función para clasificar la hora unificada
    def clasificar_hora(hora_unificada):
        if 0 <= hora_unificada < 600:
            return 'Madrugada'
        elif 600 <= hora_unificada < 1200:
            return 'Mañana'
        elif 1200 <= hora_unificada < 1800:
            return 'Tarde'
        else:
            return 'Noche'

    # Aplicar la clasificación a la columna 'hora_unificada'
    data['intervalo_hora'] = data['hora_unificada'].apply(clasificar_hora)

    # Crear columna de fin de semana
    data['es_fin_de_semana'] = data['dia'].apply(lambda x: 1 if x in [6, 7] else 0)

    # Selección de características para los modelos
    X = data[['mes', 'intervalo_hora', 'es_fin_de_semana']]
    y_cantidad = data['cantidad']  # Variable de salida para regresión
    y_tipo = data['tipo_incidencia']  # Variable de salida para clasificación

    # Convertir las categorías en variables dummies
    X = pd.get_dummies(X, columns=['intervalo_hora'], drop_first=True)

    # Convertir 'tipo_incidencia' a números
    le = LabelEncoder()
    y_tipo = le.fit_transform(y_tipo)

    # Guardar las columnas para la predicción
    columnas = X.columns

    # Dividir los datos en conjuntos de entrenamiento y prueba
    X_train, X_test, y_train, y_test = train_test_split(X, y_cantidad, test_size=0.2, random_state=42)
    X_train_clf, X_test_clf, y_train_clf, y_test_clf = train_test_split(X, y_tipo, test_size=0.2, random_state=42)

    # Aplicar PCA para reducción de dimensionalidad
    pca = PCA(n_components=2)
    X_train_pca = pca.fit_transform(X_train)
    X_test_pca = pca.transform(X_test)

    # Entrenamiento de modelos
    model_regresion = LinearRegression()
    model_regresion.fit(X_train_pca, y_train)

    model_clasificacion = RandomForestClassifier()
    model_clasificacion.fit(X_train, y_train_clf)

    # Guardar los modelos y PCA
    guardar_modelos(model_regresion, model_clasificacion, pca, le, X.columns)

    # Llamar a la función de predicción después de entrenar
    resultprediciones = predicciones(data)
    return resultprediciones

def guardar_modelos(model_regresion, model_clasificacion, pca, le, columnas):
    # Guardar los modelos en la carpeta de almacenamiento
    joblib.dump(model_regresion, os.path.join(base_path, 'modelo_regresion.pkl'))
    joblib.dump(model_clasificacion, os.path.join(base_path, 'modelo_clasificacion.pkl'))
    joblib.dump(pca, os.path.join(base_path, 'modelo_pca.pkl'))
    joblib.dump(le, os.path.join(base_path, 'modelo_le.pkl'))
    joblib.dump(columnas, os.path.join(base_path, 'columnas.pkl'))

    return jsonify({"mensaje": "Modelos entrenados y guardados en la carpeta de almacenamiento exitosamente."})

#se obtienes las predicciones basado a los datos de la clasificacion
def predicciones(data):
    # # Cargar los modelos
    warnings.filterwarnings("ignore", message="X has feature names, but LinearRegression was fitted without feature names")
    print("data recibida desde el metodo principal", data)
    # Cargar los datos desde el archivo JSON

    # Convertir el JSON en un DataFrame de pandas
    df = pd.DataFrame(data)
    # df = data
    print(df["mes"])

    # Asegúrate de que los datos están en el formato correcto
    df['mes'] = pd.to_numeric(df['mes'], errors='coerce')

    print(df.dtypes)

    # Unificar hora y minutos en una sola columna con formato entero HHMM
    df['hora_unificada'] = df['hora'] * 100 + df['minutos']



    # Definir la función para clasificar la hora unificada
    def clasificar_hora(hora_unificada):
        if 0 <= hora_unificada < 600:
            return '00:00-06:00'
        elif 600 <= hora_unificada < 1200:
            return '06:00-12:00'
        elif 1200 <= hora_unificada < 1800:
            return '12:00-18:00'
        else:
            return '18:00-24:00'

    # Aplicar la función de clasificación a la columna unificada
    df['intervalo_hora'] = df['hora_unificada'].apply(clasificar_hora)

    # Crear la columna 'es_fin_de_semana'
    df['es_fin_de_semana'] = df['dia'].apply(lambda x: 1 if x in [6, 7] else 0)

     # Crear el archivo PDF de cada gráfica
    with PdfPages(pdf_path1) as pdf:
        # Explicación general del aprendizaje aplicado
        plt.figure(figsize=(12, 6))
        plt.text(0.05, 0.5, 
                 'Tipo de Aprendizaje Aplicado:\n\n'
                 '1. Aprendizaje Supervisado: Se utilizan modelos de aprendizaje supervisado para hacer\n'
                 ' predicciones sobre los incidentes, basados en datos históricos etiquetados.\n'
                 '   - Modelo de Regresión: Se usa para predecir la cantidad de incidentes en \n'
                 ' función de las características de los datos.\n'
                 '   - Modelo de Clasificación: Se utiliza para predecir el tipo de incidencia que se \n'
                 ' espera en función de las características de los datos.\n\n'
                 '2. Análisis de Componentes Principales (PCA): Se aplica PCA para reducir la\n'
                 ' dimensionalidad de los datos y mejorar la eficiencia de los modelos.\n'
                 '   - PCA transforma los datos en componentes principales que capturan la mayor\n'
                 ' varianza posible con menos variables.\n\n'
                 'Cada gráfico en este informe proporciona una visión de diferentes aspectos \n'
                 ' del análisis de datos de incidentes.\n', 
                 ha='left', va='center', fontsize=14)
        
        plt.axis('off')
        pdf.savefig()
        plt.close()

        # Primer gráfico
        plt.figure(figsize=(12, 6))
        plt.text(0.05, 0.5, 
                'Explicación de las Predicciones:\n\n'
                'Las predicciones generadas por los modelos de aprendizaje supervisado son fundamentales\n'
                'para la toma de decisiones en el análisis de incidentes. La elección de estos modelos se\n'
                'basó en su capacidad para manejar grandes volúmenes de datos y extraer patrones significativos.\n\n'
                '   - Modelo de Regresión: Este modelo permite estimar la cantidad esperada de incidentes\n'
                '     en función de variables predictivas, facilitando la planificación y gestión de recursos.\n\n'
                '   - Modelo de Clasificación: Ayuda a categorizar los incidentes en tipos específicos,\n'
                '     lo que es crucial para priorizar las acciones y estrategias de respuesta según el tipo de\n'
                '     incidencia más probable.\n\n'
                'El uso de PCA contribuye a simplificar el análisis al reducir la complejidad del modelo sin\n'
                'perder la capacidad de capturar las características más relevantes de los datos.\n', 
                ha='left', va='center', fontsize=14)
        plt.axis('off')
        pdf.savefig()
        plt.close()

        # Segundo gráfico
        plt.figure(figsize=(10, 6))
        sns.countplot(data=df, x='dia')
        plt.title('Distribución de Incidentes por Día de la Semana')
        plt.xlabel('Día de la Semana')
        plt.ylabel('Número de Incidentes')
        plt.subplots_adjust(bottom=0.30)  # Ajustar el margen inferior
        plt.text(0.5, -0.3, 'Este gráfico muestra la distribución de incidentes a lo largo de los días de la semana.', 
                 ha='center', va='center', transform=plt.gca().transAxes, fontsize=12)
        pdf.savefig()
        plt.close()

        plt.figure(figsize=(10, 6))
        sns.countplot(data=df, x='mes')
        plt.title('Distribución de Incidentes por Mes')
        plt.xlabel('Mes')
        plt.ylabel('Número de Incidentes')
        plt.subplots_adjust(bottom=0.30)  # Ajustar el margen inferior
        plt.text(0.5, -0.3, 'Este gráfico muestra el número de incidentes registrados en cada mes del año.', 
                 ha='center', va='center', transform=plt.gca().transAxes, fontsize=12)
        pdf.savefig()
        plt.close()

        # Tercer gráfico
        plt.figure(figsize=(10, 6))
        sns.countplot(data=df, x='intervalo_hora')
        plt.title('Distribución de Incidentes por Intervalo de Hora')
        plt.xlabel('Intervalo de Hora')
        plt.ylabel('Número de Incidentes')
        plt.subplots_adjust(bottom=0.30)  # Ajustar el margen inferior
        plt.text(0.5, -0.3, 'Este gráfico muestra la cantidad de incidentes distribuidos en diferentes intervalos horarios del día.', 
                 ha='center', va='center', transform=plt.gca().transAxes, fontsize=12)
        pdf.savefig()
        plt.close()

        # Cuarto gráfico
        plt.figure(figsize=(12, 7))
        sns.countplot(data=df, x='barrio', order=df['barrio'].value_counts().index)
        plt.title('Distribución de Incidentes por Barrio')
        plt.xlabel('Barrios')
        plt.ylabel('Número de Incidentes')
        plt.xticks(rotation=90)
        plt.subplots_adjust(bottom=0.45)  # Ajustar el margen inferior
        plt.text(0.5, -0.7, 'Este gráfico muestra la cantidad de incidentes por barrio, ordenados de mayor a menor.', 
                 ha='center', va='center', transform=plt.gca().transAxes, fontsize=12)
        pdf.savefig()
        plt.close()

        # Quinto gráfico
        plt.figure(figsize=(10, 6))
        sns.countplot(data=df, x='tipo_incidencia')
        plt.title('Distribución de Incidentes por Tipo de Incidencia')
        plt.xlabel('Tipo de Incidencias')
        plt.ylabel('Número de Incidentes')
        plt.xticks(rotation=90)
        plt.subplots_adjust(bottom=0.47)  # Ajustar el margen inferior
        plt.text(0.5, -0.8, 'Este gráfico muestra la distribución de incidentes según el tipo de incidencia.', 
                 ha='center', va='center', transform=plt.gca().transAxes, fontsize=12)
        pdf.savefig()
        plt.close()

        # Sexto gráfico
        plt.figure(figsize=(12, 8))
        heatmap_data = df.groupby(['dia', 'intervalo_hora']).size().unstack()
        sns.heatmap(heatmap_data, cmap='YlGnBu', annot=True)
        plt.title('Número de Incidentes por Día y Intervalo de Hora')
        plt.xlabel('Intervalo de Hora')
        plt.ylabel('Día de la Semana')
        plt.subplots_adjust(bottom=0.4)  # Ajustar el margen inferior
        plt.text(0.5, -0.3, 'Este gráfico muestra la cantidad de incidentes distribuidos por día de la semana y por intervalo horario.', 
                 ha='center', va='center', transform=plt.gca().transAxes, fontsize=12)
        pdf.savefig()
        plt.close()

        # Séptimo gráfico
        plt.figure(figsize=(10, 6))
        correlation_matrix = df[['mes', 'hora', 'es_fin_de_semana']].corr()
        sns.heatmap(correlation_matrix, annot=True, cmap='coolwarm', fmt='.2f')
        plt.title('Matriz de Correlación')
        plt.subplots_adjust(bottom=0.4)  # Ajustar el margen inferior
        plt.text(0.5, -0.3, 'Este gráfico muestra la matriz de correlación entre las variables mes, hora y si es fin de semana.', 
                 ha='center', va='center', transform=plt.gca().transAxes, fontsize=12)
        pdf.savefig()
        plt.close()

    # Cargar modelos y PCA
    try:
        
        model_regresion = joblib.load(os.path.join(base_path, 'modelo_regresion.pkl'))
        model_clasificacion = joblib.load(os.path.join(base_path, 'modelo_clasificacion.pkl'))
        pca = joblib.load(os.path.join(base_path, 'modelo_pca.pkl'))
        le = joblib.load(os.path.join(base_path, 'modelo_le.pkl'))
        columnas = joblib.load(os.path.join(base_path, 'columnas.pkl'))
    except FileNotFoundError as e:
        print("Modelo no encontrado:", e)
        sys.exit(1)

    # Preparación de los datos de entrada para la predicción
    X_nueva = df[['mes', 'hora', 'intervalo_hora', 'es_fin_de_semana']]
    X_nueva = pd.get_dummies(X_nueva, columns=['intervalo_hora'], drop_first=True)

    # Asegúrate de que las columnas coincidan con las del entrenamiento
    X_nueva = X_nueva.reindex(columns=columnas, fill_value=0)

    # Aplicar PCA a los datos
    X_nueva_pca = pca.transform(X_nueva)

    # Predicciones
    df['cantidad_pred'] = model_regresion.predict(X_nueva_pca)
    df['tipo_incidencia_pred'] = le.inverse_transform(model_clasificacion.predict(X_nueva))

    # Guardar los resultados en un archivo CSV
    resultados_csv_path = os.path.join(base_path, 'resultados_predicciones.csv')
    guardar_resultados(df,resultados_csv_path)

   
	# *****************************************************************************************
	# Mostrar resultados
    print(df[['cantidad_pred', 'tipo_incidencia_pred']].head())

	# Crear el archivo PDF de cada gráfica
    with PdfPages(pdf_path2) as pdf:
        plt.figure(figsize=(10, 6))
        df_baras = df.groupby('es_fin_de_semana').sum().reset_index()
        sns.barplot(data=df_baras, x='es_fin_de_semana', y='cantidad_pred', hue='es_fin_de_semana', palette='viridis', dodge=False, legend=False)
        plt.title('Cantidad Predicha en Fin de Semana vs. Días Laborales')
        plt.xlabel('Es Fin de Semana')
        plt.ylabel('Cantidad Predicha')
        plt.xticks(ticks=[0, 1], labels=['Día Laboral', 'Fin de Semana'])
        plt.subplots_adjust(bottom=0.35)
        plt.text(0.5, -0.3, 'Este gráfico muestra la cantidad total de incidencias predicha para días laborales y fines de semana.', 
             ha='center', va='center', transform=plt.gca().transAxes, fontsize=12)
        plt.grid(True)
        pdf.savefig()
        plt.close()
        
        plt.figure(figsize=(10, 6))
        df_baras = df.groupby('intervalo_hora').sum().reset_index()
        sns.barplot(data=df_baras, x='intervalo_hora', y='cantidad_pred', hue='intervalo_hora', palette='mako', dodge=False, legend=False)
        plt.title('Cantidad Predicha por Intervalo Horario')
        plt.xlabel('Intervalo Horario')
        plt.ylabel('Cantidad Predicha')
        plt.xticks(rotation=45)
        plt.subplots_adjust(bottom=0.40)
        plt.text(0.5, -0.6, 'Este gráfico muestra la cantidad total de incidencias predicha para cada intervalo horario.', 
             ha='center', va='center', transform=plt.gca().transAxes, fontsize=12)
        plt.grid(True)
        pdf.savefig()
        plt.close()
        
        plt.figure(figsize=(10, 6))
        df_baras = df.groupby('barrio').sum().reset_index()
        sns.barplot(data=df_baras, x='barrio', y='cantidad_pred', hue='barrio', palette='cubehelix', dodge=False, legend=False)
        plt.title('Cantidad Predicha por Barrio')
        plt.xlabel('Barrio')
        plt.ylabel('Cantidad Predicha')
        plt.xticks(rotation=90)
        plt.subplots_adjust(bottom=0.45)
        plt.text(0.5, -10, 'Este gráfico muestra la cantidad total de incidencias predicha para cada barrio.', 
             ha='center', va='center', transform=plt.gca().transAxes, fontsize=12)
        plt.grid(True)
        pdf.savefig()
        plt.close()
        
        plt.figure(figsize=(10, 6))
        df_baras = df.groupby('tipo_incidencia').sum().reset_index()
        sns.barplot(data=df_baras, x='tipo_incidencia', y='cantidad_pred', hue='tipo_incidencia', palette='coolwarm', dodge=False, legend=False)
        plt.title('Cantidad Predicha por Tipo de Incidencia')
        plt.xlabel('Tipo de Incidencia')
        plt.ylabel('Cantidad Predicha')
        plt.xticks(rotation=90)
        plt.subplots_adjust(bottom=0.45)
        plt.text(0.5, -10, 'Este gráfico muestra la cantidad total de incidencias predicha para cada tipo de incidencia.', 
             ha='center', va='center', transform=plt.gca().transAxes, fontsize=12)
        plt.grid(True)
        pdf.savefig()
        plt.close()
                
    datos = {
            "pdf1_url": download_urls.get(pdf_name1),
            "pdf2_url": download_urls.get(pdf_name2),
            # "otros_datos": data
        }
    return jsonify({"mensaje": "Modelo entrenado y PDFs generados y subidos exitosamente.", "datos": datos})


# Función para guardar el archivo de resultados y subirlo a GitHub
def guardar_resultados(df,resultados_csv_path):
    # Guardar los resultados en un archivo CSV local
    df.to_csv(resultados_csv_path, index=False)

    df.to_csv(resultados_csv_path, index=False)
    print(f"Predicciones guardadas en {resultados_csv_path}")

    # Leer el archivo CSV
    df_resultados = pd.read_csv(resultados_csv_path)
    # Análisis de patrones por barrio
    patrones_barrios = df.groupby('barrio').agg({
        'cantidad': 'sum',                  # Total de incidencias por barrio
        'cantidad_pred': 'mean',     # Promedio de la predicción de regresión por barrio
    }).reset_index()

    # Calcular la moda de la predicción de clasificación para cada barrio
    patrones_barrios['prediccion_clasificacion_mode'] = df.groupby('barrio')['tipo_incidencia_pred'].agg(pd.Series.mode).reset_index(drop=True)

    # Analizar patrones por tipo de incidencia
    patrones_tipos = df.groupby('tipo_incidencia').agg({
        'cantidad': 'sum',                  # Total de incidencias por tipo
        'cantidad_pred': 'mean',     # Promedio de la predicción de regresión por tipo
    }).reset_index()

    # Calcular la moda de la predicción de clasificación para cada tipo de incidencia
    patrones_tipos['prediccion_clasificacion_mode'] = df_resultados.groupby('tipo_incidencia')['tipo_incidencia_pred'].agg(pd.Series.mode).reset_index(drop=True)

	# Mostrar los patrones encontrados
    print("Patrones por barrio:")
    print(patrones_barrios)

    print("\nPatrones por tipo de incidencia:")
    print(patrones_tipos)

	# Guardar los resultados en archivos CSV para su posterior análisis
    guardar_patrones_csv(patrones_barrios, patrones_tipos)
    
    return jsonify({"mensaje": "Archivo de resultados guardado y subido a GitHub exitosamente."})

# Función para guardar los archivos CSV y subirlos a GitHub
def guardar_patrones_csv(patrones_barrios, patrones_tipos):
    # Guardar los resultados en archivos CSV para su posterior análisis
    patrones_barrios_csv_path = os.path.join(base_path, 'patrones_barrios.csv')
    patrones_tipos_csv_path = os.path.join(base_path, 'patrones_tipos.csv')

    # Guardar los datos en archivos CSV locales
    patrones_barrios.to_csv(patrones_barrios_csv_path, index=False)
    patrones_tipos.to_csv(patrones_tipos_csv_path, index=False)

    return jsonify({"mensaje": "Archivos de patrones guardados y subidos a GitHub exitosamente."})

if __name__ == '__main__':
    port = int(os.environ.get("PORT", default=5000))  # Usa el puerto de Render o 5000 por defecto
    app.run(debug=True,host='0.0.0.0', port=port)
