# HAMIOS v5.0 — Interface Migratie Plan
## Optie C: Fase 3 (Toplevel panelen) → Fase 4 (PyQt6)

**Datum:** 2026-05-12  
**Huidig:** HAMIOS v4.0.2 (tkinter + PIL, draggable Frame panels)  
**Doel:** HAMIOS v5.0 (PySide6 + GPU rendering, vloeiende 60fps interface)  

---

## 1. Doelstelling

| Probleem v4 | Oplossing v5 |
|---|---|
| Kaart render 100–400ms blokkeert UI | GPU-accelerated QGraphicsView, <5ms |
| Drag/resize voelbaar traag (place()) | OS-native window movement |
| Overlay-toggle herrendert alles | Per-layer canvas items, <1ms |
| PIL in main thread | QThread rendering pipeline |
| lift() hacks voor z-order | OS-native z-order |
| Geen animaties mogelijk | QPropertyAnimation, 60fps standaard |

---

## 2. Fasering

```
v4.0.2 ──[Fase 3: 1-2 weken]──► v4.5 ──[Fase 4: 4-5 weken]──► v5.0
         Toplevel panels              PySide6 + GPU map
         Vloeiend drag/resize         Volledige herimplementatie
```

---

## 3. Fase 3 — Toplevel Panelen (v4.5)

### 3.1 Doel
Elk DraggablePanel wordt een `tk.Toplevel` met `overrideredirect=True`.
OS-niveau vensterbeheer geeft instant drag/resize zonder eigen code.

### 3.2 Architectuurwijziging

**Voor:**
```
root (Tk)
└── _desktop (tk.Frame, BG_ROOT)
    ├── panel1.frame (tk.Frame, place(x=440, y=0, w=740, h=490))
    ├── panel2.frame (tk.Frame, place(x=0, y=0, w=430, h=600))
    └── ...
```

**Na:**
```
root (Tk, 42px header only)
└── header (tk.Frame)

panel1 (tk.Toplevel, overrideredirect=True, geometry="+440+0")
panel2 (tk.Toplevel, overrideredirect=True, geometry="+0+42")
...
```

### 3.3 Stappen

#### Stap 3.3.1: DraggablePanel refactor
Bestand: `HAMIOS.py`, klasse `DraggablePanel`

**Wijzigingen:**
- `self.frame = tk.Frame(parent)` → `self.frame = tk.Toplevel(root_ref)`
- `self.frame.overrideredirect(True)`
- `self.frame.wm_attributes("-topmost", False)` — OS beheert z-order
- Windows: `self.frame.wm_attributes("-alpha", 0.97)` — subtiele schaduw
- `_place_frame()`: `self.frame.place(...)` → `self.frame.wm_geometry(f"{w}x{h}+{x}+{y}")`
- Drag: verander naar `wm_geometry` aanroep
- Resize: behoud eigen resize-handle, gebruik `wm_geometry`
- Constructor krijgt `root_ref` parameter naast `parent`

**Aandachtspunten:**
- `overrideredirect=True` vereist dat we zelf focus-management doen
- Toplevel.lift() werkt zonder hacks
- Sluit-knop: `win.withdraw()` i.p.v. `pack_forget()`
- Zichtbaarheid: `win.deiconify()` i.p.v. `pack()`

#### Stap 3.3.2: Coördinatensysteem
- Huidige lay-out: desktop-relatief (0,0 = linkerbovenhoek desktop Frame)
- Nieuw: scherm-absoluut (0,0 = linkerbovenhoek scherm)
- Offset berekenen: `root.winfo_rootx()`, `root.winfo_rooty()` + header hoogte
- `hamios_layouts.json`: opslaan als scherm-absolute coördinaten
- `_PANEL_DEFAULTS`: aanpassen naar schermcoördinaten

#### Stap 3.3.3: Z-order management
- Verwijder `_keep_panels_front()` timer-loop
- Verwijder `_lift_all_panels()` methode
- Verwijder `_bind_lift_recursive()` binding
- Panelen zijn altijd boven het hoofdvenster door OS-native Toplevel z-order
- `root.wm_attributes("-topmost", False)` — main window op achtergrond

#### Stap 3.3.4: Drag implementatie voor Toplevel
```python
def _on_drag_start(self, event):
    self._drag_sx = event.x_root
    self._drag_sy = event.y_root
    self._drag_ox = self._x
    self._drag_oy = self._y

def _on_drag_move(self, event):
    dx = event.x_root - self._drag_sx
    dy = event.y_root - self._drag_sy
    self._x = max(0, self._drag_ox + dx)
    self._y = max(0, self._drag_oy + dy)
    # Direct wm_geometry, geen after_idle nodig
    self.frame.wm_geometry(f"{self._w}x{self._h}+{self._x}+{self._y}")
```

