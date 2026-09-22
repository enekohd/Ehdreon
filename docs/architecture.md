main.py
    ↓
coordina todo


sma_strategies.py
    ↓
genera SIGNAL


backtester.py
    ↓
Signal → Position
Position → Trades
Position → Returns
Returns → Equity


metrics.py
    ↓
mide el rendimiento


trades.py
    ↓
reconstruye y analiza operaciones

Estas son las reglas de tu implementación actual:
\[
Position_t=Signal_{t-1}
\]\[
Trade_t=|Position_t-Position_{t-1}|
\]\[
StrategyReturn_t
=
Position_{t-1}\cdot OpenReturn_t
-
Trade_t\cdot0.001
\]\[
Equity_t=Equity_{t-1}(1+StrategyReturn_t)
\]