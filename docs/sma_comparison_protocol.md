# Comparación educativa de parámetros SMA

## Identidad y objetivo

Protocolo: sma_windows_v1.

Objetivo: comparar cuatro configuraciones de SMA en VALIDATION,
manteniendo constantes las demás condiciones.

Este estudio no demuestra rentabilidad futura ni autoriza operar
con dinero real.

## Candidatos

Ventanas expresadas en observaciones diarias:

| Candidato | fast_window | slow_window |
|---|---:|---:|
| A | 20 | 100 |
| B | 50 | 100 |
| C | 20 | 200 |
| D | 50 | 200 |

No se añadirán candidatos a esta revisión después de observar resultados.
Las ampliaciones se documentarán como una nueva revisión y conservarán
el historial de intentos anteriores.

## Condiciones comunes

- Estrategia: sma_trend, versión 1.
- Dataset: SPY_2020-01-01_2026-01-01_snapshot.
- SHA-256:
  9662b617273dbb09abe048bfc6408fc191fb71a5c8183963658325b44aa01d7d
- Capital inicial por periodo: 10000.0.
- Comisión: 0.001 sobre el importe negociado, en entradas y salidas.
- validation_start: 2023-01-01.
- test_start: 2024-01-01.
- Modo de ejecución: development.

Solo cambian fast_window y slow_window.

Se mantienen las convenciones actuales: señales al cierre, ejecución
en la apertura siguiente, posiciones long/cash, unidades fraccionarias
y sin liquidación forzada al final del periodo.

No se modelan spread, slippage ni restricciones de liquidez.

## Selección

El criterio principal es el Sharpe de la estrategia en VALIDATION,
calculado sobre retornos netos de las comisiones modeladas.

Se utiliza la definición actual:
media de retornos diarios multiplicada por 252, dividida entre
la desviación estándar muestral diaria multiplicada por sqrt(252).
La referencia libre de riesgo es cero.

La clasificación es descendente: mayor Sharpe primero.

TRAIN se conserva para diagnóstico, pero no interviene en la clasificación.
TEST no se evalúa durante esta comparación ni se utiliza para seleccionar.

## Valores no disponibles y errores

- Sharpe None: candidato conservado en el informe, sin clasificación.
- Sharpe cero o negativo finito: valor válido para la clasificación.
- NaN o infinito inesperados en el Sharpe: error que debe investigarse;
  no se sustituyen por cero ni se omiten silenciosamente.
- Un fallo de ejecución se registra como fallo, no como mal rendimiento
  ni como métrica no disponible.

No se declarará completa una comparación con fallos pendientes.
Las correcciones y repeticiones conservarán la referencia a los intentos
anteriores.

## Empates

Los valores de Sharpe exactamente iguales se consideran empatados.
No se elige un ganador único arbitrariamente.

El redondeo de presentación no se utiliza para determinar empates.
Una diferencia pequeña tampoco constituye por sí sola evidencia
de superioridad estadística.

## Información complementaria

Para cada candidato se conservarán:

- Configuración completa e identidad del experimento.
- Datos, código, entorno y convenciones.
- Resultados de TRAIN y VALIDATION.
- Equity final y CAGR.
- Volatilidad y máximo drawdown.
- Exposición, número de órdenes y operaciones cerradas.
- Comparación con Buy & Hold bajo las convenciones registradas.

Estas métricas aportan contexto, pero no cambian el criterio principal
después de observar los resultados.

## Interpretación y límites

El primer clasificado será el mejor según el criterio elegido
en este periodo, no una estrategia validada para producción.

Cero operaciones cerradas no implica ausencia de exposición:
puede existir una posición abierta.

Un único año de VALIDATION y un solo activo proporcionan evidencia
limitada. No se establece todavía un umbral para promover candidatos
a paper trading o live.

Los datos históricos ya han sido observados durante el desarrollo.
Este protocolo no constituye una evaluación sobre un holdout intacto.

Se conservarán todos los intentos, no solo el mejor.
No se implementan todavía correcciones estadísticas por múltiples pruebas.