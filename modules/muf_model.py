"""
MUF (Maximum Usable Frequency) & LUF (Lowest Usable Frequency) Forecast Model
Based on IRI-2016 simplified algorithm + solar/geomagnetic parameters.

Usage:
    model = MUFModel(qth_lat=52.0, qth_lon=5.0)
    muf_dict = model.forecast_day(sfi=150, ssn=100, k_index=4, distance_km=5000)
    # → {'10:00': 24.5, '11:00': 25.2, ...}
"""

import math
import datetime as dt
from .typing import Dict, Tuple


class MUFModel:
    """Vereenvoudigde IRI-2016 MUF/LUF calculator."""

    # HF bands (name, center MHz)
    BANDS = [
        ("160m", 1.8),
        ("80m", 3.5),
        ("60m", 5.3),
        ("40m", 7.0),
        ("30m", 10.1),
        ("20m", 14.0),
        ("17m", 18.1),
        ("15m", 21.2),
        ("12m", 24.9),
        ("10m", 28.0),
    ]

    def __init__(self, qth_lat: float = 52.0, qth_lon: float = 5.0):
        """
        Initialize MUF model for a QTH.

        Args:
            qth_lat: QTH latitude (-90 to 90)
            qth_lon: QTH longitude (-180 to 180)
        """
        self.qth_lat = qth_lat
        self.qth_lon = qth_lon

    def forecast_day(
        self,
        sfi: float = 90.0,
        ssn: float = 50.0,
        k_index: float = 2.0,
        distance_km: float = 5000.0,
    ) -> Dict[int, Dict[str, float]]:
        """
        Forecast MUF/LUF for each hour of the day.

        Args:
            sfi: Solar Flux Index (70–300)
            ssn: Sunspot Number (0–200+)
            k_index: K-index (0–9)
            distance_km: Target distance (1000–10000 km, default 5000 km global)

        Returns:
            Dict: {hour: {'foF2': MHz, 'muf': MHz, 'luf': MHz, 'quality': 'good'|'fair'|'poor'}}
        """
        result = {}
        now_utc = dt.datetime.now(dt.timezone.utc)

        for hour in range(24):
            local_hour = (hour + self._utc_offset_hours()) % 24
            foF2 = self._calc_foF2(sfi, ssn, k_index, local_hour)
            muf = self._calc_muf(foF2, distance_km, self.qth_lat)
            luf = self._calc_luf(foF2, self.qth_lat)
            quality = self._quality_from_muf(muf, sfi, k_index)

            result[hour] = {
                "foF2": round(foF2, 2),
                "muf": round(muf, 2),
                "luf": round(luf, 2),
                "quality": quality,
            }

        return result

    def muf_for_bands(
        self,
        sfi: float = 90.0,
        ssn: float = 50.0,
        k_index: float = 2.0,
        distance_km: float = 5000.0,
    ) -> Dict[int, Dict[str, bool]]:
        """
        Determine if each band is open for the next 24 hours.

        Returns:
            Dict: {hour: {band_name: True|False}}
        """
        forecast = self.forecast_day(sfi, ssn, k_index, distance_km)
        result = {}

        for hour, data in forecast.items():
            muf = data["muf"]
            result[hour] = {}
            for band_name, center_mhz in self.BANDS:
                # Band open if MUF > center frequency
                result[hour][band_name] = muf > center_mhz

        return result

    # ── Internal calculations ─────────────────────────────────────────────

    def _utc_offset_hours(self) -> float:
        """Get local UTC offset in hours (accounting for DST if possible)."""
        now_utc = dt.datetime.now(dt.timezone.utc)
        now_local = dt.datetime.now()
        offset = (now_local.replace(tzinfo=None) - now_utc.replace(tzinfo=None)).total_seconds() / 3600
        return offset

    def _calc_foF2(
        self, sfi: float, ssn: float, k_index: float, local_hour: float
    ) -> float:
        """
        Calculate critical frequency of F2 layer (foF2 in MHz).

        Based on:
        - SFI (solar activity) → main driver
        - K-index (geomagnetic disturbance) → suppresses foF2
        - Local hour (diurnal variation) → peaks at noon local time
        - QTH latitude (auroral zone effects)
        """
        # Base foF2 from SFI (empirical: SFI 70 → 3 MHz, SFI 300 → 15 MHz)
        foF2_base = 2.5 + (sfi - 70.0) * 0.035

        # Diurnal variation (peaks at ~13:00 local, minimum at ~04:00)
        hour_angle = (local_hour - 13.0) * 15.0 * math.pi / 180.0
        diurnal_factor = 1.0 + 0.35 * math.cos(hour_angle)

        # K-index suppression (high K → lower foF2)
        k_suppression = 1.0 - (k_index * 0.08)  # K=9 reduces by ~72%
        k_suppression = max(0.3, k_suppression)  # Floor at 30%

        # Latitude effect (auroral zone: lower foF2 at high latitudes)
        lat_rad = math.radians(abs(self.qth_lat))
        latitude_factor = 1.0 - 0.15 * math.cos(lat_rad)  # Slight reduction at equator

        foF2 = foF2_base * diurnal_factor * k_suppression * latitude_factor
        return max(2.0, foF2)  # Floor at 2 MHz

    def _calc_muf(self, foF2: float, distance_km: float, qth_lat: float) -> float:
        """
        Calculate MUF (Maximum Usable Frequency) from foF2.

        MUF = foF2 / cos(theta)
        where theta is the ray angle to reach target at distance.

        For 1-hop: assume 100 km F-layer height → spherical geometry
        """
        R = 6371.0  # Earth radius (km)
        h = 300.0  # F2 layer height (km)

        # Skip angle (angular distance / 2)
        skip_angle_deg = math.degrees(distance_km / (2.0 * (R + h)))

        # Ray angle (incidence angle)
        ray_angle_rad = math.radians(90.0 - skip_angle_deg)
        cos_ray = max(0.1, math.cos(ray_angle_rad))  # Avoid division by zero

        muf = foF2 / cos_ray

        # Multi-hop scaling for short distances
        if distance_km < 1000:
            # Close-in: lower frequencies work better (lower angle)
            muf *= 0.85

        return muf

    def _calc_luf(self, foF2: float, qth_lat: float) -> float:
        """
        Calculate LUF (Lowest Usable Frequency).

        Simple approximation: LUF ≈ 0.1 × foF2 (D-layer absorption floor)
        """
        luf = max(0.5, foF2 * 0.08)  # ~8% of foF2, minimum 0.5 MHz
        return luf

    def _quality_from_muf(self, muf: float, sfi: float, k_index: float) -> str:
        """Rate band quality based on MUF and geomagnetic conditions."""
        if k_index >= 6:
            return "poor"  # Storm: absorption high
        if muf < 3.0:
            return "poor"  # Very low MUF
        if sfi < 80 or muf < 10.0:
            return "fair"
        if sfi >= 140 and muf >= 20.0 and k_index <= 3:
            return "good"
        return "fair"


# ── Convenience functions ────────────────────────────────────────────────


def get_muf_status(
    qth_lat: float,
    qth_lon: float,
    sfi: float = 90.0,
    ssn: float = 50.0,
    k_index: float = 2.0,
) -> Dict:
    """
    One-shot MUF forecast for current hour.

    Returns: {band_name: {'muf': MHz, 'luf': MHz, 'open': True|False}}
    """
    model = MUFModel(qth_lat, qth_lon)
    now_utc = dt.datetime.now(dt.timezone.utc)
    forecast = model.forecast_day(sfi, ssn, k_index)
    current_hour = now_utc.hour

    if current_hour not in forecast:
        current_hour = 0

    current_data = forecast[current_hour]
    muf = current_data["muf"]
    luf = current_data["luf"]

    result = {}
    for band_name, center_mhz in MUFModel.BANDS:
        result[band_name] = {
            "muf": muf,
            "luf": luf,
            "open": muf > center_mhz,
            "quality": current_data["quality"],
        }

    return result
