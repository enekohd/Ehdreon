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

```bash
./.venv/bin/python main.py
```

El programa descarga datos de SPY mediante yfinance y muestra:

- Los periodos TRAIN y TEST.
- Las métricas de la estrategia SMA.
- Los benchmarks Buy & Hold, con y sin coste de entrada.
- Las operaciones cerradas y sus métricas.

Esta ejecución requiere acceso a internet.

La configuración principal está en `main.py`: activo, fechas,
capital inicial, coste de transacción y ventanas de las SMA.

## Limitaciones actuales

- Los datos se descargan de nuevo en cada ejecución y pueden cambiar.
- El modelo de costes es simplificado.
- El retorno neto del registro de operaciones es aproximado y no
    concilia exactamente con la capitalización del backtester.
- El registro de operaciones solo incluye operaciones cerradas.
- Las pruebas actuales cubren ejemplos concretos; faltan casos límite.
- El histórico de TEST ya se ha observado durante el desarrollo.
- Todavía no hay modelos ML, paper trading ni interfaz gráfica.
- La reconstrucción del entorno no se ha comprobado en otros
  sistemas operativos.