# Trading Bot Evolution Roadmap

## Iteration Philosophy

This project follows a continuous evolution approach powered by quantitative research
and the EvoMap GEP (Genome Evolution Protocol). Every iteration must be:

1. **Data-driven**: Changes backed by backtest results, not intuition
2. **Risk-bounded**: No change may increase max drawdown beyond configured limits
3. **Measurable**: Every strategy change must show improvement in Sharpe or Sortino ratio
4. **Reversible**: All changes tracked in version control with rollback capability

## Architecture Principles

- **Platform-agnostic**: All trading logic operates through `ExchangeAdapter` abstraction
- **Strategy-decoupled**: Strategies are pure signal generators, independent of execution
- **Regime-aware**: Ensemble strategy adapts to market conditions automatically
- **Performance-first**: OHLCV caching, numpy-accelerated calculations, minimal API calls

## Evolution Stages

### Stage 1: Foundation (Complete)
- [x] Core exchange abstraction layer (ExchangeAdapter)
- [x] CCXT adapter (100+ exchanges)
- [x] Paper trading adapter
- [x] 4 base strategies (RSI+MACD, Mean Reversion, Grid, DCA Momentum)
- [x] Risk management (position sizing, stop-loss, drawdown limits)
- [x] Backtesting engine with Sharpe/Sortino metrics
- [x] Market regime detection (ADX + BB + EMA + ATR)
- [x] Ensemble strategy with regime-weighted voting

### Stage 2: Intelligence (Next)
- [ ] Adaptive indicators (KAMA, Mesa Adaptive)
- [ ] Order flow analysis (volume imbalance, VWAP deviation)
- [ ] Multi-timeframe analysis (15m signals confirmed by 1h/4h trend)
- [ ] ML-based signal filtering (lightweight gradient boosting)
- [ ] Walk-forward optimization (rolling window parameter tuning)

### Stage 3: Resilience
- [ ] Circuit breakers for flash crashes
- [ ] Correlation-based portfolio risk
- [ ] Slippage-aware execution (TWAP/VWAP splitting)
- [ ] Exchange failover (auto-switch between exchanges)

### Stage 4: Scale
- [ ] WebSocket real-time data feed
- [ ] Multi-pair portfolio management
- [ ] Cross-exchange arbitrage detection
- [ ] Dashboard with real-time P&L visualization

## Evolver Integration

The project uses [evolver](https://github.com/autogame-17/evolver) for automated
self-improvement cycles via the GEP protocol:

```bash
cd .evolver && node index.js --loop
```

Strategy: `innovate` - continuously search for improvements in:
- Strategy parameters (RSI thresholds, MACD periods, etc.)
- Risk parameters (position sizing, stop distances)
- New indicator combinations
- Regime detection accuracy
