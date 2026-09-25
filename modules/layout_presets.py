"""HAMIOS v5 — Standaardindelingen (tegelbomen, zie tiling.py).

  central    "Kaart centraal"  dagelijks gebruik: banden links, advies rechts,
                                grafieken en live-data onder de kaart
  operating  "Operating"       kaart zo groot mogelijk, rest in tabbladen
  analysis   "Analyse"         grafieken en historie groot, kaart kleiner

De kaarthoogte wordt uit de beschikbare ruimte berekend, zodat de kaart
(equirectangulair, 2:1) zonder lege randen past. Op kleine schermen
(< 1500 × 850) krijgt elke indeling een compacte variant met meer tabbladen.
"""

from __future__ import annotations

PRESETS = ("central", "operating", "analysis")
SMALL_W, SMALL_H = 1500, 850


def _tabs(*pids, active=None) -> dict:
    return {"t": list(pids), "a": active or pids[0]}


def _p(pid) -> dict:
    return {"p": pid}


def _map_height(map_w_frac: float, w: int, h: int, lo=0.45, hi=0.78) -> float:
    """Hoogtefractie waarbij de kaart ~2:1 is, begrensd voor de buren."""
    if w <= 0 or h <= 0:
        return 0.62
    return max(lo, min(hi, (map_w_frac * w / 2) / h))


def preset_tree(name: str, w: int, h: int) -> dict:
    """Tegelboom voor preset `name` op een desktop van w × h pixels."""
    small = w < SMALL_W or h < SMALL_H
    if name == "operating":
        return _operating(w, h, small)
    if name == "analysis":
        return _analysis(w, h, small)
    return _central(w, h, small)


def _central(w, h, small) -> dict:
    if small:
        mh = _map_height(0.72, w, h)
        return {"o": "h", "s": [0.72, 0.28], "c": [
            {"o": "v", "s": [mh, 1 - mh], "c": [
                _p("worldmap"),
                _tabs("kp_48h", "bz_24h", "xray_24h", "solar_hist", "band_hist",
                      "dx_spots", "wspr_feed")]},
            {"o": "v", "s": [0.45, 0.55], "c": [
                _p("prop_adv"),
                _tabs("band_rel", "band_sched", "storm_fc", "solar", "lightning", "alerts",
                      "ionosondes", "sat_passes")]},
        ]}
    mh = _map_height(0.61, w, h)
    return {"o": "h", "s": [0.17, 0.61, 0.22], "c": [
        {"o": "v", "s": [0.42, 0.38, 0.20], "c": [
            _p("band_rel"),
            _p("band_sched"),
            _tabs("band_hist", "storm_fc")]},
        {"o": "v", "s": [mh, 1 - mh], "c": [
            _p("worldmap"),
            {"o": "h", "s": [0.45, 0.55], "c": [
                _tabs("kp_48h", "bz_24h", "xray_24h", "solar_hist"),
                _tabs("dx_spots", "wspr_feed", "sat_passes", "ionosondes")]}]},
        {"o": "v", "s": [0.42, 0.22, 0.20, 0.16], "c": [
            _p("prop_adv"), _p("alerts"), _p("solar"), _p("lightning")]},
    ]}


def _operating(w, h, small) -> dict:
    mw = 0.78 if small else 0.76
    mh = _map_height(mw, w, h, hi=0.80)
    return {"o": "h", "s": [mw, 1 - mw], "c": [
        {"o": "v", "s": [mh, 1 - mh], "c": [
            _p("worldmap"),
            _tabs("band_rel", "band_sched", "kp_48h", "bz_24h",
                  "xray_24h", "band_hist", "solar_hist", "ionosondes", "sat_passes")]},
        {"o": "v", "s": [0.45, 0.55], "c": [
            _p("prop_adv"),
            _tabs("dx_spots", "wspr_feed", "alerts", "lightning", "solar", "storm_fc")]},
    ]}


def _analysis(w, h, small) -> dict:
    if small:
        top = _map_height(0.55, w, h, lo=0.35, hi=0.60)
        return {"o": "v", "s": [top, 1 - top], "c": [
            {"o": "h", "s": [0.55, 0.45], "c": [
                _p("worldmap"),
                _tabs("prop_adv", "dx_spots", "wspr_feed", "alerts")]},
            {"o": "h", "s": [0.5, 0.5], "c": [
                _tabs("kp_48h", "bz_24h", "xray_24h", "solar_hist"),
                _tabs("band_rel", "band_sched", "band_hist",
                      "solar", "storm_fc", "lightning", "ionosondes", "sat_passes")]},
        ]}
    top = _map_height(0.45, w, h, lo=0.35, hi=0.55)
    return {"o": "v", "s": [top, 1 - top], "c": [
        {"o": "h", "s": [0.45, 0.25, 0.30], "c": [
            _p("worldmap"),
            _p("prop_adv"),
            _tabs("dx_spots", "wspr_feed", "alerts", "sat_passes")]},
        {"o": "h", "s": [0.2, 0.2, 0.2, 0.2, 0.2], "c": [
            {"o": "v", "s": [0.5, 0.5], "c": [_p("kp_48h"), _p("bz_24h")]},
            {"o": "v", "s": [0.5, 0.5], "c": [_p("xray_24h"), _p("solar_hist")]},
            {"o": "v", "s": [0.5, 0.5], "c": [_p("band_hist"), _p("storm_fc")]},
            {"o": "v", "s": [0.5, 0.5], "c": [_p("band_rel"), _p("band_sched")]},
            _tabs("solar", "ionosondes", "lightning")]},
    ]}
