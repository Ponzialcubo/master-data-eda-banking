# ============================================================
# DataProject: EDA — Campañas de Marketing Bancario
# Máster en Análisis de Datos — Módulo 3: Librerías Python
# Herramientas: Python, Pandas, Matplotlib, Seaborn
# ============================================================

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import seaborn as sns
import warnings

warnings.filterwarnings("ignore")
sns.set_theme(style="whitegrid")

# ============================================================
# 1. CARGA DE DATOS
# ============================================================

# Dataset principal: campañas de marketing bancario
bank = pd.read_csv("bank-additional.csv", sep=",")

# Dataset secundario: detalles de clientes (ingresos, hijos, visitas web)
customers = pd.read_excel("customer-details.xlsx")

print("=== bank-additional.csv ===")
print(f"Filas: {bank.shape[0]} | Columnas: {bank.shape[1]}")
print(bank.head(3))

print("\n=== customer-details.xlsx ===")
print(f"Filas: {customers.shape[0]} | Columnas: {customers.shape[1]}")
print(customers.head(3))

# ============================================================
# 2. TRANSFORMACIÓN Y LIMPIEZA DE DATOS
# ============================================================

# --- 2.1 Unión de datasets por ID ---
# bank usa 'id_', customers usa 'ID'
df = pd.merge(bank, customers, left_on="id_", right_on="ID", how="left")
df.drop(columns=["Unnamed: 0_x", "Unnamed: 0_y", "ID"], inplace=True)
print(f"\nDataset unificado: {df.shape[0]} filas, {df.shape[1]} columnas")

# --- 2.2 Revisión de tipos y conversión ---
# Columnas numéricas que llegaron como string por usar coma decimal
for col in ["cons.price.idx", "cons.conf.idx", "euribor3m", "nr.employed"]:
    if df[col].dtype == object:
        df[col] = df[col].astype(str).str.replace(",", ".").str.strip()
        df[col] = pd.to_numeric(df[col], errors="coerce")

# Columna date a datetime
df["date"] = pd.to_datetime(df["date"], dayfirst=False, errors="coerce")

# Variable objetivo: y → binaria (1/0)
df["y_bin"] = (df["y"] == "yes").astype(int)

print("\nTipos tras conversión:")
print(df.dtypes)

# --- 2.3 Valores nulos ---
print("\nValores nulos por columna:")
nulls = df.isnull().sum()
print(nulls[nulls > 0])

# Imputación: age con mediana, job/education/marital con moda
df["age"] = df["age"].fillna(df["age"].median())
df["job"] = df["job"].fillna(df["job"].mode()[0])
df["marital"] = df["marital"].fillna(df["marital"].mode()[0])
df["education"] = df["education"].fillna(df["education"].mode()[0])

# default, housing, loan: imputar con 0 (sin historial conocido)
for col in ["default", "housing", "loan"]:
    df[col] = df[col].fillna(0)

# Variables numéricas económicas: mediana
for col in ["euribor3m", "cons.price.idx"]:
    df[col] = df[col].fillna(df[col].median())

# Income del dataset de clientes: mediana
df["Income"] = df["Income"].fillna(df["Income"].median())

print("\nNulos restantes:", df.isnull().sum().sum())

# --- 2.4 Estandarización de texto ---
df["job"] = df["job"].str.lower().str.strip()
df["marital"] = df["marital"].str.lower().str.strip()
df["education"] = df["education"].str.lower().str.strip()
df["poutcome"] = df["poutcome"].str.upper().str.strip()
df["contact"] = df["contact"].str.lower().str.strip()

# --- 2.5 Eliminar duplicados ---
n_dup = df.duplicated().sum()
print(f"\nDuplicados eliminados: {n_dup}")
df.drop_duplicates(inplace=True)
df.reset_index(drop=True, inplace=True)

print(f"\nDataset limpio final: {df.shape[0]} filas, {df.shape[1]} columnas")

