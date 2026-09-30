"""
HAMIOS — Propagatie-overzicht (de kaartjes van het advies-paneel van vóór v5.7)

Elf korte kaartjes in drie kolommen: beste banden, geomagnetische toestand,
zonactiviteit, zonnewind, flares, dagdeel, mode/vermogen, aurora-absorptie,
sporadic-E, DX-routes en een algeheel oordeel. Een kaartje waarvan de inhoud
verandert krijgt PULSE_S (5 min) een knipperende stip, ook als het paneel in
die tijd opnieuw wordt opgebouwd.

De bandpercentages en dag/nacht komen uit het gekalibreerde model (dezelfde
cijfers als 'Banden nu'), niet meer uit de oude vuistregel.
"""

import datetime as _dt

from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
                               QLabel, QFrame, QScrollArea)

from .i18n import tr, language_changed
from .theme import ACCENT, BG_PANEL, BG_SURFACE, TEXT_BODY, TEXT_DIM


class _PulseDot(QLabel):
    """Gele stip (●) bij een kaartje dat kort geleden veranderde. Het knipperen
    doet het paneel met één gedeelde timer (zie PropTipsWidget._pulse)."""

    def __init__(self, parent=None):
        super().__init__("●", parent)
        self.setFont(QFont("Segoe UI", 8))
        self.setAlignment(Qt.AlignTop | Qt.AlignRight)
        self.setFixedWidth(12)

    def set_alpha(self, a: int):
        self.setStyleSheet(f"color: rgba(255,204,0,{a}); background: transparent;")


