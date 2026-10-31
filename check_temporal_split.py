import pandas as pd

from src.research.splits import split_temporal_data


dates = pd.to_datetime([
    "2022-12-30",
    "2023-01-01",
    "2023-12-29",
    "2024-01-01",
])

data = pd.DataFrame(
    {"Close": [100.0, 101.0, 102.0, 103.0]},
    index=dates,
)

original_data = data.copy(deep=True)

partitions = split_temporal_data(
    data,
    validation_start="2023-01-01",
    test_start="2024-01-01",
)

pd.testing.assert_frame_equal(partitions["train"], data.iloc[:1])
pd.testing.assert_frame_equal(partitions["validation"], data.iloc[1:3])
pd.testing.assert_frame_equal(partitions["test"], data.iloc[3:])

#Reconstruiremos la entrada: mismas filas, valores y orden.
reconstructed = pd.concat([
    partitions["train"],
    partitions["validation"],
    partitions["test"],
])

pd.testing.assert_frame_equal(reconstructed, original_data)

#Modificar una particion no debe cambiar los datos originales.
partitions["train"].iloc[0,0] = -999.0

pd.testing.assert_frame_equal(data, original_data)

print("Temporal split boundary and preservation checks passed.")

#Los limites no coinciden con ninguna observacion.
session_data = pd.DataFrame(
        {"Close": [100.0, 101.0, 102.0, 103.0]},
    index=pd.to_datetime([
        "2022-12-30",
        "2023-01-02",
        "2023-12-29",
        "2024-01-02",
    ]),
)

session_partitions = split_temporal_data(
    session_data,
    validation_start="2023-01-01",
    test_start="2024-01-01",
)

pd.testing.assert_frame_equal(
    session_partitions["train"],
    session_data.iloc[:1],
)

pd.testing.assert_frame_equal(
    session_partitions["validation"],
    session_data[1:3],
)

pd.testing.assert_frame_equal(
    session_partitions["test"],
    session_data.iloc[3:],
)

print("Temporal split without exact boundary observations checks passed.")

duplicate_data = original_data.copy()
duplicate_data.index = pd.DatetimeIndex([
    dates[0], dates[0], dates[2], dates[3],
])

missing_date_data = original_data.copy()
missing_date_data.index = pd.DatetimeIndex([
    dates[0], pd.NaT, dates[2], dates[3],
])

invalid_cases = [
    (
        "Empty input",
        original_data.iloc[:0],
        "2023-01-01", "2024-01-01",
        ValueError, "Data must not be empty",
    ),
    (
        "Non-temporal index",
        original_data.reset_index(drop=True),
        "2023-01-01", "2024-01-01",
        TypeError, "DatetimeIndex",
    ),
    (
        "Unsorted index",
        original_data.iloc[::-1],
        "2023-01-01", "2024-01-01",
        ValueError, "chronological",
    ),
    (
        "Duplicate dates",
        duplicate_data,
        "2023-01-01", "2024-01-01",
        ValueError, "unique",
    ),
    (
        "Missing date",
        missing_date_data,
        "2023-01-01", "2024-01-01",
        ValueError, "missing",
    ),
    (
        "Timezone-aware index",
        original_data.tz_localize("UTC"),
        "2023-01-01", "2024-01-01",
        ValueError, "timezone-naive",
    ),
    (
        "Equal boundaries",
        original_data,
        "2023-01-01", "2023-01-01",
        ValueError, "must precede",
    ),
    (
        "Reversed boundaries",
        original_data,
        "2024-01-01", "2023-01-01",
        ValueError, "must precede",
    ),
    (
        "Invalid calendar date",
        original_data,
        "2023-02-30", "2024-01-01",
        ValueError, "valid YYYY-MM-DD",
    ),
    (
        "Wrong boundary type",
        original_data,
        20230101, "2024-01-01",
        TypeError, "must be a string",
    ),
    (
        "Empty TRAIN",
        original_data,
        "2022-01-01", "2024-01-01",
        ValueError, "train partition is empty",
    ),
    (
        "Empty VALIDATION",
        original_data,
        "2023-02-01", "2023-03-01",
        ValueError, "validation partition is empty",
    ),
    (
        "Empty TEST",
        original_data,
        "2023-01-01", "2025-01-01",
        ValueError, "test partition is empty",
    ),
]

for (
    name,
    input_data,
    validation_start,
    test_start,
    expected_error,
    expected_message,
) in invalid_cases:
    try:
        split_temporal_data(
            input_data,
            validation_start=validation_start,
            test_start=test_start,
        )
    except expected_error as error:
        assert expected_message in str(error), (
            f"{name}: unexpected error: {error}"
        )
    else:
        raise AssertionError(f"{name}: invalid input was accepted.")

print("Invalid temporal split inputs correctly rejected.")