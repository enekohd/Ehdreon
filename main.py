# ============================================================
# 1. IMPORTACIONES
# ============================================================

# Biblioteca estándar.
from pathlib import Path

# Funciones de los módulos de nuestro proyecto.
from src.backtesting.backtester import run_backtest
from src.metrics import calculate_metrics
from src.strategies.sma_strategies import apply_sma_strategies
from src.trades import build_trade_log, calculate_trade_metrics
from src.backtesting.benchmarks import calculate_buy_hold
from src.data.loader import load_market_data


# ============================================================
# 2. CONFIGURACIÓN DEL EXPERIMENTO
# ============================================================

ticker = "SPY"
initial_capital = 10000

# Coste proporcional por cambio de posición: 0.001 equivale al 0.1 %.
transaction_cost = 0.001

# Las fechas anteriores pertenecen a TRAIN; las demás, a TEST.
split_date = "2024-01-01"

# La raíz se obtiene a partir de la ubicación de este archivo.
project_root = Path(__file__).resolve().parent

snapshot_path = (
    project_root
    / "data"
    / "raw"
    / "SPY_2020-01-01_2026-01-01_snapshot.csv"
)

metadata_path = (
    project_root
    / "data"
    / "metadata"
    / "SPY_2020-01-01_2026-01-01_snapshot.json"
)

# ============================================================
# 3. CARGA LOCAL Y PREPARACIÓN DE LOS DATOS
# ============================================================

# El cargador reconstruye las fechas y valida los datos originales.
data = load_market_data(snapshot_path, metadata_path)

print("\nMarket data snapshot loaded:", snapshot_path)
print("Raw rows:", len(data))
print("First date:", data.index[0])
print("Last date:", data.index[-1])

# Retorno entre cierres consecutivos.
# La primera fila queda sin retorno porque no tiene una fila anterior.
data["Return"] = data["Close"].pct_change()

# Eliminamos filas con valores ausentes.
# Actualmente esto también elimina la primera fila por su Return.
data = data.dropna()


# ============================================================
# 4. BENCHMARK GLOBAL DE REFERENCIA
# ============================================================

# Curva Buy & Hold basada en cierres y normalizada al capital inicial.
# No se utiliza para calcular las métricas separadas de TRAIN y TEST.
data["BuyHold"] = (
    initial_capital
    * data["Close"]
    / data["Close"].iloc[0]
)


# ============================================================
# 5. CÁLCULO DE LAS SMA Y LAS SEÑALES
# ============================================================

# Calculamos las medias antes del corte para que TEST disponga
# del histórico necesario para sus primeras SMA.
# Estas medias utilizan únicamente el cierre actual y los anteriores.
strategy_data = apply_sma_strategies(
    data,
    fast_window=50,
    slow_window=200,
)


# ============================================================
# 6. SEPARACIÓN TEMPORAL TRAIN / TEST
# ============================================================

# Creamos copias separadas conservando el orden cronológico.
train_data = strategy_data.loc[
    strategy_data.index < split_date
].copy()

test_data = strategy_data.loc[
    strategy_data.index >= split_date
].copy()


# ------------------------------------------------------------
# 6.1. Comprobaciones de integridad del split
# ------------------------------------------------------------

assert not train_data.empty, "Train data is empty"
assert not test_data.empty, "Test data is empty"

assert strategy_data.index.is_monotonic_increasing, (
    "The dataset must be sorted chronologically"
)

# Ninguna fecha debe pertenecer a ambos periodos.
assert train_data.index.intersection(test_data.index).empty, (
    "Train and test contain overlapping dates"
)

assert train_data.index.max() < test_data.index.min(), (
    "Train must finish before test starts"
)

# El corte debe conservar todas las filas del conjunto original.
assert len(train_data) + len(test_data) == len(strategy_data), (
    "Some rows were lost during the temporal split"
)

print("\nTemporal split checks passed.")


# ------------------------------------------------------------
# 6.2. Resumen de los periodos
# ------------------------------------------------------------

print("\n--- TRAIN PERIOD ---")
print("Start:", train_data.index[0])
print("End:", train_data.index[-1])
print("Rows:", len(train_data))

