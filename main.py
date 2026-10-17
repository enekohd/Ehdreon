# ============================================================
# 1. IMPORTACIONES
# ============================================================

# Biblioteca estándar.
from pathlib import Path
import json

# Funciones de los módulos de nuestro proyecto.
from src.data.loader import load_market_data
from src.config import ExperimentConfig
from src.experiments.results import build_period_results
from src.data.integrity import calculate_sha256
from src.experiments.provenance import (
    collect_code_info,
    collect_environment_info,
)
from src.experiments.records import (
    build_experiment_record,
    attach_experiment_results,
    save_experiment_record,
)
from src.experiments.conventions import build_experiment_conventions

from src.experiments.runner import run_experiment

# ============================================================
# 2. CONFIGURACIÓN DEL EXPERIMENTO
# ============================================================

ticker = "SPY"

#Unica configuracion del experimento para esta ejecucion.
config = ExperimentConfig()

# Conservamos temporalmente los nombres que utiliza el resto del main
initial_capital = config.initial_capital
transaction_cost = config.transaction_cost
split_date = config.split_date

# La raíz se obtiene a partir de la ubicación de este archivo.
project_root = Path(__file__).resolve().parent

snapshot_path = (
    project_root
    / "data"
    / "raw"
    / f"{config.dataset_id}.csv"
)

metadata_path = (
    project_root
    / "data"
    / "metadata"
    / f"{config.dataset_id}.json"
)

# ============================================================
# 3. CARGA LOCAL Y PREPARACIÓN DE LOS DATOS
# ============================================================

# El cargador reconstruye las fechas y valida los datos originales.
data = load_market_data(snapshot_path, metadata_path)

#Metadatos de esta ejecucion antes de transformar los datos.
experiment_record = build_experiment_record(
    config,dataset_sha256=calculate_sha256(snapshot_path),
    code_info=collect_code_info(project_root),
    environment_info=collect_environment_info(),
    conventions=build_experiment_conventions(),
)

print("\nMarket data snapshot loaded:", snapshot_path)
print("Raw rows:", len(data))
print("First date:", data.index[0])
print("Last date:", data.index[-1])

# ============================================================
# 4. EJECUCIÓN DEL EXPERIMENTO
# ============================================================

result = run_experiment(data, config)

train = result["train"]
test = result["test"]

# ============================================================
# 5. COMPROBACIONES DE INTEGRACIÓN Y PRESENTACIÓN
# ============================================================

train_index = train["backtest"].index
test_index = test["backtest"].index

assert train_index.intersection(test_index).empty
assert train_index.max() < test_index.min()

for period_name, period in result.items():
    backtest = period["backtest"]
    strategy_metrics = period["strategy_metrics"]
    trade_log = period["trade_log"]
    prices = backtest["Open"]

    assert strategy_metrics["Initial Value"] == config.initial_capital
    assert (
        strategy_metrics["Final Value"]
        == backtest["StrategyEquity"].iloc[-1]
    )

    print(f"\n--- {period_name.upper()} PERIOD ---")
    print("Start:", backtest.index[0])
    print("End:", backtest.index[-1])
    print("Rows:", len(backtest))

    print(f"\n--- {period_name.upper()}: SMA STRATEGY ---")
    for name, value in strategy_metrics.items():
        print(name, ":", value)

    for benchmark_name, benchmark in period["benchmarks"].items():
        assert benchmark["equity"].index.equals(backtest.index)
        assert benchmark["returns"].index.equals(backtest.index)

        entry_cost = (
            0.0
            if benchmark_name == "buy_hold_open_gross"
            else config.transaction_cost
        )

        expected_initial_equity = (
            config.initial_capital / (1.0 + entry_cost)
        )

        expected_final_equity = (
            expected_initial_equity * prices.iloc[-1] / prices.iloc[0]
        )

        assert abs(
            benchmark["equity"].iloc[0] - expected_initial_equity
        ) < 1e-8

        assert abs(
            benchmark["equity"].iloc[-1] - expected_final_equity
        ) < 1e-8

        print(f"\n--- {period_name.upper()}: {benchmark_name} ---")
        for name, value in benchmark["metrics"].items():
            print(name, ":", value)

    #Un registro vacio es valido: puede no haber operqaciones cerradas.
    if not trade_log.empty:
        assert (trade_log["Entry Date"] >= backtest.index[0]).all()
        assert (trade_log["Exit Date"] <= backtest.index[-1]).all()
        assert (trade_log["Exit Date"] >= trade_log["Entry Date"]).all()

    print(f"\n--- {period_name.upper()}: CLOSED TRADE LOG ---")
    print(trade_log.to_string(index=False))

    print(f"\n--- {period_name.upper()}: CLOSED TRADE METRICS ---")
    for name, value in period["trade_metrics"].items():
        print(name, ":", value)

