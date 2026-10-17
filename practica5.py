import io
import pandas as pd
import boto3
from sklearn.preprocessing import MinMaxScaler

# 1. Configuración real con tu bucket de AWS S3
BUCKET_NAME = "webserver-m4-bucket-2026"
RAW_KEY = "raw/datos_clientes.csv"
PROCESSED_KEY = "processed/etl_output.parquet"
REGION = "us-east-1"


def extraer_datos_s3(s3_client, bucket, key) -> pd.DataFrame:
    """Fase 1: Extracción de datos desde la zona raw de S3 (o fallback sintético)."""
    print("=== 1. FASE DE EXTRACCIÓN (Extract) ===")
    try:
        response = s3_client.get_object(Bucket=bucket, Key=key)
        df_raw = pd.read_csv(io.BytesIO(response['Body'].read()))
        print(f"-> Éxito: Se extrajeron {len(df_raw)} registros desde s3://{bucket}/{key}")
        return df_raw
    except Exception as e:
        print(f"-> Nota: No se encontró 'raw/datos_clientes.csv' en S3 ({e}). Generando dataset inicial para prueba...")
        return pd.DataFrame({
            'cliente': ['Cliente_A', 'Cliente_B', 'Cliente_C', 'Cliente_D', 'Cliente_E'],
            'edad': [21, 45, 62, 29, 38],
            'monto_compras': [1200.0, 50000.0, 30000.0, 15000.0, 8500.0]
        })


def transformar_datos(df_raw: pd.DataFrame) -> pd.DataFrame:
    """Fase 2: Transformación, Discretización (Binning) y Normalización MinMaxScaler."""
    print("\n=== 2. FASE DE TRANSFORMACIÓN (Transform) ===")
    df_transform = df_raw.copy()

    # 1. Discretización / Binning de Edad
    df_transform['categoria_edad'] = pd.cut(
        df_transform['edad'],
        bins=[0, 25, 50, 100],
        labels=['Joven', 'Adulto', 'Senior']
    )

    # 2. Normalización Min-Max de monto_compras
    scaler = MinMaxScaler()
    df_transform['monto_normalizado'] = scaler.fit_transform(df_transform[['monto_compras']])

    # 3. Ingeniería de Características (Feature Engineering)
    df_transform['score_promocional'] = df_transform['monto_normalizado'] * 100

    print("Dataset Transformado:")
    print(df_transform)
    return df_transform


def cargar_datos_s3(s3_client, df_processed: pd.DataFrame, bucket, key):
    """Fase 3: Serialización a Parquet en memoria (io.BytesIO) y carga en AWS S3."""
    print("\n=== 3. FASE DE CARGA (Load) ===")
    
    # Serialización en memoria binaria mediante io.BytesIO()
    buffer = io.BytesIO()
    df_processed.to_parquet(buffer, index=False, engine='pyarrow')
    buffer.seek(0)

    # Carga efectiva del objeto a AWS S3
    s3_client.put_object(
        Bucket=bucket,
        Key=key,
        Body=buffer.getvalue(),
        ContentType='application/x-parquet'
    )
    print(f"-> Éxito: Archivo Parquet comprimido cargado correctamente en la zona 'processed' de S3 (s3://{bucket}/{key}).")


def pipeline_etl_completo():
    """Coordinador principal de la ejecución ETL."""
    s3_client = boto3.client('s3', region_name=REGION)
    
    df_raw = extraer_datos_s3(s3_client, BUCKET_NAME, RAW_KEY)
    df_processed = transformar_datos(df_raw)
    cargar_datos_s3(s3_client, df_processed, BUCKET_NAME, PROCESSED_KEY)


if __name__ == "__main__":
    pipeline_etl_completo()