print("\n--- TEST PERIOD ---")
print("Start:", test_data.index[0])
print("End:", test_data.index[-1])
print("Rows:", len(test_data))


# ============================================================
# 7. EVALUACIÓN DE TRAIN
# ============================================================

# ------------------------------------------------------------
# 7.1. Backtest de la estrategia SMA
# ------------------------------------------------------------

# El motor convierte las señales en posiciones, operaciones,
# retornos de estrategia y curva de capital.
train_results = run_backtest(
    train_data,
    initial_capital=initial_capital,
    transaction_cost=transaction_cost,
)


# ------------------------------------------------------------
# 7.2. Métricas de la estrategia SMA
# ------------------------------------------------------------

train_strategy_metrics = calculate_metrics(
    train_results["StrategyEquity"],
    train_results["StrategyReturn"],
    train_results["Position"],
    train_results["Trade"],
    initial_capital=initial_capital,
)

print("\n--- TRAIN: SMA STRATEGY ---")
for key, value in train_strategy_metrics.items():
    print(key, ":", value)


# ------------------------------------------------------------
# 7.3. Benchmark Buy & Hold de TRAIN - NO COSTS
# ------------------------------------------------------------

# Calculamos el benchmark entre aperturas, sin coste de entrada.
train_buy_hold_returns, train_buy_hold_equity = calculate_buy_hold(
    train_data["Open"],
    initial_capital=initial_capital
)

train_buy_hold_metrics = calculate_metrics(
    train_buy_hold_equity,
    train_buy_hold_returns,
    initial_capital=initial_capital,
)

print("\n--- TRAIN: BUY & HOLD OPEN - NO COSTS---")
for key, value in train_buy_hold_metrics.items():
    print(key, ":", value)

assert train_buy_hold_returns.iloc[0] == 0.0
assert train_buy_hold_equity.iloc[0] == initial_capital
assert train_buy_hold_equity.index.equals(train_results.index)

# Verificación alternativa: comprar y mantener equivale
# a multiplicar el capital por el cociente de precios.
train_expected_final_value = (
    initial_capital 
    * train_data["Open"].iloc[-1]
    / train_data["Open"].iloc[0]
)

train_relative_error = abs(
    train_buy_hold_equity.iloc[-1] / train_expected_final_value - 1
)

assert train_relative_error < 1e-10, (
    "Train Buy & Hold does not match the price-ratio calculation."
)

# ------------------------------------------------------------
# 7.3.1 Benchmark Buy & Hold de TRAIN - ENTRY COSTS
# ------------------------------------------------------------

# Al comprar en la primera apertura, el primer retorno
# representa únicamente el coste de entrada.
train_buy_hold_net_returns, train_buy_hold_net_equity = calculate_buy_hold(
    train_data["Open"],
    initial_capital=initial_capital,
    entry_cost=transaction_cost
)

train_buy_hold_net_metrics = calculate_metrics(
    train_buy_hold_net_equity,
    train_buy_hold_net_returns,
    initial_capital=initial_capital
)

print("\n --- TRAIN: BUY & HOLD OPEN — ENTRY COST ---")
for key,value in train_buy_hold_net_metrics.items():
    print(key, ":", value)

# Verificación alternativa
train_net_expected_final_value = (
    initial_capital
    / (1 + transaction_cost)
    * train_data["Open"].iloc[-1]
    / train_data["Open"].iloc[0]
)

train_net_relative_error = abs(
    train_buy_hold_net_equity.iloc[-1]
    / train_net_expected_final_value -1
)

assert train_net_relative_error < 1e-10, (
    "Net Buy & Hold does not match the expected final value."
)

# La versión sin costes debe conservar su primer retorno original.
assert train_buy_hold_returns.iloc[0] == 0.0

assert abs(
    train_buy_hold_net_equity.iloc[0]
    - initial_capital / (1 + transaction_cost)
) < 1e-8


# ------------------------------------------------------------
# 7.4. Registro de operaciones cerradas de TRAIN
# ------------------------------------------------------------

