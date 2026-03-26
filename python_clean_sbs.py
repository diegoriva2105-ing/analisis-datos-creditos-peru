import pandas as pd
from sqlalchemy import create_engine
import os

"""
Script de limpieza y carga de datos del sistema financiero.

Este script realiza:
- Limpieza y transformación de datos
- Validación de calidad
- Carga a SQL Server

Requisitos:
- Python 3.x
- pandas
- sqlalchemy
- pyodbc

Configuración:
Definir variables de entorno:
- DB_SERVER
- DB_NAME
"""

# =========================
# CARGA DE DATOS
# =========================

df = pd.read_csv(
    "Reporte(01-2001 - 09-2022).csv",
    encoding="latin-1",
    sep=";"
)

# =========================
# VALIDACIÓN INICIAL
# =========================

print('Valores nulos por columna:')
print(df.isna().sum())

print('Duplicados encontrados:', df.duplicated().sum())

# =========================
# LIMPIEZA DE COLUMNAS
# =========================

df.columns = (
    df.columns
        .str.strip()
        .str.replace(' ', '_', regex=False)
        .str.replace('(', '', regex=False)
        .str.replace(')', '', regex=False)
        .str.replace('%', 'pct', regex=False)
        .str.replace('/', '', regex=False)
)

# =========================
# TRANSFORMACIONES
# =========================

df['Fecha'] = pd.to_datetime(df['Fecha'], dayfirst=True, errors='coerce')

df = df.dropna(subset=['Fecha'])
df = df.drop_duplicates()

df = df.sort_values('Fecha').reset_index(drop=True)

df = df.rename(columns={
    "Entidad": "entidad",
    "Fecha": "fecha",
    "Créditos_Consumo_Miles_de_S": "creditos_consumo",
    "Créditos_Hipotecarios_Miles_de_S": "creditos_hipotecarios",
    "Créditos_Corporativos_Miles_de_S": "creditos_corporativos",
    "Créditos_Medianas_Empresas_Miles_de_S": "creditos_medianas",
    "Créditos_Pequeñas_Empresas_Miles_de_S": "creditos_pequenas",
    "Créditos_Microempresas_Miles_de_S": "creditos_microempresas",
    "Créditos_Vigentes_Miles_de_S": "creditos_vigentes",
    "Créditos_Vencidos_Miles_de_S": "creditos_vencidos",
    "Ratio_de_Capital_Global_pct": "ratio_capital_global",
    "Morosidad_pct": "morosidad",
    "ROE_pct": "roe",
    "ROA_pct": "roa"
})

columnas_numericas = [
    "creditos_consumo",
    "creditos_hipotecarios",
    "creditos_corporativos",
    "creditos_medianas",
    "creditos_pequenas",
    "creditos_microempresas",
    "creditos_vigentes",
    "creditos_vencidos",
    "ratio_capital_global",
    "morosidad",
    "roe",
    "roa"
]

for col in columnas_numericas:
    df[col] = pd.to_numeric(df[col], errors='coerce')

# =========================
# VALIDACIÓN FINAL
# =========================

print('Filas finales:', df.shape[0])
print('Columnas finales:', df.shape[1])

# =========================
# CONEXIÓN A BASE DE DATOS
# =========================

server = os.getenv("DB_SERVER")
database = os.getenv("DB_NAME")

if not server or not database:
    raise ValueError("Ingresar los datos DB_SERVER y DB_NAME")

engine = create_engine(
    f"mssql+pyodbc://@{server}/{database}?driver=ODBC+Driver+17+for+SQL+Server&trusted_connection=yes"
)

# =========================
# CARGA DE DATOS
# =========================

try:
    df.to_sql(
        "creditos_sbs",
        engine,
        if_exists="replace",
        index=False,
        chunksize=1000
    )
    print("Datos cargados correctamente a SQL Server")

except Exception as e:
    print("Error al cargar datos:", e)