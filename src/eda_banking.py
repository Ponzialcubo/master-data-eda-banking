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
import os

warnings.filterwarnings("ignore")
sns.set_theme(style="whitegrid")

# Rutas relativas desde src/
DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
OUT_DIR  = os.path.join(os.path.dirname(__file__), "..", "graficas")
os.makedirs(OUT_DIR, exist_ok=True)

# ============================================================
# 1. CARGA DE DATOS
# ============================================================

bank      = pd.read_csv(os.path.join(DATA_DIR, "bank-additional.csv"), sep=",")
customers = pd.read_excel(os.path.join(DATA_DIR, "customer-details.xlsx"))

print("=== bank-additional.csv ===")
print(f"Filas: {bank.shape[0]} | Columnas: {bank.shape[1]}")
print(bank.head(3))

print("\n=== customer-details.xlsx ===")
print(f"Filas: {customers.shape[0]} | Columnas: {customers.shape[1]}")
print(customers.head(3))

# ============================================================
# 2. TRANSFORMACIÓN Y LIMPIEZA DE DATOS
# ============================================================

# 2.1 Unión de datasets por ID
df = pd.merge(bank, customers, left_on="id_", right_on="ID", how="left")
df.drop(columns=["Unnamed: 0_x", "Unnamed: 0_y", "ID"], inplace=True)
print(f"\nDataset unificado: {df.shape[0]} filas, {df.shape[1]} columnas")

# 2.2 Corrección de tipos — columnas numéricas con coma decimal
for col in ["cons.price.idx", "cons.conf.idx", "euribor3m", "nr.employed"]:
    if df[col].dtype == object:
        df[col] = pd.to_numeric(
            df[col].astype(str).str.replace(",", ".").str.strip(),
            errors="coerce"
        )

# Fecha y variable objetivo binaria
df["date"]  = pd.to_datetime(df["date"], dayfirst=False, errors="coerce")
df["y_bin"] = (df["y"] == "yes").astype(int)

print("\nTipos tras conversión:")
print(df.dtypes)

# 2.3 Valores nulos — inspección
print("\nValores nulos por columna:")
nulls = df.isnull().sum()
print(nulls[nulls > 0])

# Imputación: variables numéricas → mediana; categóricas → moda; binarias → 0
df["age"]       = df["age"].fillna(df["age"].median())
df["job"]       = df["job"].fillna(df["job"].mode()[0])
df["marital"]   = df["marital"].fillna(df["marital"].mode()[0])
df["education"] = df["education"].fillna(df["education"].mode()[0])
df["Income"]    = df["Income"].fillna(df["Income"].median())

for col in ["default", "housing", "loan"]:
    df[col] = df[col].fillna(0)
for col in ["euribor3m", "cons.price.idx"]:
    df[col] = df[col].fillna(df[col].median())

print("\nNulos restantes:", df.isnull().sum().sum())

# 2.4 Estandarización de texto
for col in ["job", "marital", "education", "contact"]:
    df[col] = df[col].str.lower().str.strip()
df["poutcome"] = df["poutcome"].str.upper().str.strip()

# 2.5 Duplicados
n_dup = df.duplicated().sum()
print(f"\nDuplicados eliminados: {n_dup}")
df.drop_duplicates(inplace=True)
df.reset_index(drop=True, inplace=True)

# 2.6 Guardar dataset limpio en data/
df.to_csv(os.path.join(DATA_DIR, "bank_clean.csv"), index=False)
print(f"\nDataset limpio guardado en data/bank_clean.csv ({df.shape[0]} filas)")

# ============================================================
# 3. ANÁLISIS DESCRIPTIVO
# ============================================================

print("\n=== ESTADÍSTICAS DESCRIPTIVAS ===")
print(df[["age", "duration", "campaign", "pdays", "previous",
          "emp.var.rate", "cons.price.idx", "cons.conf.idx",
          "euribor3m", "Income"]].describe().round(2))

tasa = df["y_bin"].mean() * 100
print(f"\nTasa de suscripción global: {tasa:.2f}%")

print("\nTasa de suscripción por profesión:")
print(df.groupby("job")["y_bin"].mean().sort_values(ascending=False).round(3))

print("\nTasa de suscripción por nivel educativo:")
print(df.groupby("education")["y_bin"].mean().sort_values(ascending=False).round(3))

print("\nTasa de suscripción por método de contacto:")
print(df.groupby("contact")["y_bin"].mean().round(3))

print("\nTasa de suscripción por resultado campaña anterior:")
print(df.groupby("poutcome")["y_bin"].mean().sort_values(ascending=False).round(3))

print("\nDuración media de llamada (segundos):")
print(df.groupby("y")["duration"].mean().round(1))

dur_yes = df[df["y"] == "yes"]["duration"].mean()
dur_no  = df[df["y"] == "no"]["duration"].mean()

# ============================================================
# 4. VISUALIZACIÓN DE DATOS
# ============================================================

# 4.1 Distribución de edad
fig, ax = plt.subplots(figsize=(10, 5))
ax.hist(df["age"], bins=30, color="#4C72B0", edgecolor="white")
ax.set_title("Distribución de Edad de los Clientes", fontsize=14, fontweight="bold")
ax.set_xlabel("Edad"); ax.set_ylabel("Frecuencia")
plt.tight_layout()
plt.savefig(os.path.join(OUT_DIR, "01_distribucion_edad.png"), dpi=150)
plt.close()

# 4.2 Resultado de la campaña (balance)
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
plt.savefig(os.path.join(OUT_DIR, "02_resultado_campana.png"), dpi=150)
plt.close()

