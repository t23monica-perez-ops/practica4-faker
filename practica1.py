import boto3
import pandas as pd
import json
import io

# 1. Configuración de cliente Boto3 para conexión con AWS S3
s3_client = boto3.client('s3', region_name='us-east-1')
BUCKET_NAME = 'webserver-m4-bucket-2026'

def load_and_profile_s3(file_key, is_json=False):
    """Descarga archivos desde S3 y genera un perfilamiento básico de tipos de datos."""
    print(f"=== Processing S3 Object: {file_key} ===")
    response = s3_client.get_object(Bucket=BUCKET_NAME, Key=file_key)
    body = response['Body'].read()
    
    if is_json:
        data_json = json.loads(body.decode('utf-8'))
        df = pd.json_normalize(data_json)
    else:
        df = pd.read_csv(io.BytesIO(body))
        
    print(f"Dataset Dimensions: {df.shape[0]} rows x {df.shape[1]} columns")
    print("\nData Type Profile & Identification:")
    print(df.dtypes)
    print("\nDescriptive Statistics Summary (Quantitative):")
    print(df.describe().T)
    return df

if __name__ == "__main__":
    # 1. Perfilamiento del CSV (Captura 1)
    df_transactions = load_and_profile_s3('raw/transacciones.csv')
    print("\n" + "="*60 + "\n")
    # 2. Perfilamiento del JSON (Captura 2)
    df_logs = load_and_profile_s3('raw/logs_m2m.json', is_json=True)
