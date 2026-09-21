def apply_sma_strategies( data, fast_window=20, slow_window=50 ):

    data = data.copy()

    fast_column = f"SMA_{fast_window}"
    slow_column = f"SMA_{slow_window}"

    data[fast_column] = (
        data["Close"].rolling(fast_window).mean()
    )

    data[slow_column] = (
        data["Close"].rolling(slow_window).mean()
    )

    data["Signal"] = 0

    data.loc[
        data[fast_column] > data[slow_column],
        "Signal"
    ] = 1

    return data