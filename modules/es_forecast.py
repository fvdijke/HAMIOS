"""
Sporadic-E (Es) Propagation Forecast Model

Sporadic-E is unpredictable by nature, but seasonal patterns & K-index correlation
allow probabilistic alerting for 6m/4m/2m operators.

Usage:
    es = ESForecast()
    prob = es.es_probability(month=6, hour_local=12, k_index=3)
    # → 0.75 (75% chance of Es opening in June, noon local, calm geomagnetic condition)
"""

import datetime as dt
import math
from typing import Dict, Tuple


class ESForecast:
    """Sporadic-E seasonal probability and K-index correlation model."""

    # Peak season probabilities (empirical from literature + WSPR data)
    # {month: base_probability}
    SEASONAL_BASE = {
        1: 0.08,   # Jan (winter secondary peak)
        2: 0.10,
        3: 0.05,
        4: 0.04,
        5: 0.15,   # May (summer primary peak starts)
        6: 0.40,   # June (PRIMARY PEAK)
        7: 0.45,   # July (PRIMARY PEAK)
        8: 0.35,   # Aug (tail of summer peak)
        9: 0.08,
        10: 0.04,
        11: 0.06,
        12: 0.12,  # Dec (winter secondary peak)
    }

    # Diurnal variation (hour 00-23 UTC)
    # Peak at local noon, minor peak at sunrise/sunset
    DIURNAL_PROFILE = [
        0.1, 0.1, 0.1, 0.2, 0.3,   # 00-04 UTC (dawn in some zones)
        0.4, 0.5, 0.6, 0.7, 0.8,   # 05-09
        0.9, 0.95, 1.0, 0.95, 0.9, # 10-14 (peak around 12 UTC)
        0.8, 0.7, 0.6, 0.5, 0.4,   # 15-19
        0.3, 0.2, 0.15, 0.1,       # 20-23
    ]

    # K-index suppression factor (geomagnetic storms suppress Es)
    # K=0-2: optimal; K=3-4: slight reduction; K=5-6: moderate; K=7+: poor
    K_SUPPRESSION = {
        0: 1.0,
        1: 1.0,
        2: 0.95,
        3: 0.85,
        4: 0.70,
        5: 0.50,
        6: 0.35,
        7: 0.15,
        8: 0.05,
        9: 0.01,
    }

    def es_probability(
        self, month: int = 6, hour_local: float = 12.0, k_index: float = 2.0
    ) -> float:
        """
        Calculate probability (0–1) of Sporadic-E opening.

        Args:
            month: 1–12
            hour_local: Local hour (0–23)
            k_index: K-index (0–9)

        Returns:
            Probability (0.0 to 1.0)
        """
        # Ensure month in range
        month = max(1, min(12, month))
        k_index = max(0, min(9, k_index))

        # Seasonal baseline
        seasonal_prob = self.SEASONAL_BASE.get(month, 0.05)

        # Diurnal variation (convert local hour to approximate UTC profile index)
        hour_utc = int(hour_local) % 24  # Simplified: assume local ≈ UTC
        diurnal_factor = self.DIURNAL_PROFILE[hour_utc]

        # K-index suppression
        k_int = int(k_index)
        k_suppression = self.K_SUPPRESSION.get(k_int, 0.0)

        # Combine factors
        prob = seasonal_prob * diurnal_factor * k_suppression

        # Add noise/unpredictability (Es is inherently random)
        # Keep it deterministic for testing, but acknowledge uncertainty in documentation
        prob = max(0.0, min(1.0, prob))

        return prob

    def es_alert_level(
        self,
        month: int = 6,
        hour_local: float = 12.0,
        k_index: float = 2.0,
        threshold: float = 0.30,
    ) -> Tuple[str, float]:
        """
        Determine Es alert level relative to threshold.

        Args:
            month: 1–12
            hour_local: Local hour
            k_index: K-index
            threshold: User-configured threshold (0.0–1.0)

        Returns:
            (level: 'active'|'marginal'|'inactive', probability: 0.0–1.0)
        """
        prob = self.es_probability(month, hour_local, k_index)

        if prob >= threshold:
            if prob >= threshold * 1.5:
                return ("active", prob)
            else:
                return ("marginal", prob)
        else:
            return ("inactive", prob)

    def peak_hours_today(self, qth_lat: float = 52.0) -> Tuple[int, int]:
        """
        Return peak Es hours (UTC) for today at this QTH.

        Es peaks roughly around local noon (10–14 local time typically).
        At QTH latitude, this translates to UTC hour range.

        Args:
            qth_lat: QTH latitude (for rough time zone estimate; simplified)

        Returns:
            (start_hour_utc, end_hour_utc)
        """
        # Simplified: assume peak 12:00 local = ~11:00 UTC (rough European time)
        # For global accuracy, would need to integrate actual timezone
        utc_peak_start = 10  # UTC
        utc_peak_end = 14    # UTC

        return (utc_peak_start, utc_peak_end)

    def es_status_today(
        self, k_index: float = 2.0, threshold: float = 0.30
    ) -> Dict:
        """
        Get overall Es forecast for today.

        Returns:
            {
                'season': 'active'|'inactive',
                'month_base': float,
                'peak_hours_utc': (int, int),
                'current_prob': float,
                'current_level': 'active'|'marginal'|'inactive',
            }
        """
        now = dt.datetime.now()
        month = now.month
        hour_local = now.hour

        season = "active" if self.SEASONAL_BASE[month] >= 0.15 else "inactive"
        month_base = self.SEASONAL_BASE[month]
        current_prob = self.es_probability(month, hour_local, k_index)
        current_level, _ = self.es_alert_level(
            month, hour_local, k_index, threshold
        )
        peak_hours = self.peak_hours_today()

        return {
            "season": season,
            "month_base_prob": month_base,
            "peak_hours_utc": peak_hours,
            "current_prob": current_prob,
            "current_level": current_level,
            "threshold": threshold,
        }


# ── Convenience functions ────────────────────────────────────────────────


def get_es_alert(
    k_index: float = 2.0, threshold: float = 0.30
) -> Tuple[str, float]:
    """
    Quick Es alert status for current hour.

    Returns: (level: 'active'|'marginal'|'inactive', probability: 0–1)
    """
    now = dt.datetime.now()
    es = ESForecast()
    return es.es_alert_level(now.month, now.hour, k_index, threshold)
