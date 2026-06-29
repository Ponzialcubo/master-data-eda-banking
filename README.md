# DataProject: EDA — Campañas de Marketing Bancario

**Módulo 3 — Máster en Análisis de Datos | The Power Education**

Análisis exploratorio de datos (EDA) sobre campañas de marketing directo de un banco portugués. El objetivo es entender qué factores influyen en que un cliente suscriba un depósito a plazo bancario.

---

## Estructura del repositorio

```
master-data-eda-banking/
├── src/
│   └── eda_banking.py        # Script principal con todo el análisis
├── data/
│   ├── bank-additional.csv   # Dataset en bruto (añadir localmente)
│   ├── customer-details.xlsx # Dataset en bruto (añadir localmente)
│   └── bank_clean.csv        # Dataset limpio (generado al ejecutar el script)
├── graficas/                 # 10 visualizaciones generadas automáticamente
└── README.md
```

---

## Datasets utilizados

| Archivo | Registros | Descripción |
|---|---|---|
| `bank-additional.csv` | 43.000 | Campañas: edad, profesión, contacto, indicadores económicos... |
| `customer-details.xlsx` | 20.115 | Datos del cliente: ingresos, hijos, visitas web... |

Ambos datasets se unen mediante la clave `id_` / `ID`.

---

## Ejecución

```bash
pip install pandas matplotlib seaborn openpyxl
python src/eda_banking.py
```

---

## Pasos seguidos durante el proyecto

### 1. Carga y exploración inicial
- Lectura de `bank-additional.csv` (sep=`,`) y `customer-details.xlsx` con Pandas.
- Inspección de dimensiones, tipos de datos y valores nulos.
- Identificación de columnas numéricas mal formateadas (coma decimal europea).

### 2. Transformación y limpieza

**Unión de datasets**
- Merge por `id_` (bank) ↔ `ID` (customers) con `how="left"` para conservar todos los registros del dataset principal.

**Corrección de tipos**
- Columnas `cons.price.idx`, `cons.conf.idx`, `euribor3m`, `nr.employed` llegaban como string con coma decimal → convertidas a float con `str.replace(",", ".")` + `pd.to_numeric`.
- Columna `date` convertida a datetime.
- Variable objetivo `y` binarizada → `y_bin` (1=suscrito, 0=no).

**Imputación de nulos**
| Variable | Estrategia | Justificación |
|---|---|---|
| `age` | Mediana | Resistente a outliers (clientes muy mayores) |
| `job`, `marital`, `education` | Moda | Variables categóricas con categoría dominante |
| `default`, `housing`, `loan` | 0 | Sin dato conocido = sin incidencia registrada |
| `euribor3m`, `cons.price.idx` | Mediana | Variables macroeconómicas estables |
| `Income` | Mediana | Variable externa con muchos nulos por join parcial |

**Estandarización**
- Texto a minúsculas y sin espacios en: `job`, `marital`, `education`, `contact`.
- `poutcome` a mayúsculas para consistencia.
- Eliminación de duplicados.

**Exportación**
- Dataset limpio guardado en `data/bank_clean.csv`.

### 3. Análisis descriptivo

**Estadísticas generales**
- Media, mediana, desviación estándar, mín/máx de todas las variables numéricas.
- Distribuciones de `age`, `duration`, `campaign`, `Income`.

**Análisis segmentado**
- Tasa de suscripción por: profesión, nivel educativo, estado civil, método de contacto, resultado campaña anterior.
- Duración media de llamada comparada entre suscritos y no suscritos.
- Correlaciones entre variables numéricas y la variable objetivo.

### 4. Visualización

| Gráfica | Contenido |
|---|---|
| `01_distribucion_edad.png` | Histograma de edad de los clientes |
| `02_resultado_campana.png` | Balance suscritos / no suscritos |
| `03_suscripcion_profesion.png` | Tasa de suscripción por profesión |
| `04_suscripcion_educacion.png` | Tasa de suscripción por nivel educativo |
| `05_duracion_llamada.png` | Duración de llamada según resultado |
| `06_suscripcion_poutcome.png` | Tasa según resultado campaña anterior |
| `07_correlacion.png` | Matriz de correlación (variables numéricas) |
| `08_ingresos_resultado.png` | Distribución de ingresos por resultado |
| `09_contactos_resultado.png` | Número de contactos vs resultado (boxplot) |
| `10_suscripcion_estado_civil.png` | Tasa de suscripción por estado civil |

---

## Informe del análisis

### Contexto
Datos de campañas de marketing directo (llamadas telefónicas) de un banco portugués. Variable objetivo: `y` — si el cliente suscribe un depósito a plazo bancario.

### Tasa de suscripción global: ~11%
El dataset está fuertemente desbalanceado: solo 1 de cada 9 clientes suscribe. Esto es relevante de cara a futuros modelos predictivos (se necesitaría oversampling o métricas ajustadas).

### Hallazgos clave

**1. Duración de la llamada — predictor más fuerte**
Los clientes que suscriben tienen llamadas significativamente más largas (~550s de media vs ~250s los que no suscriben). A mayor engagement en la conversación, mayor probabilidad de conversión. Sin embargo, este dato no puede usarse para predecir antes de la llamada.

**2. Historial de campaña anterior (poutcome)**
Clientes con éxito previo (SUCCESS) convierten a una tasa muy superior al resto (~65% vs ~10% en NONEXISTENT). El historial positivo es el predictor más accionable antes de iniciar la llamada.

**3. Perfil de mayor conversión por profesión**
Estudiantes y retirados presentan las tasas más altas. Probablemente tienen más liquidez disponible o mayor disposición a contratar productos de ahorro conservadores.

**4. Nivel educativo**
Clientes con educación universitaria suscriben más que los de formación básica. A mayor nivel educativo, mayor comprensión del producto y mayor propensión a invertir.

**5. Número de contactos óptimo**
Más de 3-4 contactos no mejora la tasa de conversión. A partir de ese punto, el cliente ya ha tomado su decisión y insistir puede generar rechazo. Recomendable limitar a 3 intentos máximo.

**6. Contexto macroeconómico**
La tasa `euribor3m` y `emp.var.rate` correlacionan negativamente con la suscripción. En entornos de tipos altos, los depósitos a plazo son menos atractivos frente a otras alternativas de inversión. Las campañas deberían intensificarse en períodos de tipos bajos.

**7. Método de contacto**
El contacto por teléfono móvil (`cellular`) tiene una tasa de conversión notablemente superior al teléfono fijo (`telephone`). Priorizar el canal móvil.

### Conclusiones y recomendaciones

| Acción | Justificación |
|---|---|
| Priorizar clientes con éxito en campaña anterior | Tasa de conversión hasta 6x superior |
| Segmentar para retirados y estudiantes | Mayor tasa de suscripción histórica |
| Limitar contactos a 3-4 por cliente | Más intentos no mejoran la conversión |
| Usar canal móvil preferentemente | Mayor tasa de éxito que teléfono fijo |
| Intensificar campañas con Euribor bajo | Contexto macro favorable para depósitos |
| Apostar por educación universitaria | Mayor propensión al producto |