#### Stap 3.3.5: Resize implementatie
- Eigen resize-handle (◢) blijft
- `wm_geometry(f"{w}x{h}+{x}+{y}")` instellen bij resize
- Alternatief: `wm_resizable(True, True)` voor OS-native resize
  - Vereist detectie van WM_SIZE event → `frame.bind("<Configure>", ...)`

#### Stap 3.3.6: Amber rand en titelbalk
- Toplevel heeft geen eigen OS-chrome (overrideredirect)
- Onze eigen amber rand + titelbalk blijft intact
- Transparantie: `wm_attributes("-transparentcolor", BG_ROOT)` voor doorkijk
- Windows: subtiele schaduw via DWM (automatisch bij Toplevel)

#### Stap 3.3.7: Focus en interactie
- `frame.focus_force()` bij klik op titelbalk
- `frame.bind("<FocusIn>", ...)` om z-order bij te houden
- Alt+F4 afvangen: `frame.protocol("WM_DELETE_WINDOW", self._toggle_hide)`
- Alt+Tab: panels zijn zichtbaar in taskbar — eventueel verbergen via
  `win.wm_transient(root)` zodat ze als sub-vensters worden behandeld

### 3.4 Fase 3 Risico's en mitigaties

| Risico | Kans | Mitigatie |
|---|---|---|
| Platform-verschillen Win/Mac/Linux | Midden | Testen op alle platforms, platform-checks |
| overrideredirect breekt focus | Hoog | Explicit focus_set() bij click |
| Panels verdwijnen achter taskbar | Laag | wm_transient(root) |
| Performance regressie | Laag | Benchmarken voor/na |
| Layout-opslag incompatibiliteit | Midden | Versie-tag in layouts.json |

### 3.5 Deliverables Fase 3
- [ ] HAMIOS v4.5 met Toplevel panels
- [ ] Vloeiend drag/resize zonder vertraging
- [ ] Layout-opslag in schermcoördinaten
- [ ] Verwijderd: lift()-hacks, _keep_panels_front timer
- [ ] Test: alle 15 panels werken correct
- [ ] Test: layout opslaan/laden werkt
- [ ] Test: splash screen, settings, dialogen correct gecentreerd

---

## 4. Fase 4 — PySide6 Migratie (v5.0)

### 4.1 Installatie
```bash
pip install PySide6          # Main framework (LGPL)
pip install pyqtgraph        # GPU-accelerated charts
pip install Pillow           # Behouden voor map preprocessing
```

### 4.2 Architectuur v5.0

```
QApplication (HAMIOS)
├── MainWindow (QMainWindow)
│   ├── HeaderWidget (QWidget, 42px)
│   │   ├── Titel, Exit, Fullscreen
│   │   ├── Sat, Spy, Settings knoppen
│   │   └── Tijd, Auto-refresh
│   └── Desktop (QWidget, transparant achtergrond)
│
├── MapPanel (FloatingPanel)
│   └── MapView (QGraphicsView, hardware-accelerated)
│       ├── BaseMapLayer (QGraphicsPixmapItem)
│       ├── NightLayer (QGraphicsItem, QPainter)
│       ├── GraylineLayer (QGraphicsItem)
│       ├── AuroraLayer (QGraphicsItem)
│       ├── SatelliteLayer (QGraphicsItemGroup)
│       ├── LightningLayer (QGraphicsItemGroup)
│       └── DXSpotsLayer (QGraphicsItemGroup)
│
├── SolarPanel (FloatingPanel)
│   └── SolarWidget (QWidget, QGridLayout)
│
├── BandHistPanel (FloatingPanel)
│   └── pyqtgraph.PlotWidget
│
├── KpPanel (FloatingPanel)
│   └── pyqtgraph.BarGraphItem
│
├── BzPanel (FloatingPanel)
│   └── pyqtgraph.PlotWidget
│
└── ... (alle andere panelen)
```

### 4.3 Migratie-strategie: Python-logica hergebruiken

**Hergebruiken (90% van de code):**
- Alle data-fetching functies (`_fetch_solar`, `_fetch_bz_24h`, etc.)
- Alle berekeningen (`_calc_propagation`, `_sgp4_latlon`, etc.)
- Settings opslaan/laden (`_load_settings`, `_save_settings`)
- WebSocket handlers (Blitzortung)
- Satelliet TLE logica
- Spy stations data
- Alle constanten en `_T` vertalingen

**Herschrijven (10% van de code):**
- GUI-klassen en widget-constructie
- Event-bindings (`bind` → `connect`)
- Canvas-tekening (PIL → QPainter/QGraphicsItem)
- Font/kleur systeem (tkinter vars → Qt stylesheets)

### 4.4 Sprint-planning Fase 4