# ============================================================
# 3. ANÁLISIS DESCRIPTIVO
# ============================================================

print("\n=== ESTADÍSTICAS DESCRIPTIVAS ===")
print(df[["age", "duration", "campaign", "pdays", "previous",
          "emp.var.rate", "cons.price.idx", "cons.conf.idx",
          "euribor3m", "Income"]].describe().round(2))

# Tasa de conversión global
tasa = df["y_bin"].mean() * 100
print(f"\nTasa de suscripción global: {tasa:.2f}%")

# Conversión por profesión
print("\nTasa de suscripción por profesión:")
print(df.groupby("job")["y_bin"].mean().sort_values(ascending=False).round(3))

# Conversión por educación
print("\nTasa de suscripción por nivel educativo:")
print(df.groupby("education")["y_bin"].mean().sort_values(ascending=False).round(3))

# Conversión por método de contacto
print("\nTasa de suscripción por método de contacto:")
print(df.groupby("contact")["y_bin"].mean().round(3))

# Conversión por resultado de campaña anterior
print("\nTasa de suscripción por resultado campaña anterior:")
print(df.groupby("poutcome")["y_bin"].mean().sort_values(ascending=False).round(3))

# Duración media de llamada entre suscritos y no suscritos
print("\nDuración media de llamada (segundos):")
print(df.groupby("y")["duration"].mean().round(1))

# ============================================================
# 4. VISUALIZACIÓN DE DATOS
# ============================================================

fig_dir = "graficas"
import os
os.makedirs(fig_dir, exist_ok=True)

# --- 4.1 Distribución de edad ---
fig, ax = plt.subplots(figsize=(10, 5))
ax.hist(df["age"], bins=30, color="#4C72B0", edgecolor="white")
ax.set_title("Distribución de Edad de los Clientes", fontsize=14, fontweight="bold")
ax.set_xlabel("Edad")
ax.set_ylabel("Frecuencia")
plt.tight_layout()
plt.savefig(f"{fig_dir}/01_distribucion_edad.png", dpi=150)
plt.close()

# --- 4.2 Tasa de suscripción global ---
conteo = df["y"].value_counts()
fig, ax = plt.subplots(figsize=(6, 5))
bars = ax.bar(["No suscrito", "Suscrito"], conteo.values,
              color=["#DD8452", "#4C72B0"], edgecolor="white")
for bar, val in zip(bars, conteo.values):
    ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 200,
            f"{val:,}", ha="center", fontsize=11)
ax.set_title("Resultado de la Campaña de Marketing", fontsize=14, fontweight="bold")
ax.set_ylabel("Número de Clientes")
plt.tight_layout()
plt.savefig(f"{fig_dir}/02_resultado_campana.png", dpi=150)
plt.close()

# --- 4.3 Tasa de suscripción por profesión ---
conv_job = df.groupby("job")["y_bin"].mean().sort_values(ascending=False)
fig, ax = plt.subplots(figsize=(12, 5))
conv_job.plot(kind="bar", ax=ax, color="#4C72B0", edgecolor="white")
ax.set_title("Tasa de Suscripción por Profesión", fontsize=14, fontweight="bold")
ax.set_xlabel("")
ax.set_ylabel("Tasa de Suscripción")
ax.yaxis.set_major_formatter(mticker.PercentFormatter(xmax=1))
plt.xticks(rotation=35, ha="right")
plt.tight_layout()
plt.savefig(f"{fig_dir}/03_suscripcion_profesion.png", dpi=150)
plt.close()

# --- 4.4 Tasa de suscripción por nivel educativo ---
conv_edu = df.groupby("education")["y_bin"].mean().sort_values(ascending=False)
fig, ax = plt.subplots(figsize=(10, 5))
conv_edu.plot(kind="bar", ax=ax, color="#55A868", edgecolor="white")
ax.set_title("Tasa de Suscripción por Nivel Educativo", fontsize=14, fontweight="bold")
ax.set_xlabel("")
ax.set_ylabel("Tasa de Suscripción")
ax.yaxis.set_major_formatter(mticker.PercentFormatter(xmax=1))
plt.xticks(rotation=35, ha="right")
plt.tight_layout()
plt.savefig(f"{fig_dir}/04_suscripcion_educacion.png", dpi=150)
plt.close()

