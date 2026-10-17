import pandas as pd
import numpy as np
from faker import Faker
from sklearn.model_selection import train_test_split

# 1. Configuración de Faker con localización de México y semillas aleatorias
fake = Faker('es_MX')
Faker.seed(42)
np.random.seed(42)

# 2. Generación programática de 1,000 registros sintéticos
registros = []
for i in range(1000):
    registros.append({
        'id_cliente': i + 1,
        'nombre': fake.name(),
        'email': fake.email(),
        # Campos adicionales requeridos
        'telefono': fake.phone_number(),
        'fecha_nacimiento': fake.date_of_birth(minimum_age=18, maximum_age=70),
        'estado_civil': np.random.choice(['Soltero', 'Casado', 'Divorciado'], p=[0.5, 0.4, 0.1]),
        'ingreso_anual': round(np.random.uniform(100000, 1000000), 2),
        'churn': np.random.choice([0, 1], p=[0.8, 0.2])  # 20% tasa de abandono
    })

df_sintetico = pd.DataFrame(registros)

# 3. Codificación de variables categóricas (estado_civil)
df_encoded = pd.get_dummies(df_sintetico, columns=['estado_civil'], drop_first=True, dtype=int)

# 4. Selección de Features (X) y Target (y)
# Excluimos identificadores/datos PII irrelevantes y la variable objetivo
X = df_encoded.drop(columns=['id_cliente', 'nombre', 'email', 'telefono', 'fecha_nacimiento', 'churn'])
y = df_encoded['churn']

# 5. Partición Estratificada (Train 80%, Test 20%)
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.20, random_state=42, stratify=y
)

# 6. Despliegue de resultados para el análisis
print("\n" + "=" * 60)
print(" RESULTADOS DEL MUESTREO ESTRATIFICADO")
print("=" * 60)
print(f"Dataset Completo | Total: {len(df_sintetico)} | Proporción Churn: {y.mean():.4f} ({y.mean()*100:.2f}%)")
print(f"Conjunto Train   | Formato: {X_train.shape} | Proporción Churn: {y_train.mean():.4f} ({y_train.mean()*100:.2f}%)")
print(f"Conjunto Test    | Formato: {X_test.shape}  | Proporción Churn: {y_test.mean():.4f} ({y_test.mean()*100:.2f}%)")
print("=" * 60 + "\n")

# Muestra de las primeras filas del DataFrame procesado
print("Muestra de datos de entrenamiento (X_train):")
print(X_train.head())