#### Sprint 1 (Week 1): Fundament + MainWindow
- PySide6 project opzetten naast bestaand tkinter project
- `QApplication` + `QMainWindow` basis
- `FloatingPanel` basisklasse (QWidget, frameless, draggable)
- Header-balk porteerden
- Settings dialoog porteerden
- Splash screen porteerden
- **Deliverable:** App start op, header en settings werken

#### Sprint 2 (Week 2): Kaart-paneel (hoogste prioriteit)
- `QGraphicsView` + `QGraphicsScene` voor wereldkaart
- NASA map laden als `QPixmap` → `QGraphicsPixmapItem`
- Nachtoverlay: pre-render PIL → `QPixmap`, update elke 30s
- Grayline, Aurora als `QGraphicsItem` met `QPainter`
- Zoom/pan via `QGraphicsView.scale()` en `translate()`
- Muisinteractie: groot-cirkel pad, scroll-zoom
- **Deliverable:** Kaart werkt, vloeiend zoom/pan

#### Sprint 3 (Week 3): Overlay-lagen kaart
- Satellieten als `QGraphicsEllipseItem` (real-time update)
- Bliksem als `QGraphicsEllipseItem` (instant, 60fps fade)
- DX-spots als `QGraphicsLineItem` + `QGraphicsEllipseItem`
- WSPR paden
- Ionosonde markers
- GC-pad bij klik
- **Deliverable:** Alle overlays werken real-time

#### Sprint 4 (Week 4): Grafieken
- Kp 48h: `pyqtgraph.BarGraphItem`
- Bz 24h: `pyqtgraph.PlotDataItem` (Y-as zoom behouden)
- X-ray 24h: `pyqtgraph.PlotDataItem` (log-schaal)
- Band history: `pyqtgraph.PlotDataItem` per band
- Solar history strip: `pyqtgraph.BarGraphItem` (K-index) + `PlotDataItem` (SFI)
- Tooltips op alle grafieken via pyqtgraph hover
- **Deliverable:** Alle 5 grafieken werken met GPU-acceleratie

#### Sprint 5 (Week 5): Overige panelen + integratie
- Solar parameters panel (QGridLayout)
- Band conditions panel (QTableWidget)
- Storm forecast panel (QLabel)
- Band reliability bars (QPainter custom widget of pyqtgraph)
- DX spots panel (QTableWidget, sorteerbaar)
- Band schedule heatmap (QTableWidget + kleuren)
- Alerts panel (QWidget)
- Lightning forecast panel (pyqtgraph + status)
- **Deliverable:** Alle panelen geporteerd

#### Sprint 6 (Week 6): Polish + release
- Alle 13 talen werken (QTranslator of eigen _T systeem)
- Settings volledig werkend (QDialog)
- Layout presets (hamios_layouts.json hergebruiken)
- Splash screen
- Dependency check
- Performance benchmarks
- Bug fixes
- **Deliverable:** HAMIOS v5.0 release

### 4.5 FloatingPanel basisklasse (PySide6)

```python
class FloatingPanel(QWidget):
    """Vervanger voor DraggablePanel — OS-native floating window."""
    
    def __init__(self, title: str, icon: str = "", parent=None):
        super().__init__(parent, Qt.Tool | Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self._drag_pos = None
        self._setup_ui(title, icon)
    
    def _setup_ui(self, title, icon):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(1, 1, 1, 1)  # 1px amber rand
        layout.setSpacing(0)
        
        # Titelbalk
        self._titlebar = QWidget()
        self._titlebar.setFixedHeight(26)
        self._titlebar.setStyleSheet(f"background: {ACCENT_COLOR};")
        # ... titel label, sluit knop
        
        # Content
        self.content = QWidget()
        layout.addWidget(self._titlebar)
        layout.addWidget(self.content)
        self.setStyleSheet(f"border: 1px solid {ACCENT_COLOR};")
    
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self._drag_pos = event.globalPosition().toPoint() - self.pos()
    
    def mouseMoveEvent(self, event):
        if self._drag_pos and event.buttons() == Qt.LeftButton:
            self.move(event.globalPosition().toPoint() - self._drag_pos)
```

### 4.6 MapView implementatie (PySide6)

