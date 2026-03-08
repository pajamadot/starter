"""Ensemble Strategy — combines multiple strategies with regime-aware weighting.

Instead of relying on a single strategy, the ensemble:
1. Detects the current market regime (trending, ranging, volatile)
2. Runs all sub-strategies in parallel
3. Weights their signals by regime suitability
4. Produces a consensus signal

This is the recommended strategy for production use.
"""

import pandas as pd
from src.strategies.base import BaseStrategy, TradeSignal, Signal
from src.strategies.rsi_macd import RsiMacdStrategy
from src.strategies.mean_reversion import MeanReversionStrategy
from src.strategies.grid_trading import GridTradingStrategy
from src.strategies.dca_momentum import DCAMomentumStrategy
from src.strategies.regime import detect_regime, get_regime_strategy_weights, MarketRegime
from src.utils.logger import setup_logger

logger = setup_logger("strategy.ensemble")


class EnsembleStrategy(BaseStrategy):
    """Regime-adaptive ensemble of all available strategies."""

    strategy_name = "Ensemble"

    def __init__(self, config: dict):
        super().__init__(config)
        self.sub_strategies: dict[str, BaseStrategy] = {
            "rsi_macd": RsiMacdStrategy(config),
            "mean_reversion": MeanReversionStrategy(config),
            "grid": GridTradingStrategy(config),
            "dca_momentum": DCAMomentumStrategy(config),
        }
        self.min_consensus = self.params.get("ensemble_min_consensus", 0.4)
        self._last_regime = MarketRegime.RANGING

    def generate_signal(self, df: pd.DataFrame) -> str:
        sig = self.generate_rich_signal(df)
        return sig.signal.value

    def generate_rich_signal(self, df: pd.DataFrame) -> TradeSignal:
        # 1. Detect market regime
        regime = detect_regime(df)
        if regime != self._last_regime:
            logger.info(f"Regime change: {self._last_regime.value} -> {regime.value}")
            self._last_regime = regime

        # 2. Get strategy weights for this regime
        weights = get_regime_strategy_weights(regime)

        # 3. Collect signals from all sub-strategies
        buy_score = 0.0
        sell_score = 0.0
        total_weight = 0.0
        reasons = []

        for name, strategy in self.sub_strategies.items():
            weight = weights.get(name, 0.5)
            try:
                signal = strategy.generate_rich_signal(df)
            except Exception as e:
                logger.debug(f"Strategy {name} error: {e}")
                continue

            total_weight += weight

            if signal.signal == Signal.BUY:
                contribution = weight * signal.confidence
                buy_score += contribution
                reasons.append(f"{name}:BUY({signal.confidence:.1f})*{weight:.1f}")
            elif signal.signal == Signal.SELL:
                contribution = weight * signal.confidence
                sell_score += contribution
                reasons.append(f"{name}:SELL({signal.confidence:.1f})*{weight:.1f}")

        if total_weight == 0:
            return TradeSignal(Signal.HOLD, 0.0, "No strategy data")

        # 4. Normalize scores
        buy_consensus = buy_score / total_weight
        sell_consensus = sell_score / total_weight

        reason_str = f"Regime={regime.value} | " + " ".join(reasons)

        # 5. Produce consensus signal
        if buy_consensus >= self.min_consensus and buy_consensus > sell_consensus:
            logger.info(f"ENSEMBLE BUY | consensus={buy_consensus:.2f} | {reason_str}")
            price = float(df.iloc[-1]["close"])
            return TradeSignal(
                Signal.BUY, min(1.0, buy_consensus),
                reason_str, entry_price=price,
                metadata={"regime": regime.value, "consensus": buy_consensus},
            )

        if sell_consensus >= self.min_consensus and sell_consensus > buy_consensus:
            logger.info(f"ENSEMBLE SELL | consensus={sell_consensus:.2f} | {reason_str}")
            price = float(df.iloc[-1]["close"])
            return TradeSignal(
                Signal.SELL, min(1.0, sell_consensus),
                reason_str, entry_price=price,
                metadata={"regime": regime.value, "consensus": sell_consensus},
            )

        return TradeSignal(
            Signal.HOLD, 0.0,
            f"Regime={regime.value} buy={buy_consensus:.2f} sell={sell_consensus:.2f}"
        )
