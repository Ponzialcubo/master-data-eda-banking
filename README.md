# DataProject: EDA — Campañas de Marketing Bancario

**Módulo 3 — Máster en Análisis de Datos | The Power Education**

Análisis exploratorio de datos (EDA) sobre campañas de marketing directo de un banco portugués. El objetivo es entender qué factores influyen en que un cliente suscriba un depósito a plazo bancario.

---

## Datasets utilizados

| Archivo | Registros | Descripción |
|---|---|---|
| `bank-additional.csv` | 43.000 | Datos de campañas: edad, profesión, contacto, indicadores económicos... |
| `customer-details.xlsx` | 20.115 | Datos adicionales del cliente: ingresos, hijos, visitas web... |

Ambos datasets se unen mediante la clave `id_` / `ID`.

---

## Pasos seguidos durante el proyecto

### 1. Carga y exploración inicial
- Lectura de ambos ficheros con Pandas.
- Inspección de tipos, dimensiones y valores nulos.

### 2. Transformación y limpieza
- Unión de datasets por clave común (`id_` ↔ `ID`).
- Corrección de columnas numéricas con coma decimal (formato europeo → float).
- Conversión de la columna `date` a datetime.
- Imputación de valores nulos:
  - Variables numéricas → mediana
  - Variables categóricas → moda
  - Variables binarias (default, housing, loan) → 0
- Estandarización de texto (minúsculas, sin espacios).
- Eliminación de duplicados.

### 3. Análisis descriptivo
- Estadísticas descriptivas de variables numéricas.
- Tasa de suscripción global y segmentada por: profesión, educación, estado civil, método de contacto y resultado de campaña anterior.
- Análisis de duración de llamada entre suscritos y no suscritos.

### 4. Visualización
Se generan 10 gráficas guardadas en la carpeta `graficas/`:

| Archivo | Contenido |
|---|---|
| `01_distribucion_edad.png` | Histograma de edad |
| `02_resultado_campana.png` | Balance suscritos / no suscritos |
| `03_suscripcion_profesion.png` | Tasa de suscripción por profesión |
| `04_suscripcion_educacion.png` | Tasa de suscripción por nivel educativo |
| `05_duracion_llamada.png` | Duración de llamada según resultado |
| `06_suscripcion_poutcome.png` | Tasa según resultado campaña anterior |
| `07_correlacion.png` | Matriz de correlación |
| `08_ingresos_resultado.png` | Distribución de ingresos por resultado |
| `09_contactos_resultado.png` | Número de contactos vs resultado |
| `10_suscripcion_estado_civil.png` | Tasa de suscripción por estado civil |

### 5. Informe
El análisis genera automáticamente un informe en `informe_eda.txt` con hallazgos y conclusiones.

---

## Estructura del repositorio

```
master-data-eda-banking/
├── eda_banking.py            # Script principal de análisis
├── bank-additional.csv       # Dataset principal (no incluido en repo, añadir localmente)
├── customer-details.xlsx     # Dataset secundario (no incluido en repo, añadir localmente)
├── graficas/                 # Carpeta con las 10 visualizaciones generadas
└── README.md
```

---

## Ejecución

```bash
pip install pandas matplotlib seaborn openpyxl
python eda_banking.py
```

---

## Hallazgos principales

- **Tasa de suscripción global:** ~11% — dataset muy desbalanceado.
- **Duración de llamada:** el predictor más fuerte; llamadas largas → mayor conversión.
- **Historial de campaña:** clientes con éxito previo suscriben a tasas mucho más altas.
- **Perfil de mayor conversión:** estudiantes y retirados con educación universitaria.
- **Número de contactos óptimo:** 3-4 contactos; más no mejora la tasa.
- **Contexto macro:** Euribor alto y tasa de empleo variable correlacionan negativamente con la suscripción.