# Empareja entradas y salidas.
# Las posiciones abiertas al final no aparecen como trades cerrados.
train_trade_log = build_trade_log(
    train_results
)

print("\n--- TRAIN: TRADE LOG ---")
print(train_trade_log)


# ------------------------------------------------------------
# 7.5. Métricas de las operaciones cerradas de TRAIN
# ------------------------------------------------------------

train_trade_metrics = calculate_trade_metrics(
    train_trade_log
)

print("\n--- TRAIN: TRADE METRICS ---")
for key, value in train_trade_metrics.items():
    print(key, ":", value)


# ============================================================
# 8. PREPARACIÓN DE TEST CON CONTEXTO HISTÓRICO
# ============================================================

# Añadimos el último día de TRAIN para disponer de su señal.
# Las SMA ya están calculadas: esta fila aporta contexto de ejecución.
test_with_context = strategy_data.loc[
    train_data.index[-1]:
].copy()


# ------------------------------------------------------------
# 8.1. Comprobaciones de la fila de contexto
# ------------------------------------------------------------

assert test_with_context.index[0] == train_data.index[-1], (
    "The context must start on the last train date."
)

assert test_with_context.index[1] == test_data.index[0], (
    "The first evaluated row must be the first test date."
)

assert len(test_with_context) == len(test_data) + 1, (
    "Test context must contain exactly one additional row."
)


# ------------------------------------------------------------
# 8.2. Comprobación del histórico necesario para las SMA
# ------------------------------------------------------------

first_test_date = test_data.index[0]

# Ambas medias deben estar disponibles desde la primera fila de TEST.
assert test_data.loc[
    first_test_date,
    ["SMA_50", "SMA_200"],
].notna().all(), (
    "The first test row must contain valid SMA features."
)


# ============================================================
# 9. BACKTEST DE TEST
# ============================================================

# Simulamos un portfolio nuevo.
# La fila de contexto permite ejecutar la última señal de TRAIN
# en la primera apertura de TEST.
test_with_context_results = run_backtest(
    test_with_context,
    initial_capital=initial_capital,
    transaction_cost=transaction_cost,
)

# Excluimos la fila auxiliar de los resultados que vamos a evaluar.
test_results = test_with_context_results.loc[
    test_with_context_results.index >= split_date
].copy()

assert test_results.index.equals(test_data.index), (
    "Test results must contain exactly the test dates."
)


# ============================================================
# 10. INSPECCIÓN DE LA FRONTERA TRAIN / TEST
# ============================================================

# Mostramos el contexto y las dos primeras sesiones de TEST
# para revisar señales, posiciones, costes y retornos.
boundary_columns = [
    "Open",
    "Signal",
    "Position",
    "Trade",
    "OpenReturn",
    "StrategyReturn",
    "StrategyEquity",
]

print("\n--- TEST BOUNDARY CHECK ---")
print(
    test_with_context_results[
        boundary_columns
    ].iloc[:3].to_string()
)


# ============================================================
# 11. MÉTRICAS DE LA ESTRATEGIA SMA EN TEST
# ============================================================

# Todas las series deben proceder del mismo periodo evaluado.
# El capital inicial es el disponible antes del primer coste.
test_strategy_metrics = calculate_metrics(
    test_results["StrategyEquity"],
    test_results["StrategyReturn"],
    test_results["Position"],
    test_results["Trade"],
    initial_capital=initial_capital,
)


# ------------------------------------------------------------
# 11.1. Comprobaciones del capital informado
# ------------------------------------------------------------

assert test_strategy_metrics["Initial Value"] == initial_capital, (
    "Test metrics must use the capital available before the first trade."
)

assert test_strategy_metrics["Final Value"] == (
    test_results["StrategyEquity"].iloc[-1]
), (
    "The reported final value must match the final test equity."
)


# ------------------------------------------------------------
# 11.2. Presentación de las métricas
# ------------------------------------------------------------

print("\n--- TEST: SMA STRATEGY ---")
for key, value in test_strategy_metrics.items():
    print(key, ":", value)