# ============================================================
# 6. ADAPTACIÓN TEMPORAL AL BLOQUE DE REGISTRO EXISTENTE
# ============================================================

train_results = train["backtest"]
train_strategy_metrics = train["strategy_metrics"]
train_trade_metrics = train["trade_metrics"]
train_buy_hold_metrics = (
    train["benchmarks"]["buy_hold_open_gross"]["metrics"]
)
train_buy_hold_net_metrics = (
    train["benchmarks"]["buy_hold_open_entry_cost"]["metrics"]
)

test_results = test["backtest"]
test_strategy_metrics = test["strategy_metrics"]
test_trade_metrics = test["trade_metrics"]
test_buy_hold_metrics = (
    test["benchmarks"]["buy_hold_open_gross"]["metrics"]
)
test_buy_hold_net_metrics = (
    test["benchmarks"]["buy_hold_open_entry_cost"]["metrics"]
)

# ============================================================
# 7. RESULTADOS ESTRUCTURADOS DEL EXPERIMENTO
# ============================================================

experiment_results = {
    "train": build_period_results(
        evaluation_index=train_results.index,
        strategy_metrics=train_strategy_metrics,
        closed_trade_metrics=train_trade_metrics,
        benchmark_metrics={
            "buy_hold_open_gross": train_buy_hold_metrics,
            "buy_hold_open_entry_cost": train_buy_hold_net_metrics,
        },
    ),
    "test": build_period_results(
        evaluation_index=test_results.index,
        strategy_metrics=test_strategy_metrics,
        closed_trade_metrics=test_trade_metrics,
        benchmark_metrics={
            "buy_hold_open_gross": test_buy_hold_metrics,
            "buy_hold_open_entry_cost": test_buy_hold_net_metrics,
        },
    ),
}

#Verificamos que cada apartado conserva el resultadod de su periodo.
for period_name, source_results in (
    ("train", train_results),
    ("test", test_results),
):
    period_record = experiment_results[period_name]

    assert period_record["period"]["rows"] == len(source_results), (
        f"{period_name}: incorrect evaluation row count."
    )

    recorded_final_value = (
        period_record["strategy"]["metrics"]["Final Value"]
    )

    assert recorded_final_value["status"] == "finite"

    assert (
        recorded_final_value["value"]
        == source_results["StrategyEquity"].iloc[-1]
    ), f"{period_name}: recorded final equity does not match the backtest."

#Probamos todo el conjunto con JSON estricto, sin escribir archivos.
results_json = json.dumps(
    experiment_results,
    indent=2,
    allow_nan=False,
)

assert json.loads(results_json) == experiment_results, (
    "Experiment results changed during the JSON round trip."
)

print("\nExperiment results integration chechks passed.")

#Completamos el mismo registro sin modificar el original.
completed_record = attach_experiment_results(
    experiment_record,
    experiment_results,
)

assert "results" not in experiment_record, (
    "The original metadata record must remain unchanged."
)

assert(
    completed_record["experiment_id"]
    == experiment_record["experiment_id"]
), "Attaching results must preserve the experiment identity."

assert completed_record["results"] == experiment_results, (
    "The completed record must contain the calculated results."
)

#Comprobamos metadatos y resultados juntos con JSON estricto.
completed_record_json = json.dumps(
    completed_record,
    indent=2,
    allow_nan=False,
)

assert json.loads(completed_record_json) == completed_record, (
    "The completed record changed during the JSON round trip."
)

print("\nCompleted experiment record checks passed.")
print("Experiment ID:", completed_record["experiment_id"])
print(
    "Uncommitted changes:",
    completed_record["code"]["working_tree_dirty"],
)

#Carpeta de salida local de los experimentos.
experiment_directory = project_root / "artifacts" / "experiments"

experiment_directory.mkdir(
    parents=True,
    exist_ok=True,
)

#Utilizamos el identificador ya creado: no generamos otro UUID.
experiment_path = (
    experiment_directory
    / f"{completed_record['experiment_id']}.json"
)

save_experiment_record(completed_record, experiment_path)

#Verificamos el contenido realmente escrito en disco.
with experiment_path.open("r", encoding="utf-8") as file:
    saved_record = json.load(file)

assert saved_record == completed_record, (
    "The saved experiment record does not match the completed record."
)

print("Experiment record saved:", experiment_path)