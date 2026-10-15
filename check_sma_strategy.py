import numpy as np
import pandas as pd

from src.strategies.sma_strategies import apply_sma_strategies

dates = pd.date_range("2024-01-01", periods=5, freq="D")

data = pd.DataFrame(
    {"Close": [10.0, 10.0, 10.0, 13.0, 7.0]},
    index=dates,
)

original_data = data.copy(deep=True)

results = apply_sma_strategies(
    data,
    fast_window=2,
    slow_window=3,
)

# Medias esperadas calculadas independientemente.
np.testing.assert_allclose(
    results["SMA_2"].to_numpy(),
    [np.nan, 10.0, 10.0, 11.5, 10.0],
    rtol=0,
    atol=1e-12,
    equal_nan=True,
)

np.testing.assert_allclose(
    results["SMA_3"].to_numpy(),
    [np.nan, np.nan, 10.0, 11.0, 10.0],
    rtol=0,
    atol=1e-12,
    equal_nan=True,
)

np.testing.assert_array_equal(
    results["Signal"].to_numpy(),
    [0, 0, 0, 1, 0],
)

#La estrategia no debe modificar los datos recibidos.
print("SMA values, warm-up and equality checks passed.")

#Alterar un cierre futuro no debe cambiar resultados anteriores.
changed_data = data.copy(deep=True)
changed_data.loc[dates[-1], "Close"] = 1000.0

changed_results = apply_sma_strategies(
    changed_data,
    fast_window=2,
    slow_window=3,
)

pd.testing.assert_frame_equal(
    results[["SMA_2", "SMA_3", "Signal"]].iloc[:-1],
    changed_results[["SMA_2", "SMA_3", "Signal"]].iloc[:-1],
)

print("SMA future_change isolation checks passed.")