# ============================================================
# 12. BENCHMARK BUY & HOLD DE TEST: OPEN, SIN COSTES
# ============================================================

test_buy_hold_returns, test_buy_hold_equity = calculate_buy_hold(
    test_data["Open"],
    initial_capital=initial_capital,
)

test_buy_hold_metrics = calculate_metrics(
    test_buy_hold_equity,
    test_buy_hold_returns,
    initial_capital=initial_capital
)

print("\n--- TEST: BUY & HOLD OPEN — NO COSTS ---")
for key , value in test_buy_hold_metrics.items():
    print(key, ":", value)

assert test_buy_hold_returns.iloc[0] == 0.0
assert test_buy_hold_equity.iloc[0] == initial_capital
assert test_buy_hold_equity.index.equals(test_results.index)

# Verificación alternativa: comprar y mantener equivale
# a multiplicar el capital por el cociente de precios.
test_expected_final_value = (
    initial_capital 
    * test_data["Open"].iloc[-1]
    / test_data["Open"].iloc[0]
)

test_relative_error = abs(
    test_buy_hold_equity.iloc[-1] / test_expected_final_value - 1
)

assert test_relative_error < 1e-10, (
    "Test Buy & Hold does not match the price-ratio calculation."
)

print("\nBuy & Hold checks passed for TRAIN and TEST.")

# ============================================================
# 13. BENCHMARK BUY & HOLD DE TEST: CON COSTE DE ENTRADA
# ============================================================

# Al comprar en la primera apertura, el primer retorno
# representa únicamente el coste de entrada.
test_buy_hold_net_returns, test_buy_hold_net_equity = calculate_buy_hold(
    test_data["Open"],
    initial_capital=initial_capital,
    entry_cost=transaction_cost
)

test_buy_hold_net_metrics = calculate_metrics(
    test_buy_hold_net_equity,
    test_buy_hold_net_returns,
    initial_capital=initial_capital
)

print("\n --- TEST: BUY & HOLD OPEN — ENTRY COST ---")
for key,value in test_buy_hold_net_metrics.items():
    print(key, ":", value)

# Verificación alternativa
test_net_expected_final_value = (
    initial_capital
    / (1 + transaction_cost)
    * test_data["Open"].iloc[-1]
    / test_data["Open"].iloc[0]
)

test_net_relative_error = abs(
    test_buy_hold_net_equity.iloc[-1]
    / test_net_expected_final_value -1
)

assert test_net_relative_error < 1e-10, (
    "Net Buy & Hold does not match the expected final value."
)

# La versión sin costes debe conservar su primer retorno original.
assert test_buy_hold_returns.iloc[0] == 0.0

assert abs(
    test_buy_hold_net_equity.iloc[0]
    - initial_capital / (1 + transaction_cost)
) < 1e-8

# ============================================================
# 14. REGISTRO DE OPERACIONES CERRADAS DE TEST
# ============================================================

# El contexto permite detectar la entrada en la primera sesión.
test_trade_log = build_trade_log(
    test_with_context_results
)

print("\n--- TEST: TRADE LOG ---")
print(test_trade_log.to_string(index=False))

#Comprobaciones
assert not test_trade_log.empty, (
    "Expected at least one closed trade in this test experiment"
)

first_test_date = test_results.index[0]
last_test_date = test_results.index[-1]

assert (
    test_trade_log["Entry Date"] >= first_test_date
).all(), (
    "A test trade starts before the evaluated period."
)

assert (
    test_trade_log["Exit Date"] <= last_test_date
).all(), (
    "A test trade ends after the evaluated period."
)

assert (
    test_trade_log["Entry Date"] < test_trade_log["Exit Date"]
).all(), (
    "Each closed trade must exit after its entry."
)

# ------------------------------------------------------------
# 14.1. Métricas de las operaciones cerradas de TEST
# ------------------------------------------------------------

test_trade_metrics = calculate_trade_metrics(
    test_trade_log
)

print("\n--- TEST: CLOSED TRADE METRICS — EXECUTION-BASED NET RETURNS ---")
for key,value in test_trade_metrics.items():
    print(key, ":", value)