```python
class MapView(QGraphicsView):
    """Hardware-accelerated kaart met overlay lagen."""
    
    def __init__(self):
        super().__init__()
        self.setRenderHint(QPainter.Antialiasing)
        self.setViewportUpdateMode(QGraphicsView.FullViewportUpdate)
        self.setOptimizationFlag(QGraphicsView.DontAdjustForAntialiasing)
        # Optioneel: OpenGL voor maximale performance
        # self.setViewport(QOpenGLWidget())
        
        self._scene = QGraphicsScene()
        self.setScene(self._scene)
        
        # Lagen (z-order via QGraphicsItem.setZValue)
        self._base_map  = QGraphicsPixmapItem()  # z=0
        self._night     = NightOverlayItem()      # z=1
        self._grayline  = GraylineItem()          # z=2
        self._aurora    = AuroraItem()            # z=3
        self._satellites = QGraphicsItemGroup()  # z=10
        self._lightning  = QGraphicsItemGroup()  # z=11
        self._dx_spots   = QGraphicsItemGroup()  # z=12
        
    def update_base_map(self, pixmap: QPixmap):
        """Update kaartafbeelding (aanroepen vanuit QThread)."""
        self._base_map.setPixmap(pixmap)
    
    def add_lightning_strike(self, lat, lon, age_s, energy):
        """Real-time inslag toevoegen (direct, geen render nodig)."""
        x, y = self._latlon_to_scene(lat, lon)
        item = LightningItem(x, y, age_s, energy)
        item.setZValue(11)
        self._scene.addItem(item)
        self._lightning.addToGroup(item)
```

### 4.7 Rendering pipeline v5.0

```
WebSocket (QThread)          HTTP (QThread)
    │                            │
    ▼                            ▼
strike buffer              solar data
    │                            │
    ▼                            ▼
MapScene.addItem()         MapUpdateThread
(direct, 0ms)                   │
                                 ├─ render PIL base map
                                 ├─ convert → QPixmap
                                 └─ emit signal → main thread
                                      │
                                      ▼
                              MapView.update_base_map()
                              (alleen swap pixmap, <1ms)
```

### 4.8 Stijl en thema in PySide6

```python
# Centraal stylesheet (vervangt BG_PANEL, ACCENT, etc.)
HAMIOS_STYLESHEET = """
QWidget {
    background-color: #22252A;
    color: #F0E6C8;
    font-family: 'Segoe UI';
}
QWidget[class="panel-titlebar"] {
    background-color: #22252A;
    color: #C8A84B;
    font-weight: bold;
}
/* Amber rand via border op FloatingPanel */
FloatingPanel {
    border: 1px solid #C8A84B;
}
"""
```

### 4.9 Fase 4 Risico's en mitigaties

| Risico | Kans | Impact | Mitigatie |
|---|---|---|---|
| PySide6 LGPL-licentie issue | Laag | Hoog | Open source project, LGPL is toegestaan |
| pyqtgraph learning curve | Midden | Midden | Goede documentatie, voorbeelden beschikbaar |
| Qt platform-specifiek gedrag | Midden | Midden | Testen op Windows, macOS, Linux |
| Performance valt tegen (software render) | Laag | Hoog | OpenGL viewport aanzetten als fallback |
| Vertalingssysteem (_T) herbouwen | Midden | Laag | Eigen _T systeem hergebruiken |
| Bestaande features missen | Midden | Hoog | Checklist per feature bij elke sprint |

---

## 5. Versie-nummering

| Versie | Status | Beschrijving |
|---|---|---|
| v4.0.2 | ✅ Huidig | tkinter + PIL, draggable Frame panels |
| v4.5.0 | 🔄 Fase 3 | tkinter + PIL, Toplevel panels (vloeiend drag) |
| v5.0.0 | 🎯 Fase 4 | PySide6 + GPU rendering |

---

## 6. Niet migreren (v5.0 scope out)

- CAT interface (blijft uitgeschakeld in v5.0)
- Spy stations uitbreiden (scope blijft gelijk)
- Nieuwe data-bronnen (scope v5.x)

---

## 7. Rollback-plan

**Per fase:**
- Fase 3: Git branch `feature/toplevel-panels` — rollback = `git checkout main`
- Fase 4: Git branch `feature/pyside6` — rollback = `git checkout main`
- HAMIOS v4.0.2 exe blijft beschikbaar als release op GitHub

---

## 8. Succescriteria

### Fase 3 (v4.5)
- [ ] Panel drag: geen merkbare vertraging (< 5ms)
- [ ] Panel resize: vloeiend, geen stutter
- [ ] Alle 15 panelen werken als Toplevel
- [ ] Layout opslaan/laden werkt
- [ ] Geen regressies t.o.v. v4.0.2

### Fase 4 (v5.0)
- [ ] Kaart render: < 10ms (was 100–400ms)
- [ ] Overlay toggle: < 1ms (was 100–200ms)
- [ ] Lightning strikes: zichtbaar < 50ms na ontvangst (was 500ms+)
- [ ] Panel drag: 0ms vertraging (OS-native)
- [ ] 60fps animaties mogelijk
- [ ] Alle features van v4.0.2 aanwezig
- [ ] Windows + macOS + Linux werkt

---

*Document aangemaakt: 2026-05-12*  
*Auteur: Frank van Dijke + Claude AI*
