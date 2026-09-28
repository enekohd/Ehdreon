# AI Trader

## Objetivo

Proyecto de aprendizaje de ingeniería de software, Machine Learning
y finanzas cuantitativas.

El objetivo es construir una plataforma de investigación con datos
financieros, backtesting, validación temporal y gestión del riesgo.

Actualmente incluye una estrategia SMA, evaluación TRAIN/TEST,
benchmarks Buy & Hold y pruebas con datos sintéticos.

A largo plazo, se incorporarán modelos de ML, ejecución simulada
en tiempo real (paper trading) y una interfaz con gráficos,
estadísticas y seguimiento de operaciones. La ejecución automatizada
es un objetivo futuro; todavía no está implementada.

## Entorno comprobado

- Python 3.13.0 en macOS.
- Instalación desde `requirements.txt` verificada en un entorno nuevo.
- Instalación desde `requirements-frozen.txt` verificada en otro
  entorno nuevo.
- Ambas instalaciones superaron `pip check`, las tres pruebas
  sintéticas y la ejecución de `main.py`.
- Las versiones instaladas en el segundo entorno coincidieron
  con las registradas en `requirements-frozen.txt`.

`requirements.txt` contiene las dependencias directas.
`requirements-frozen.txt` registra las versiones instaladas
en el entorno de comprobación.

## Instalación

Desde la raíz del proyecto y con Python 3.13 disponible:

```bash
python3.13 -m venv .venv
./.venv/bin/python -m pip install -r requirements.txt
./.venv/bin/python -m pip check
```

Para instalar las versiones registradas en el entorno comprobado,
crea un entorno nuevo y utiliza:

```bash
python3.13 -m venv .venv
./.venv/bin/python -m pip install -r requirements-frozen.txt
./.venv/bin/python -m pip check
```

Como alternativa, `requirements.txt` fija las dependencias directas
y permite que el instalador resuelva sus dependencias transitivas.

La instalación desde ambos archivos se ha comprobado en macOS
con Python 3.13.0. No se ha verificado en otras plataformas.

Las instrucciones anteriores corresponden a macOS.
La instalación de paquetes requiere acceso a internet.

## Pruebas

Desde la raíz del proyecto:

```bash
./.venv/bin/python check_metrics.py
./.venv/bin/python check_backtest.py
./.venv/bin/python check_benchmarks.py
```

Estas pruebas utilizan datos sintéticos y no necesitan descargar
precios de mercado.

Comprueban determinados cálculos de métricas, la ejecución temporal
del backtester y los benchmarks Buy & Hold.

## Ejecución

El programa carga una instantánea local de SPY, verifica su huella
SHA-256 y valida sus datos antes de ejecutar los backtests.

Para ejecutarlo se necesitan:

- `data/raw/SPY_2020-01-01_2026-01-01_snapshot.csv`
- `data/metadata/SPY_2020-01-01_2026-01-01_snapshot.json`

El CSV está excluido de Git y debe proporcionarse por separado.
Los metadatos permiten comprobar su identidad, pero no reconstruirlo.

La ejecución de `main.py` no necesita conexión a internet una vez
instaladas las dependencias y disponible la instantánea correcta.

## Limitaciones actuales

- El CSV local no está incluido en Git y necesita conservarse por separado.
- No se registraron el momento exacto de descarga ni el valor efectivo
  de `auto_adjust` de esta instantánea.
- La huella identifica el archivo, pero no demuestra la exactitud
  de los precios ni que estén todas las sesiones esperadas.
- El modelo de costes es simplificado.
- El retorno neto del registro de operaciones es aproximado y no
    concilia exactamente con la capitalización del backtester.
- El registro de operaciones solo incluye operaciones cerradas.
- Las pruebas actuales cubren ejemplos concretos; faltan casos límite.
- El histórico de TEST ya se ha observado durante el desarrollo.
- Todavía no hay modelos ML, paper trading ni interfaz gráfica.
- La reconstrucción del entorno no se ha comprobado en otros
  sistemas operativos.