# --- 4.5 Duración de llamada: suscritos vs no suscritos ---
fig, ax = plt.subplots(figsize=(8, 5))
for label, color in [("yes", "#4C72B0"), ("no", "#DD8452")]:
    ax.hist(df[df["y"] == label]["duration"], bins=50, alpha=0.6,
            label=label.capitalize(), color=color, edgecolor="none")
ax.set_title("Duración de Llamada: Suscritos vs No Suscritos", fontsize=14, fontweight="bold")
ax.set_xlabel("Duración (segundos)")
ax.set_ylabel("Frecuencia")
ax.legend()
plt.tight_layout()
plt.savefig(f"{fig_dir}/05_duracion_llamada.png", dpi=150)
plt.close()

# --- 4.6 Tasa de suscripción por resultado campaña anterior ---
conv_pout = df.groupby("poutcome")["y_bin"].mean().sort_values(ascending=False)
fig, ax = plt.subplots(figsize=(7, 5))
conv_pout.plot(kind="bar", ax=ax, color="#C44E52", edgecolor="white")
ax.set_title("Tasa de Suscripción por Resultado Campaña Anterior", fontsize=14, fontweight="bold")
ax.set_xlabel("")
ax.set_ylabel("Tasa de Suscripción")
ax.yaxis.set_major_formatter(mticker.PercentFormatter(xmax=1))
plt.xticks(rotation=0)
plt.tight_layout()
plt.savefig(f"{fig_dir}/06_suscripcion_poutcome.png", dpi=150)
plt.close()

# --- 4.7 Matriz de correlación (variables numéricas) ---
num_cols = ["age", "duration", "campaign", "previous",
            "emp.var.rate", "cons.price.idx", "cons.conf.idx",
            "euribor3m", "Income", "y_bin"]
corr = df[num_cols].corr()
fig, ax = plt.subplots(figsize=(10, 8))
sns.heatmap(corr, annot=True, fmt=".2f", cmap="coolwarm",
            center=0, ax=ax, linewidths=0.5)
ax.set_title("Matriz de Correlación", fontsize=14, fontweight="bold")
plt.tight_layout()
plt.savefig(f"{fig_dir}/07_correlacion.png", dpi=150)
plt.close()

# --- 4.8 Distribución de ingresos por resultado ---
fig, ax = plt.subplots(figsize=(8, 5))
for label, color in [("yes", "#4C72B0"), ("no", "#DD8452")]:
    ax.hist(df[df["y"] == label]["Income"].dropna(), bins=40, alpha=0.6,
            label=label.capitalize(), color=color, edgecolor="none")
ax.set_title("Distribución de Ingresos: Suscritos vs No Suscritos", fontsize=14, fontweight="bold")
ax.set_xlabel("Ingreso anual")
ax.set_ylabel("Frecuencia")
ax.legend()
plt.tight_layout()
plt.savefig(f"{fig_dir}/08_ingresos_resultado.png", dpi=150)
plt.close()

# --- 4.9 Número de contactos (campaign) vs suscripción ---
fig, ax = plt.subplots(figsize=(9, 5))
sns.boxplot(data=df, x="y", y="campaign", palette=["#DD8452", "#4C72B0"], ax=ax)
ax.set_title("Número de Contactos de Campaña vs Resultado", fontsize=14, fontweight="bold")
ax.set_xlabel("Suscrito")
ax.set_ylabel("Número de contactos")
ax.set_ylim(0, 20)
plt.tight_layout()
plt.savefig(f"{fig_dir}/09_contactos_resultado.png", dpi=150)
plt.close()

