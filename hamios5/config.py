"""HAMIOS v5 — Configuratie (hamios_config.json)"""

import json
import os
from dataclasses import dataclass, field, asdict

_HERE        = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_CONFIG_FILE = os.path.join(_HERE, "hamios_config.json")


@dataclass
class AppConfig:
    # ── Station ──────────────────────────────────────────────────────────────
    callsign:       str   = ""
    qth_lat:        float = 52.0
    qth_lon:        float = 5.0
    qth_locator:    str   = "JO22"
    mode:           str   = "SSB"
    power:          str   = "100W"
    antenna:        str   = "Dipole ~2dBi"   # reëlere standaard

    # ── Kaart overlays ────────────────────────────────────────────────────────
    show_night:     bool  = True
    show_grayline:  bool  = True
    show_aurora:    bool  = True
    show_sun:       bool  = True
    show_moon:      bool  = True
    show_lightning: bool  = True
    show_dx_spots:  bool  = True
    show_locator:   bool  = False
    map_overlay:    bool  = True    # header-knop staat

    # ── Bliksem ───────────────────────────────────────────────────────────────
    lightning_fade:    int   = 600   # seconden
    lightning_radius:  int   = 500   # km — drempel voor header-melding (0 = uit)
    lightning_rate:    int   = 500   # ms — animatie-update interval
    lightning_beep:    bool  = False # piepje bij elke inslag
    lightning_beep_r:  int   = 0    # piepje alleen binnen radius km (0 = altijd)

    # ── Refresh-interval ─────────────────────────────────────────────────────
    refresh_interval:  int   = 5      # minuten (0 = uit)

    # ── Snap-raster / weergave ────────────────────────────────────────────────
    snap_grid:         int   = 10
    overlay_font_size: int   = 8      # graticule lettergrootte (pt)
    sat_font_size:     int   = 8      # satelliet-labels op kaart
    dx_map_font_size:  int   = 7      # DX spots callsigns op kaart
    dx_font_size:      int   = 8      # DX spots tabel
    show_splash:       bool  = True

    # ── DX spots status ───────────────────────────────────────────────────────
    dx_own_continent:  bool  = False
    dx_heatmap:        bool  = False

    # ── BandRel instellingen (gebruikt dezelfde mode/power als Station-tab) ──
    band_day_auto: bool = True

    # ── Satellieten ───────────────────────────────────────────────────────────
    sat_visible:    bool  = False
    sat_selected:   list  = field(default_factory=list)
    sat_path:       list  = field(default_factory=list)
    sat_fp:         list  = field(default_factory=list)
    sat_back_h:     int   = 1
    sat_fwd_h:      int   = 12
    sat_filter_sel: bool  = True   # "Geselecteerd"-filter actief bij openen

    # ── Meldingen ─────────────────────────────────────────────────────────────
    k_alert:        int   = 4       # K-index drempel (0–9)
    k_alert_en:     bool  = True
    xflare_alert_en: bool = True
    band_alert:     int   = 40      # band-betrouwbaarheid % drempel
    band_alert_en:  bool  = True
    alert_max:      int   = 50     # max aantal meldingen (FIFO)

    # ── CAT ───────────────────────────────────────────────────────────────────
    cat_enabled:    bool  = False
    cat_port:       str   = ""
    cat_baud:       int   = 4800
    cat_databits:   int   = 8
    cat_parity:     str   = "Geen"
    cat_stopbits:   str   = "1"
    cat_rtscts:     bool  = False
    cat_dtr:        bool  = False
    cat_rts:        bool  = False
    cat_radio_type: str   = "Yaesu"
    cat_civ_addr:   int   = 0x58   # Icom standaard adres 0x58


def load_config() -> AppConfig:
    cfg = AppConfig()
    try:
        if os.path.exists(_CONFIG_FILE):
            with open(_CONFIG_FILE, encoding="utf-8") as f:
                data = json.load(f)
            for k, v in data.items():
                if hasattr(cfg, k):
                    default = getattr(cfg, k)
                    try:
                        setattr(cfg, k, type(default)(v))
                    except (TypeError, ValueError):
                        setattr(cfg, k, v)
    except Exception:
        pass
    return cfg


def save_config(cfg: AppConfig):
    try:
        with open(_CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(asdict(cfg), f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"Config opslaan mislukt: {e}")
