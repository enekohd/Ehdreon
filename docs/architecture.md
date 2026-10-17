# Arquitectura actual de AI Trader

## Alcance

Backtesting diario de un activo con estrategia SMA, posiciones long/cash,
unidades fraccionarias y comisiones proporcionales al importe negociado.

No incluye spread, slippage, restricciones de liquidez ni ejecución real.
Las posiciones abiertas no se liquidan automáticamente al final del periodo.

## Flujo principal

1. ExperimentConfig define y valida los parámetros.
2. El cargador verifica el SHA-256 y valida los datos OHLCV.
3. Se recopilan los metadatos del experimento.
4. La estrategia calcula medias móviles y señales.
5. Se separan los periodos de evaluación.
6. El backtester ejecuta operaciones y mantiene efectivo y unidades.
7. Se calculan métricas, benchmarks y operaciones cerradas.
8. Los resultados se serializan y se adjuntan al registro.
9. El registro se guarda como JSON y se comprueba mediante relectura.

main.py coordina la carga, la obtención de metadatos, la presentación
y la persistencia. Delega el cálculo en src/experiments/runner.py.

## Ejecución del experimento

run_experiment(data, config):

- Recibe el snapshot OHLCV ya cargado y validado.
- Trabaja sobre una copia.
- Prepara retornos y señales SMA.
- Separa TRAIN y TEST.
- Añade una fila de contexto de ejecución a TEST.
- Evalúa ambos periodos con capital inicial independiente.
- Devuelve resultados de cálculo, sin serializarlos.

evaluate_period(backtest_data, evaluation_index, config):

- Admite evaluar todas las filas o excluir una única fila inicial
  de contexto.
- Ejecuta el backtest con el contexto necesario.
- Calcula las métricas de cartera solo sobre las fechas evaluadas.
- Reconstruye las operaciones utilizando el resultado con contexto.
- Calcula los benchmarks desde la primera apertura evaluada.
- Devuelve curvas, métricas, operaciones y benchmarks.

Estas funciones no cargan archivos, consultan Git, imprimen ni guardan
resultados.

La preparación conserva el comportamiento anterior: elimina la primera
fila por el retorno inicial ausente y mantiene la columna global BuyHold
por compatibilidad. Esta columna no sustituye los benchmarks por periodo.

La evaluación requiere al menos dos observaciones y un intervalo
de al menos un día, de acuerdo con las métricas diarias actuales.

## Señales, ejecución y contabilidad

La señal del cierre anterior determina el objetivo en la apertura actual.

TargetPosition representa la intención.
Position indica si hay unidades después de ejecutar.
Quantity representa las unidades realmente mantenidas.

Compra con todo el efectivo disponible:

quantity = cash / (price * (1 + commission_rate))
notional = quantity * price
fee = notional * commission_rate
cash_after = cash - notional - fee

Venta completa:

notional = quantity * price
fee = notional * commission_rate
cash_received = notional - fee

Valoración después de la posible operación:

equity = cash + quantity * open_price

Retorno de la cartera:

strategy_return = equity / previous_equity - 1

Las comisiones ya están reflejadas en el efectivo.
No se descuentan otra vez del retorno.

## Evaluación temporal

TRAIN y TEST se simulan con capital inicial independiente.

TEST utiliza una fila histórica de contexto para determinar su primera
operación. Esa fila no se incluye en las métricas ni en el periodo
de evaluación informado.

El registro de operaciones utiliza el contexto necesario para reconocer
la primera entrada de TEST.

El periodo TEST actual ya ha sido observado durante el desarrollo.
No es un holdout final intacto.

## Métricas y operaciones

Las métricas de cartera incluyen la valoración de posiciones abiertas.
El registro de operaciones contiene únicamente operaciones cerradas.

Por tanto, el PnL de operaciones cerradas no representa necesariamente
toda la variación de equity.

Una métrica no disponible se distingue de una métrica cuyo valor es cero.

## Módulos de experimentos

- provenance.py: consulta Git y el entorno activo.
- records.py: construye registros, adjunta resultados y guarda JSON.
- serialization.py: representa métricas y fechas sin alterar sus cálculos.
- results.py: organiza resultados por periodo, estrategia y benchmark.
- runner.py: prepara y ejecuta el cálculo de TRAIN y TEST sin operaciones
  de entrada/salida.

Cada registro contiene identidad, configuración, dataset y hash,
información del código, entorno y resultados.

created_at indica el momento de creación del registro.
No representa necesariamente el inicio o final exacto del programa.

## Persistencia

Los registros se guardan en:

artifacts/experiments/<experiment_id>.json

La serialización se realiza antes de crear el archivo.
El modo de creación exclusiva impide sobrescribir archivos existentes.

Los resultados generados se excluyen de Git.
Esta exclusión no constituye una copia de seguridad.

## Limitaciones de reproducibilidad

- Un commit no conserva modificaciones locales no versionadas.
- La captura del entorno es mínima.
- Se presupone que datos y código no cambian durante la ejecución.
- El hash identifica contenido, pero no garantiza corrección point-in-time.
- La escritura no es todavía resistente a interrupciones a mitad del proceso.
- No se registran todavía todos los estados ni las ejecuciones fallidas.
- No se persisten todavía las curvas completas ni el detalle de operaciones
  como artefactos independientes.