# --- 4.10 Tasa de suscripción por estado civil ---
conv_marital = df.groupby("marital")["y_bin"].mean().sort_values(ascending=False)
fig, ax = plt.subplots(figsize=(7, 5))
conv_marital.plot(kind="bar", ax=ax, color="#8172B2", edgecolor="white")
ax.set_title("Tasa de Suscripción por Estado Civil", fontsize=14, fontweight="bold")
ax.set_xlabel("")
ax.set_ylabel("Tasa de Suscripción")
ax.yaxis.set_major_formatter(mticker.PercentFormatter(xmax=1))
plt.xticks(rotation=0)
plt.tight_layout()
plt.savefig(f"{fig_dir}/10_suscripcion_estado_civil.png", dpi=150)
plt.close()

print("\nGráficas guardadas en la carpeta 'graficas/'")

# ============================================================
# 5. INFORME EXPLICATIVO DEL ANÁLISIS
# ============================================================

informe = f"""
============================================================
INFORME DE ANÁLISIS EDA — CAMPAÑAS DE MARKETING BANCARIO
============================================================

CONTEXTO
--------
Los datos corresponden a campañas de marketing directo de un banco portugués.
El objetivo es predecir si un cliente suscribirá un depósito a plazo (variable 'y').
Se han unido dos datasets: bank-additional.csv ({bank.shape[0]} registros) y
customer-details.xlsx ({customers.shape[0]} registros), mediante la clave 'id_' / 'ID'.
Dataset final tras limpieza: {df.shape[0]} filas.

LIMPIEZA REALIZADA
------------------
- Columnas numéricas con coma decimal (cons.price.idx, euribor3m, etc.) convertidas a float.
- Valores nulos imputados:
    · age: mediana
    · job, marital, education: moda
    · default, housing, loan: 0 (sin información = sin incidencia)
    · euribor3m, cons.price.idx: mediana
    · Income: mediana
- Texto estandarizado (minúsculas, sin espacios).
- Duplicados eliminados: {n_dup}.

HALLAZGOS PRINCIPALES
----------------------
1. TASA DE SUSCRIPCIÓN GLOBAL: {tasa:.1f}%
   El dataset está fuertemente desbalanceado: solo ~1 de cada 9 clientes suscribe.

2. DURACIÓN DE LLAMADA
   Los clientes que suscriben tienen llamadas significativamente más largas
   ({df[df['y']=='yes']['duration'].mean():.0f}s de media vs {df[df['y']=='no']['duration'].mean():.0f}s los que no suscriben).
   Es el predictor más correlacionado con la suscripción.

3. RESULTADO DE CAMPAÑA ANTERIOR (poutcome)
   Los clientes con éxito previo (SUCCESS) suscriben a una tasa muy superior
   al resto. El historial es un factor clave.

4. PROFESIÓN
   Estudiantes y retirados presentan las tasas de suscripción más altas,
   probablemente por mayor disponibilidad de capital o tiempo.

5. EDUCACIÓN
   Clientes con educación universitaria suscriben más que los de formación básica.

6. NÚMERO DE CONTACTOS
   Más de 3-4 contactos no mejora la tasa de conversión: pasado ese umbral,
   la probabilidad de suscripción no aumenta.

7. CONTEXTO MACROECONÓMICO
   La tasa euribor3m y la tasa de variación del empleo (emp.var.rate) correlacionan
   negativamente con la suscripción: en entornos de tipos altos, los depósitos
   a plazo son menos atractivos.

CONCLUSIONES
------------
- Priorizar clientes con historial de éxito en campañas anteriores.
- Inversión en llamadas de mayor duración (mayor engagement = mayor conversión).
- Segmentar campañas para retirados y estudiantes.
- Limitar el número de contactos a un máximo de 3-4 por cliente.
- Adaptar el timing de las campañas al contexto macroeconómico.

============================================================
"""

print(informe)

with open("informe_eda.txt", "w", encoding="utf-8") as f:
    f.write(informe)

print("Informe guardado en 'informe_eda.txt'")