# 4.3 Suscripción por profesión
conv_job = df.groupby("job")["y_bin"].mean().sort_values(ascending=False)
fig, ax = plt.subplots(figsize=(12, 5))
conv_job.plot(kind="bar", ax=ax, color="#4C72B0", edgecolor="white")
ax.set_title("Tasa de Suscripción por Profesión", fontsize=14, fontweight="bold")
ax.set_xlabel(""); ax.set_ylabel("Tasa de Suscripción")
ax.yaxis.set_major_formatter(mticker.PercentFormatter(xmax=1))
plt.xticks(rotation=35, ha="right"); plt.tight_layout()
plt.savefig(os.path.join(OUT_DIR, "03_suscripcion_profesion.png"), dpi=150)
plt.close()

# 4.4 Suscripción por educación
conv_edu = df.groupby("education")["y_bin"].mean().sort_values(ascending=False)
fig, ax = plt.subplots(figsize=(10, 5))
conv_edu.plot(kind="bar", ax=ax, color="#55A868", edgecolor="white")
ax.set_title("Tasa de Suscripción por Nivel Educativo", fontsize=14, fontweight="bold")
ax.set_xlabel(""); ax.set_ylabel("Tasa de Suscripción")
ax.yaxis.set_major_formatter(mticker.PercentFormatter(xmax=1))
plt.xticks(rotation=35, ha="right"); plt.tight_layout()
plt.savefig(os.path.join(OUT_DIR, "04_suscripcion_educacion.png"), dpi=150)
plt.close()

# 4.5 Duración de llamada
fig, ax = plt.subplots(figsize=(8, 5))
for label, color in [("yes", "#4C72B0"), ("no", "#DD8452")]:
    ax.hist(df[df["y"] == label]["duration"], bins=50, alpha=0.6,
            label=label.capitalize(), color=color, edgecolor="none")
ax.set_title("Duración de Llamada: Suscritos vs No Suscritos", fontsize=14, fontweight="bold")
ax.set_xlabel("Duración (segundos)"); ax.set_ylabel("Frecuencia"); ax.legend()
plt.tight_layout()
plt.savefig(os.path.join(OUT_DIR, "05_duracion_llamada.png"), dpi=150)
plt.close()

# 4.6 Suscripción por resultado campaña anterior
conv_pout = df.groupby("poutcome")["y_bin"].mean().sort_values(ascending=False)
fig, ax = plt.subplots(figsize=(7, 5))
conv_pout.plot(kind="bar", ax=ax, color="#C44E52", edgecolor="white")
ax.set_title("Tasa de Suscripción por Resultado Campaña Anterior", fontsize=14, fontweight="bold")
ax.set_xlabel(""); ax.set_ylabel("Tasa de Suscripción")
ax.yaxis.set_major_formatter(mticker.PercentFormatter(xmax=1))
plt.xticks(rotation=0); plt.tight_layout()
plt.savefig(os.path.join(OUT_DIR, "06_suscripcion_poutcome.png"), dpi=150)
plt.close()

# 4.7 Matriz de correlación
num_cols = ["age", "duration", "campaign", "previous",
            "emp.var.rate", "cons.price.idx", "cons.conf.idx",
            "euribor3m", "Income", "y_bin"]
corr = df[num_cols].corr()
fig, ax = plt.subplots(figsize=(10, 8))
sns.heatmap(corr, annot=True, fmt=".2f", cmap="coolwarm", center=0,
            ax=ax, linewidths=0.5)
ax.set_title("Matriz de Correlación", fontsize=14, fontweight="bold")
plt.tight_layout()
plt.savefig(os.path.join(OUT_DIR, "07_correlacion.png"), dpi=150)
plt.close()

# 4.8 Distribución de ingresos
fig, ax = plt.subplots(figsize=(8, 5))
for label, color in [("yes", "#4C72B0"), ("no", "#DD8452")]:
    ax.hist(df[df["y"] == label]["Income"].dropna(), bins=40, alpha=0.6,
            label=label.capitalize(), color=color, edgecolor="none")
ax.set_title("Distribución de Ingresos: Suscritos vs No Suscritos", fontsize=14, fontweight="bold")
ax.set_xlabel("Ingreso anual"); ax.set_ylabel("Frecuencia"); ax.legend()
plt.tight_layout()
plt.savefig(os.path.join(OUT_DIR, "08_ingresos_resultado.png"), dpi=150)
plt.close()

# 4.9 Contactos vs resultado
fig, ax = plt.subplots(figsize=(9, 5))
sns.boxplot(data=df, x="y", y="campaign", palette=["#DD8452", "#4C72B0"], ax=ax)
ax.set_title("Número de Contactos de Campaña vs Resultado", fontsize=14, fontweight="bold")
ax.set_xlabel("Suscrito"); ax.set_ylabel("Número de contactos"); ax.set_ylim(0, 20)
plt.tight_layout()
plt.savefig(os.path.join(OUT_DIR, "09_contactos_resultado.png"), dpi=150)
plt.close()

# 4.10 Suscripción por estado civil
conv_marital = df.groupby("marital")["y_bin"].mean().sort_values(ascending=False)
fig, ax = plt.subplots(figsize=(7, 5))
conv_marital.plot(kind="bar", ax=ax, color="#8172B2", edgecolor="white")
ax.set_title("Tasa de Suscripción por Estado Civil", fontsize=14, fontweight="bold")
ax.set_xlabel(""); ax.set_ylabel("Tasa de Suscripción")
ax.yaxis.set_major_formatter(mticker.PercentFormatter(xmax=1))
plt.xticks(rotation=0); plt.tight_layout()
plt.savefig(os.path.join(OUT_DIR, "10_suscripcion_estado_civil.png"), dpi=150)
plt.close()

print(f"\n10 gráficas guardadas en graficas/")
print("Análisis completado.")
