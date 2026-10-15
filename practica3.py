import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.impute import KNNImputer, SimpleImputer
import boto3
import io

# Configuración de estilo gráfico
sns.set_theme(style="whitegrid")

# -------------------------------------------------------------
# 1. Generación de Dataset Ruidoso (Raw Data)
# -------------------------------------------------------------
data = {
    'edad': [25, 30, np.nan, 45, 22, 120, 35, 28, np.nan, 40], # 120: Valor erróneo
    'ingreso_mensual': [15000, 22000, 18000, np.nan, 12000, 950000, 25000, 21000, 19000, np.nan], # 950k: Outlier
    'scoring_credito': [650, 700, 680, 710, 590, 800, 670, 640, 620, 730]
}
df_dirty = pd.DataFrame(data)

# -------------------------------------------------------------
# 2. Generación de Gráficos (Boxplots)
# -------------------------------------------------------------
plt.figure(figsize=(10, 4))
plt.subplot(1, 2, 1)
sns.boxplot(y=df_dirty['ingreso_mensual'], color='salmon')
plt.title("Ingreso Mensual (Con Outlier 950k)")

plt.subplot(1, 2, 2)
sns.boxplot(y=df_dirty['edad'], color='orange')
plt.title("Edad (Con Error 120)")
plt.tight_layout()
plt.savefig("boxplot_antes.png", dpi=300)
plt.close()

# -------------------------------------------------------------
# 3. Detección y Tratamiento Estadístico (IQR)
# -------------------------------------------------------------
Q1 = df_dirty['ingreso_mensual'].quantile(0.25)
Q3 = df_dirty['ingreso_mensual'].quantile(0.75)
IQR = Q3 - Q1
limite_superior = Q3 + 1.5 * IQR

df_treated = df_dirty.copy()
df_treated.loc[df_treated['ingreso_mensual'] > limite_superior, 'ingreso_mensual'] = np.nan
df_treated.loc[df_treated['edad'] > 100, 'edad'] = np.nan

# -------------------------------------------------------------
# 4. Imputación Múltiple con KNNImputer (k=2)
# -------------------------------------------------------------
imputer = KNNImputer(n_neighbors=2)
df_clean_array = imputer.fit_transform(df_treated)
df_clean = pd.DataFrame(df_clean_array, columns=df_dirty.columns)

print("=== DATASET LIMPIO E IMPUTADO FINAL ===")
print(df_clean)

# -------------------------------------------------------------
# 5. Función para Exportar Directorio / Archivos a AWS S3
# -------------------------------------------------------------
def subir_a_s3(df, bucket_name, object_name):
    s3_client = boto3.client('s3')
    csv_buffer = io.StringIO()
    df.to_csv(csv_buffer, index=False)
    s3_client.put_object(Bucket=bucket_name, Key=object_name, Body=csv_buffer.getvalue())
    print(f"✅ Archivo subido con éxito a AWS S3: s3://{bucket_name}/{object_name}")

BUCKET_NAME = 'webserver-m4-bucket-2026'

if __name__ == "__main__":
    print("\n=== EXPORTANDO RESULTADOS A AWS S3 ===")
    try:
        # Subir CSV de datos limpios a la carpeta 'cleaned/'
        subir_a_s3(df_clean, BUCKET_NAME, 'cleaned/df_clean_knn.csv')
        
        # Subir imagen de la gráfica a la carpeta 'cleaned/reports/'
        s3 = boto3.client('s3')
        s3.upload_file('boxplot_antes.png', BUCKET_NAME, 'cleaned/reports/boxplot_antes.png')
        print(f"✅ Gráfica subida con éxito a AWS S3: s3://{BUCKET_NAME}/cleaned/reports/boxplot_antes.png")
        
        print("\n🚀 ¡Estructura de carpetas actualizada correctamente en AWS S3!")
    except Exception as e:
        print(f"⚠️ Error al conectar o subir a AWS S3: {e}")