class PropTipsWidget(QWidget):
    """Propagatie-overzicht in kaartjes."""

    CARD_H = 72
    PULSE_S = 300      # zo lang knippert een gewijzigd kaartje (s), ongeacht verversingen
    _ALPHAS = [255, 200, 130, 70, 40, 70, 130, 200]
    CARD_MIN_W = 190   # kolommen: zoveel kaartjes van deze breedte als er passen (1–3)

    def __init__(self, cfg=None, parent=None):
        super().__init__(parent)
        self._cfg = cfg
        self._solar: dict = {}
        self._hashes: dict = {}       # kaartsleutel → hash(inhoud)
        self._changed_at: dict = {}   # kaartsleutel → monotonic tijd van de wijziging
        self._had_data = False        # eerste gegevens ≠ wijziging
        self._relang = False          # taalwissel ≠ wijziging
        self._dots: list = []         # (sleutel, _PulseDot)
        self._phase = 0
        self._pulse_timer = QTimer(self)
        self._pulse_timer.timeout.connect(self._pulse)
        self._cards: list = []
        self._cols = 3
        v = QVBoxLayout(self)
        v.setContentsMargins(4, 4, 4, 4)
        v.setSpacing(4)
        self._cards_widget = QWidget()
        self._cards_widget.setStyleSheet(f"background: {BG_PANEL};")
        self._grid = QGridLayout(self._cards_widget)
        self._grid.setSpacing(4)
        self._grid.setAlignment(Qt.AlignTop)
        # Scrollen i.p.v. samenpersen: in een laag paneel blijft elke tekst heel
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QScrollArea.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll.setStyleSheet(f"QScrollArea {{ background: {BG_PANEL}; border: none; }}")
        scroll.setWidget(self._cards_widget)
        v.addWidget(scroll, 1)

        # Dagdeel, Es-venster en DX-routes hangen van de klok af
        self._clock = QTimer(self)
        self._clock.timeout.connect(self._rebuild)
        self._clock.start(5 * 60_000)
        language_changed.connect(self._on_language)
        self._rebuild()

    def _on_language(self, _lang=None):
        """Andere taal = andere tekst, maar geen inhoudelijke wijziging."""
        self._relang = True
        self._rebuild()

    def _cols_for_width(self) -> int:
        return max(1, min(3, (self.width() - 8) // self.CARD_MIN_W))

    def resizeEvent(self, event):
        super().resizeEvent(event)
        cols = self._cols_for_width()
        if cols != self._cols:
            self._cols = cols
            self._place_cards()

    def _place_cards(self):
        for card in self._cards:
            self._grid.removeWidget(card)
        for i, card in enumerate(self._cards):
            self._grid.addWidget(card, i // self._cols, i % self._cols)
        for c in range(3):
            self._grid.setColumnStretch(c, 1 if c < self._cols else 0)

    def set_cfg(self, cfg):
        self._cfg = cfg
        self._rebuild()

    def set_data(self, solar: dict):
        self._solar = solar or {}
        self._rebuild()

    # ── Kaarten ───────────────────────────────────────────────────────────────
    def _rebuild(self):
        import time
        tips = self._build_tips()
        now = time.monotonic()
        has_data = bool(self._solar)
        track = self._had_data and has_data and not self._relang
        new_hashes = {}
        for key, icon, text, color in tips:
            h = hash((icon, text))
            if track and self._hashes.get(key) != h:
                self._changed_at[key] = now
            new_hashes[key] = h
        self._hashes = new_hashes
        self._had_data = self._had_data or has_data
        self._relang = False
        self._changed_at = {k: t for k, t in self._changed_at.items()
                            if k in new_hashes and now - t < self.PULSE_S}

        while self._grid.count():
            item = self._grid.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        self._cards, self._dots = [], []
        for key, icon, text, color in tips:
            card, dot = self._make_card(icon, text, color, key in self._changed_at)
            self._cards.append(card)
            if dot is not None:
                self._dots.append((key, dot))
        self._cols = self._cols_for_width() if self.width() > 50 else self._cols
        self._place_cards()
        self._pulse()
        if self._dots and not self._pulse_timer.isActive():
            self._pulse_timer.start(150)

    def _pulse(self):
        """Eén timer voor alle stippen; een stip verdwijnt na PULSE_S."""
        import time
        now = time.monotonic()
        a = self._ALPHAS[self._phase % len(self._ALPHAS)]
        self._phase += 1
        alive = []
        for key, dot in self._dots:
            if now - self._changed_at.get(key, 0) < self.PULSE_S:
                dot.set_alpha(a)
                alive.append((key, dot))
            else:
                dot.hide()
        self._dots = alive
        if not alive:
            self._pulse_timer.stop()

    def _make_card(self, icon: str, text: str, color: str, changed: bool):
        """(QFrame, _PulseDot | None)"""
        frame = QFrame()
        frame.setMinimumHeight(self.CARD_H)
        frame.setStyleSheet(f"QFrame {{ background: {BG_SURFACE}; border-radius: 2px; }}")
        fl = QVBoxLayout(frame)
        fl.setContentsMargins(6, 4, 6, 4)
        fl.setSpacing(0)
        top = QHBoxLayout()
        top.setSpacing(2)
        lbl = QLabel(f"{icon}  {text}")
        lbl.setFont(QFont("Segoe UI", 8))
        lbl.setStyleSheet(f"color: {color}; background: transparent;")
        lbl.setWordWrap(True)
        top.addWidget(lbl, 1)
        dot = None
        if changed:
            dot = _PulseDot()
            top.addWidget(dot)
        fl.addLayout(top)
        fl.addStretch()
        return frame, dot

    # ── Advies ────────────────────────────────────────────────────────────────
    def _build_tips(self) -> list:
        from .panels5 import _prop_now, _station_snr

        def num(key, default):
            try:
                return float(str(self._solar.get(key, default)).replace("—", str(default)) or default)
            except (ValueError, TypeError):
                return float(default)

        sfi, ssn = num("sfi", 90), num("ssn", 50)
        k_index, a_index = num("k_index", 2), num("a_index", 5)
        xray   = str(self._solar.get("xray", ""))
        sw_spd = str(self._solar.get("sw_speed", "—"))
        sw_bz  = str(self._solar.get("sw_bz", "—"))

        utc_h = _dt.datetime.now(_dt.timezone.utc).hour
        now_loc = _dt.datetime.now()
        lok_h, month = now_loc.hour, now_loc.month

        # Banden en dag/nacht uit het gekalibreerde model (zoals 'Banden nu')
        try:
            cond = _prop_now(self._cfg)
            band_pct, is_day = dict(cond.band_pct), bool(cond.is_day)
        except Exception:
            band_pct, is_day = {}, 6 <= utc_h < 20
        hf_open = sorted([(n, p) for n, p in band_pct.items() if p > 0], key=lambda x: -x[1])

        s_i, ss_i, k_i, a_i = int(sfi), int(ssn), int(k_index), int(a_index)
        tips = []

        # 1. Beste banden
        if not self._solar:
            tips.append(("s1", "📡", tr("prop.adv.no_data"), TEXT_DIM))
        elif hf_open:
            bstr = "  ·  ".join(f"{n} {p}%" for n, p in hf_open[:5])
            extra = f"  (+{len(hf_open) - 5})" if len(hf_open) > 5 else ""
            tips.append(("s1", "📡", tr("prop.adv.best", bands=bstr + extra), "#4CAF50"))
        else:
            tips.append(("s1", "📡", tr("prop.adv.best", bands="—"), TEXT_DIM))

        # 2. Geomagnetisch
        if k_index >= 7:
            tips.append(("s2", "🚨", tr("prop.adv.storm4", k_i=k_i, a_i=a_i), "#F44336"))
        elif k_index >= 5:
            tips.append(("s2", "⚠️", tr("prop.adv.storm3", k_i=k_i, a_i=a_i), "#F44336"))
        elif k_index >= 3:
            tips.append(("s2", "⚡", tr("prop.adv.storm2", k_i=k_i, a_i=a_i), "#FFC107"))
        else:
            tips.append(("s2", "✅", tr("prop.adv.storm0", k_i=k_i, a_i=a_i), "#4CAF50"))

        # 3. Zonactiviteit
        if sfi >= 200:
            tips.append(("s3", "🌟", tr("prop.adv.sfi.exc", s_i=s_i, ss_i=ss_i), ACCENT))
        elif sfi >= 150:
            tips.append(("s3", "☀️", tr("prop.adv.sfi.high", s_i=s_i, ss_i=ss_i), ACCENT))
        elif sfi >= 100:
            tips.append(("s3", "🌤", tr("prop.adv.sfi.med", s_i=s_i, ss_i=ss_i), ACCENT))
        elif sfi >= 80:
            tips.append(("s3", "🌥", tr("prop.adv.sfi.low", s_i=s_i, ss_i=ss_i), TEXT_BODY))
        else:
            tips.append(("s3", "🌧", tr("prop.adv.sfi.min", s_i=s_i, ss_i=ss_i), TEXT_DIM))

        # 4. Zonnewind en Bz
        try:
            spd, bz = float(sw_spd), float(sw_bz)
            spd_s, bz_s = str(int(spd)), f"{bz:+.1f}"
            if spd > 700 or bz <= -20:
                tips.append(("s4", "🌪", tr("prop.adv.sw.storm", spd_s=spd_s, bz_s=bz_s), "#F44336"))
            elif spd > 500 or bz <= -10:
                tips.append(("s4", "💨", tr("prop.adv.sw.high", spd_s=spd_s, bz_s=bz_s), "#FFC107"))
            elif bz > 5:
                tips.append(("s4", "🛡", tr("prop.adv.sw.north", spd_s=spd_s, bz_s=bz_s), "#4CAF50"))
            else:
                tips.append(("s4", "💫", tr("prop.adv.sw.normal", spd_s=spd_s, bz_s=bz_s), TEXT_BODY))
        except (ValueError, TypeError):
            tips.append(("s4", "💫", tr("prop.adv.sw.none"), TEXT_DIM))

        # 5. Flares — elf vaste kaartjes: ook bij rust een kaartje, zodat het
        #    raster niet verspringt en een verandering op dezelfde plek knippert
        xclass = xray[:1].upper() if xray else ""
        if xclass == "X":
            tips.append(("s5", "☢", tr("prop.adv.flare_x", xray=xray), "#F44336"))
        elif xclass == "M":
            tips.append(("s5", "⚡", tr("prop.adv.flare_m", xray=xray), "#FFC107"))
        else:
            tips.append(("s5", "🔆", tr("prop.adv.flare_none", xray=xray or "—"), TEXT_BODY))

        # 6. Dagdeel (lokale tijd; dag/nacht volgens de echte zon op de QTH)
        h_s = f"{lok_h:02d}"
        if is_day:
            key = ("prop.adv.day.morn" if lok_h < 10 else
                   "prop.adv.day.noon" if lok_h < 16 else "prop.adv.day.aft")
            icon = "🌅" if lok_h < 10 else "🌞" if lok_h < 16 else "🌇"
        else:
            key = ("prop.adv.night.eve" if (lok_h >= 18 or lok_h < 2) else
                   "prop.adv.night.mid" if lok_h < 5 else "prop.adv.night.pre")
            icon = "🌃" if (lok_h >= 18 or lok_h < 2) else "🌌" if lok_h < 5 else "🌄"
        tips.append(("s6", icon, tr(key, h_s=h_s), TEXT_BODY))

        # 7. Mode / vermogen
        if self._cfg:
            mode, power, ant = self._cfg.mode, self._cfg.power, getattr(self._cfg, "antenna", "")
            snr_s = f"{_station_snr(self._cfg):+d}"
            bn0, bp0 = hf_open[0] if hf_open else ("", 0)
            if not hf_open:
                tips.append(("s7", "🔧", tr("prop.adv.mode.none", mode=mode, power=power,
                                      snr_s=snr_s), TEXT_DIM))
            elif bp0 < 30 and mode == "SSB":
                tips.append(("s7", "🔧", tr("prop.adv.mode.weak", bn0=bn0, bp0=bp0, snr_s=snr_s), "#FFC107"))
            else:
                tips.append(("s7", "🔧", tr("prop.adv.mode.ok", mode=mode, bn0=bn0, bp0=bp0,
                                      power=power, snr_s=snr_s, ant=ant), TEXT_BODY))

        # 8. Absorptie op hoge breedte
        if self._cfg:
            lat = abs(self._cfg.qth_lat)
            if lat > 50 and k_index >= 4:
                tips.append(("s8", "🧲", tr("prop.adv.aurora.hi", k_i=k_i, lat=lat), "#FFC107"))
            elif lat > 45 and k_index >= 3:
                tips.append(("s8", "🧲", tr("prop.adv.aurora.lo", k_i=k_i, lat=lat), TEXT_BODY))
            else:
                tips.append(("s8", "🧲", tr("prop.adv.aurora.none", k_i=k_i, lat=lat), TEXT_BODY))

        # 9. Sporadic-E (noordelijk halfrond: mei–aug, klein winterpiekje)
        es_score = 3 if month in (6, 7) else 2 if month in (5, 8) else 1 if month in (12, 1) else 0
        es_time = (9 <= lok_h < 14) or (17 <= lok_h < 22)
        if es_score >= 2 and es_time:
            tips.append(("s9", "⚡", tr("prop.adv.es.high", month=month, h_s=h_s), "#66BB6A"))
        elif es_score >= 2:
            tips.append(("s9", "⚡", tr("prop.adv.es.season", month=month), TEXT_DIM))
        else:
            tips.append(("s9", "⚡", tr("prop.adv.es.off", month=month), TEXT_DIM))

        # 10. DX-routes (vuistregels vanuit Europa, UTC)
        routes = []
        if is_day:
            if 5 <= utc_h < 10 and sfi >= 100: routes.append("EU→JA (20m/17m)")
            if 12 <= utc_h < 18 and sfi >= 80:  routes.append("EU→W (20m/15m)")
            if 8 <= utc_h < 14 and sfi >= 80:   routes.append("EU→AF (20m/17m)")
            if 14 <= utc_h < 20 and sfi >= 120: routes.append("EU→OC (15m/10m)")
        else:
            if utc_h >= 22 or utc_h < 4: routes.append("EU→W (40m/80m)")
            if 2 <= utc_h < 8:           routes.append("EU→JA (40m gray line)")
        if routes:
            tips.append(("s10", "🌍", tr("prop.adv.dx.routes", routes="  ·  ".join(routes)), "#4FC3F7"))
        else:
            tips.append(("s10", "🌍", tr("prop.adv.dx.none"), TEXT_DIM))

        # 11. Algeheel oordeel
        score = (3 if sfi >= 150 else 2 if sfi >= 100 else 1 if sfi >= 80 else 0)
        score += 2 if k_index <= 2 else 1 if k_index <= 4 else 0
        score += 2 if hf_open and hf_open[0][1] >= 60 else 1 if hf_open else 0
        try:
            if float(sw_bz) < -10:
                score -= 1
        except (ValueError, TypeError):
            pass
        overall = (tr("band.excellent") if score >= 6 else tr("band.good") if score >= 4
                   else tr("band.fair") if score >= 2 else tr("band.poor"))
        clr = ("#4CAF50" if score >= 6 else "#8BC34A" if score >= 4
               else "#FFC107" if score >= 2 else "#F44336")
        tips.append(("s11", "📊", tr("prop.adv.overall", overall=overall)
                     + f"  (SFI {s_i} · K {k_i} · {len(hf_open)})", clr))
        return tips
