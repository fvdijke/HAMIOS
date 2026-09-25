"""HAMIOS v5 — Uitleg (tooltips) bij het propagatie-advies.

Bouwt per onderdeel van het advies een tooltip in gewone taal op uit de cijfers:
waarom een band open is (MUF/LUF op het pad, dag/nacht op de controlepunten),
wat de waarnemingen zeggen, hoe het oordeel tot stand komt, en een leeswijzer
voor alle balkjes, percentages en symbolen.

Alle teksten via i18n (NL/EN); uitvoer is Qt rich text (HTML).
"""

from __future__ import annotations

from .i18n import tr

_GREEN, _BLUE, _DIM, _AMBER = "#4CAF50", "#4FC3F7", "#9AA3AE", "#C8A84B"
_SRC_KEYS = (("WSPR", "adv.x.src.wspr"), ("DX", "adv.x.src.dx"), ("PSK", "adv.x.src.psk"))


def _h(text: str) -> str:
    return f"<b>{text}</b>"


def _sources(d: dict) -> str:
    parts = [f"{tr(k)} {d[s]}" for s, k in _SRC_KEYS if d.get(s)]
    return " · ".join(parts) if parts else "—"


def _muf_line(r) -> str:
    """Positie van de band t.o.v. de MUF op het pad + vuistregel."""
    if r.path_muf <= 0:
        return ""
    ratio = r.band_mhz / r.path_muf
    if ratio <= 0.85:
        key = "adv.x.muf.well_below"
    elif ratio <= 1.0:
        key = "adv.x.muf.just_below"
    elif ratio <= 1.15:
        key = "adv.x.muf.above"
    else:
        key = "adv.x.muf.far_above"
    return (tr("adv.x.muf", muf=r.path_muf, band=r.band, mhz=r.band_mhz,
               pct=int(round(100 * ratio))) + " " + tr(key)
            + f"<br><span style='color:{_DIM}'>&nbsp;&nbsp;{tr('adv.x.muf.rule')}</span>")


def _luf_line(r) -> str:
    if r.path_luf <= 0:
        return ""
    ratio = r.band_mhz / r.path_luf
    key = ("adv.x.luf.far" if ratio >= 2 else "adv.x.luf.above" if ratio >= 1.2
           else "adv.x.luf.near" if ratio >= 1.0 else "adv.x.luf.below")
    return tr("adv.x.luf", luf=r.path_luf, mhz=r.band_mhz) + " " + tr(key)


def _cp_line(r) -> str:
    days = list(r.cp_day)
    if not days:
        return ""
    if len(days) == 1:
        key = "adv.x.cp.one_day" if days[0] else "adv.x.cp.one_night"
    elif all(days):
        key = "adv.x.cp.all_day"
    elif not any(days):
        key = "adv.x.cp.all_night"
    else:
        key = "adv.x.cp.mixed"
    return tr(key)


def rec_tooltip(r, region_name: str, station: str, snr_db: float, until_txt: str) -> str:
    """Volledige uitleg bij één aanbeveling."""
    status_key, clr = {
        "confirmed": ("adv.x.status.confirmed", _GREEN),
        "observed":  ("adv.x.status.observed", _BLUE),
    }.get(r.confidence, ("adv.x.status.model", _AMBER))
    km = f"{r.dist_km:,}".replace(",", ".")
    lines = [
        _h(f"{r.band} → {region_name}"),
        tr("adv.x.path1", km=km) if r.hops == 1 else tr("adv.x.path", km=km, hops=r.hops),
        "",
        f"<b style='color:{clr}'>{tr(status_key)}</b>",
        tr("adv.x.pcts", eff=r.eff, p=r.pct),
        "",
        _h(tr("adv.x.why")),
    ]
    for ln in (_muf_line(r), _luf_line(r), _cp_line(r)):
        if ln:
            lines.append("• " + ln)
    if getattr(r, "absorption", 0) >= 1:
        lines.append("• " + tr("adv.x.absorption", haf=f"{r.absorption:.0f}"))
    lines += ["", _h(tr("adv.x.observed")),
              "• " + tr("adv.x.spots", n=r.obs, src=_sources(r.sources))]
    if r.confidence == "confirmed":
        lines.append("→ " + tr("adv.x.obs.confirms"))
    elif r.confidence == "observed":
        lines.append("→ " + tr("adv.x.obs.beats_model"))
    else:
        lines.append("→ " + tr("adv.x.obs.none"))
    lines += ["", _h(tr("adv.x.window"))]
    if until_txt:
        lines.append(tr("adv.x.until", t=until_txt))
    elif r.pct >= 50:
        lines.append(tr("adv.x.open_long"))
    else:
        lines.append(tr("adv.x.no_window"))
    lines += ["", _h(tr("adv.x.station")),
              tr("adv.x.station_line", station=station, snr=f"{snr_db:+.0f}"),
              "", f"<i style='color:{_DIM}'>{tr('adv.click_tip')}</i>"]
    return "<br>".join(lines)


def verdict_tooltip(adv, event_texts: list[str]) -> str:
    lvl = tr(f"adv.level.{adv.level}")
    lines = [_h(tr("adv.x.verdict.title", level=lvl)),
             tr("adv.x.verdict.count", n=adv.good),
             f"<span style='color:{_DIM}'>{tr('adv.x.verdict.scale')}</span>"]
    if adv.level != adv.level_raw:
        lines += ["", tr("adv.x.verdict.lowered", frm=tr(f"adv.level.{adv.level_raw}"), to=lvl)]
        lines += ["• " + t for t in event_texts]
    lines += ["", f"<span style='color:{_DIM}'>{tr('adv.x.verdict.events_rule')}</span>"]
    return "<br>".join(lines)


def sub_tooltip(adv, iono_age_min: int | None) -> str:
    lines = [_h(f"MUF {adv.muf} MHz"), tr("adv.x.sub.muf")]
    if adv.source != "model":
        lines.append(tr("adv.x.sub.measured", name=adv.source,
                        age=iono_age_min if iono_age_min is not None else "?"))
    else:
        lines.append(tr("adv.x.sub.model"))
    lines += ["", _h(tr("adv.x.sub.obs_title", n=adv.obs_total)),
              _sources(adv.obs_by_source), tr("adv.x.sub.obs_rule")]
    return "<br>".join(lines)


def event_tooltip(ev) -> str:
    params = dict(ev.params)
    if "sid" in params:
        params["name"] = tr(f"meteor.{params['sid']}")
    return "<br>".join([_h(tr(ev.key, **params)), "", tr(ev.key + ".why")])


def timeline_tooltip(item) -> str:
    key = ("adv.x.tl.grayline" if item.key in ("adv.tl.sunrise", "adv.tl.sunset")
           else "adv.x.tl.band")
    return tr(key)


def trend_tooltip() -> str:
    return "<br>".join([tr("adv.x.trend"), "", tr("adv.x.es")])


def reading_guide() -> str:
    """Leeswijzer voor het hele paneel (ⓘ)."""
    keys = ["adv.guide.title", "", "adv.guide.verdict", "adv.guide.sub", "",
            "adv.guide.recs", "adv.guide.bar", "adv.guide.pct", "adv.guide.conf",
            "adv.guide.when", "", "adv.guide.events", "adv.guide.timeline",
            "adv.guide.trends", "", "adv.guide.click"]
    return "<br>".join(tr(k) if k else "" for k in keys)
