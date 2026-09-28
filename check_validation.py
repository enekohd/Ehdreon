import pandas as pd

from src.data.validation import validate_market_data

dates = pd.to_datetime([
    "2024-01-02",
    "2024-01-03",
])

valid_data = pd.DataFrame({
        "Open": [100.0, 102.0],
        "High": [105.0, 106.0],
        "Low": [98.0, 101.0],
        "Close": [103.0, 104.0],
        "Volume": [1000, 1200],
    },
    index=dates,
)

original_data = valid_data.copy()

invalid_data = valid_data.copy()

invalid_data.loc[dates[0], "Close"] = 107.0

try:
    validate_market_data(invalid_data)

except ValueError as error:
    assert "Inconsistent OHLC prices" in str(error), (
        f"Unexpected validation error: {error}"
    )
    print("Invalid Close correctly rejected.")

else:
    raise AssertionError(
        "The validator accepted a Close greater than High."
    )

duplicate_dates_data = valid_data.copy()

duplicate_dates_data.index = pd.DatetimeIndex([
    dates[0],
    dates[0],
])

try:
    validate_market_data(duplicate_dates_data)

except ValueError as error:
    assert "duplicate dates." in str(error), (
        f"Unexpected validation error: {error}"
    )
    print("Duplicate dates correctly rejected.")

else:
    raise AssertionError(
        "The validator accepted duplicate dates."
    )

unsorted_dates = valid_data.iloc[::-1].copy()

try:
    validate_market_data(unsorted_dates)

except ValueError as error:
    assert "dates must be sorted chronologically" in str(error), (
        f"Unexpected validation error: {error}"
    )
    print("Unsorted dates correctly rejected.")

else:
    raise AssertionError(
        "The validator accepted unsorted dates."
    )

pd.testing.assert_frame_equal(valid_data, original_data)

print("Valid data accepted without modification.")