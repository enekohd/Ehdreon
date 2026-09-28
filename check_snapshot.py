from pathlib import Path
from src.data.loader import load_market_data


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

loaded_data = load_market_data(snapshot_path, metadata_path)

print("\nSnapshot structure, numeric and OHLC checks passed.")

print("\n--- LOADED SNAPSHOT ---")
print("Rows:", len(loaded_data))
print("First date:", loaded_data.index[0])
print("Last date:", loaded_data.index[-1])

print("\nIndex type:", type(loaded_data.index).__name__)

print("\nColumn types:")
print(loaded_data.dtypes)

print("\nFirst rows:")
print(loaded_data.head(3).to_string())