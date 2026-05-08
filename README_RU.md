# 📡 HAMIOS v4.0.1

**Монитор распространения КВ и DX для Windows**

> v4.0.1 — Перетаскиваемые и масштабируемые панели · Единый диалог Настроек · Оптимизация производительности · График истории солнечной активности

*Conceived by Frank van Dijke · Developed with Claude AI*

HAMIOS предоставляет радиолюбителям информацию в реальном времени о распространении КВ, солнечной активности и DX-возможностях — в современном тёмном графическом интерфейсе.

---

## ✨ Возможности

### 🌍 Интерактивная карта мира *(в центре окна)*
- Равнопромежуточная карта NASA, автоматически загружается при первом запуске
- **Фиксированная высота (380 пкс)** с правильным рендерингом 2:1 — без горизонтального искажения
- **Граница день/ночь** с мягкой переходной зоной
- **Серая линия** (янтарная полоса, ~1000 км шириной)
- **Положение Солнца и Луны** (геоцентрический расчёт)
- **Маркер QTH** (синий перекрестие) — широта/долгота настраивается в заголовке
- **Ортодромия**: клик на карте → расстояние + азимут + **качество диапазона для этого маршрута**
- **Оверлей регионов МСЭ** R1/R2/R3 (официальный МСЭ RR Ст. 5)
- **Сетка локаторов Мэйденхед** (20° × 10°, метки AA–RR)
- **Слой префиксов позывных** (~110 объектов DXCC)
- **Масштабирование/прокрутка**: колёсико мыши 1×–8×, клик+перетаскивание, ПКМ для сброса
- **Наложения карты сгруппированы** под картой:
  - *Display:* Sun · Moon · Gray line · Aurora · Sat
  - *Data:* WSPR · Spots · CS · Locator

### 🛰️ Propagation Path Map
- **Band quality** calculated at the midpoint of the great-circle path
- Day/night correction at the midpoint
- Number of hops estimated (≈ distance / 3500 km)
- Top-5 open bands: `↳  8,847 km / 3 hops / day  ▸  20m 87%  ·  17m 72%  ·  15m 54%  (MUF 24.1 MHz)`
- **Great-circle line colour follows the best band**

### 🌌 Aurora Ring Overlay
- Magnetic aurora oval based on K-index (Feldstein/Holzworth, IGRF-2025)
- **Colour by K-index**: green (K < 3) · yellow (K 3–5) · red (K ≥ 6)

### 🖥️ Система панелей *(v4.0.1)*
- **11 свободно перетаскиваемых и масштабируемых панелей** на свободном холсте рабочего стола
- Каждая панель имеет янтарную рамку 1px, строку заголовка с кнопкой ✕ закрытия и маркер ◢ изменения размера
- **Привязка к сетке** (2px) при отпускании после перетаскивания/изменения размера для чёткого выравнивания
- Панели: Надёжность КВ-диапазонов · Карта мира · Солнечная/Ионосфера · Предупреждения · Расписание диапазонов · История диапазонов · Kp 48ч · Bz 24ч · Рентген 24ч · DX-споты · Рекомендации по распространению
- **⚙ Диалог Настройки** содержит всю конфигурацию: QTH · Язык · Тема · Подсказки · Бегущая строка · Летнее время · Видимость панелей · Управление макетами
- **Предустановки макетов**: сохранение/загрузка/перезапись/удаление именованных профилей в `hamios_layouts.json`
- **Сохранить по умолчанию**: сохраняет текущий макет как макет запуска

### 🛰 Отслеживание спутников *(кнопка 🛰 Sat в заголовке)*
- Данные TLE загружаются с **Celestrak** (Amateur / ISS / Weather / CubeSat)
- **Фильтр по категории**: Все · Amateur · ISS · Weather · CubeSat
- Для каждого спутника: переключать **точку позиции** (●), **орбитальный путь** (~) и **зону охвата** на карте
- **Зона охвата становится зелёной** когда QTH находится внутри зоны покрытия спутника
- **Панель уведомлений** показывает спутники, находящиеся над QTH с углом возвышения
- Времена траектории отображаются по местному времени (CEST / CET)
- Кнопка **↻ TLE** для ручного обновления орбитальных элементов
- Кэшируется в `hamios_tle.json`

### 🕵 Шпионские / цифровые станции *(кнопка 🕵 Spy в заголовке)*
- Прокручиваемая таблица 24 известных цифровых и шпионских радиостанций
- Столбцы: статус (● активный / исторический), название, страна, частоты, режим
- **Сортируемые столбцы** — нажмите на заголовок для сортировки; нажмите снова для обратной сортировки
- **Фильтр** по статусу активный/неактивный и свободный текстовый поиск (название, страна, частота)
- **Наведите мышь** на строку для просмотра полного описания + расписания вещания
- Файл данных: `hamios_spy_stations.json` (редактируемый)

### 🔵 WSPR / PSKReporter Spots on Map
- Live propagation paths from **wspr.rocks** (WSPR) and **pskreporter.info** (FT8/FT4)
- Connection lines: **colour = band**, **thickness = SNR**

### 📍 DX Spot Markers on Map
- Active DX cluster spots: dot at DX location + line to spotter, colour-coded by band
- Click a dot to show callsign, frequency and comment

### 🌞 Солнечные и ионосферные данные

| Parameter | Source | Description |
|-----------|--------|-------------|
| SFI | hamqsl.com | Solar Flux Index (10.7 cm) |
| SSN | hamqsl.com | Sunspot Number |
| A-index | hamqsl.com | Daily geomagnetic activity |
| K-index | hamqsl.com | 3-hour geomagnetic activity (0–9) |
| X-ray | hamqsl.com | GOES X-ray flux (A/B/C/M/X class) |
| MUF | internal model | Maximum Usable Frequency |
| LUF | internal model | Lowest Usable Frequency |
| Solar wind speed | NOAA SWPC | km/s via DSCOVR/ACE |
| Bz | NOAA SWPC | Interplanetary magnetic field Z-component (nT) |
| foF2 | GIRO/LGDC | Measured F2-layer critical frequency (ionosonde) |

### 📊 Bz 24-hour Chart *(dedicated panel)*
- **Blue** = positive Bz (favourable) · **Red** = negative Bz (geo-effective)
- Y-labels −20 / 0 / +20 nT · scales automatically with the panel

### 📶 HF Band Reliability *(redesigned in v3.0)*
- Internal MUF/LUF model based on SFI, SSN, K-index and QTH latitude
- SNR budget corrected for **mode**, **power** and **antenna**
- **Gradient bars in band-specific colour** (light → dark) with gloss line
- Band name **bold and in band colour** — every band has its own identity
- Columns: start MHz · modes · FT8 frequency

### 🔔 Notifications & Alerts

| Notification | Setting | Description |
|-------------|---------|-------------|
| ⚠️ K-index storm | Checkbox + threshold (1–9) | Alert when K rises above threshold |
| 📡 Band open | Checkbox + threshold (10–90 %) | Alert when band opens |
| 🛰 Спутник над QTH | Всегда активно | Показывает какие выбранные спутники находятся над QTH с углом возвышения |

Thresholds are saved to `HAMIOS.ini`.

### 🔌 CAT Interface *(temporarily disabled)*
> The CAT interface is temporarily disabled pending further development. Code is intact and will be completed in a future release.

### 🕐 Band Opening Schedule
- 24-hour heatmap for all 11 HF bands
- Time axis in local time (CET/CEST), current time highlighted
- Hover tooltip: band · hour · quality · modes · FT8 frequency

### 📈 Band History
- Time graph of all HF bands (%) — 90 days kept in CSV
- Time range: Hours · Days · Weeks · Months
- Clickable legend to toggle individual bands

### 📡 Live DX Spots *(full-height right column)*
- JSON feed from dxwatch.com, refreshed every 5 minutes
- Columns: UTC · Band · DX · MHz · Spotter · Comment
- **Own-continent filter** — show only spots from your own continent
- **Heatmap mode**: band × UTC-hour activity pattern (24h buffer)
- Spots also shown as markers on the world map (toggleable)

### 💡 Propagation Analysis & Advice
12 analysis cards in 3 columns × 4 rows.

| # | Card | Contents |
|---|------|----------|
| 1 | 📡 Best bands | Top-5 open bands with quality percentage |
| 2 | ✅/⚠️ Geo-storm | K + A-index, route advice, severity |
| 3 | ☀️ Solar activity | SFI + SSN, solar cycle phase |
| 4 | 💨 Solar wind | Speed + Bz impact |
| 5 | ☢️ X-flare/SWF | X-ray class, recovery estimate |
| 6 | 📶 Ionosphere | MUF, LUF, F2 layer |
| 7 | 🌅 Day/night | Gray-line time windows |
| 8 | 🔧 Mode advice | FT8 vs SSB/CW based on SNR budget |
| 9 | 🧲 Absorption | Auroral absorption polar routes |
| 10 | 📊 Overall score | Composite propagation rating |

### 🌐 Multilingual
**14 languages** via external language pack system (`langs/*.json`).

| Code | Language | Code | Language |
|------|----------|------|----------|
| EN | English *(built-in)* | NO | Norsk |
| NL | Nederlands | PL | Polski |
| DE | Deutsch | SV | Svenska |
| FR | Français | DA | Dansk |
| IT | Italiano | FI | Suomi |
| ES | Español | PT | Português |
| JA | 日本語 | RU | Русский |

### ⚙️ Прочее
- **Динамические темы**: Midnight · DeepOcean · HighContrast
- **Системный трей**: свернуть в трей, уведомления
- **Подсказки** с пояснениями по каждому солнечному параметру
- **Автоматическое обновление**: Выкл / 30 с / 1 мин / 5 мин / 10 мин / 30 мин / 1 час
- **Бегущая строка** с актуальными советами по распространению
- **Перетаскиваемая система панелей**: свободно размещайте и масштабируйте все панели
- **Предустановки макетов**: сохранение и переключение между настраиваемыми расположениями панелей
- Все настройки сохранены в `HAMIOS.ini`

---

## 🖥️ Макет (v4.0.1) — Свободно плавающие панели

```
┌─────────────────────────────────────────────────────────────────────────┐
│  ⚙ Настройки  (QTH · Язык · Тема · Подсказки · Строка · Летнее время · Панели · Макеты) │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  ┌──────────────┐  ┌──────────────────────────────┐  ┌──────────────┐  │
│  │Солн./Ионосф. │  │      Карта мира           ✕  │  │КВ-диап.  ✕  │  │
│  │     ✕    ◢  │  │   зум/прокр. · оверлей    ◢  │  │Надёжность ◢ │  │
│  └──────────────┘  └──────────────────────────────┘  └──────────────┘  │
│                                                                         │
│  ┌─────────────┐  ┌─────────────┐  ┌──────────┐  ┌──────────────────┐  │
│  │Расписание   │  │История диап.│  │  Kp 48ч  │  │  DX-споты    ✕  │  │
│  │    ✕    ◢  │  │    ✕    ◢  │  │  ✕    ◢  │  │             ◢  │  │
│  └─────────────┘  └─────────────┘  └──────────┘  └──────────────────┘  │
│                                                                         │
│  ┌──────────┐  ┌──────────┐  ┌──────────────────────────────────────┐  │
│  │  Bz 24ч  │  │Рентг. 24ч│  │  Рекомендации по распространению ✕  │  │
│  │  ✕    ◢  │  │  ✕    ◢  │  │                               ◢  │  │
│  └──────────┘  └──────────┘  └──────────────────────────────────────┘  │
│                                                                         │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │  Предупреждения  ✕  ◢                                           │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                                                                         │
│  Все панели: янтарная рамка · ✕ закрыть · ◢ размер · сетка (2px)      │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## 🖥️ Установка

### Шаг 1 — Требования Python

```bash
pip install pillow
```

Optional for system tray notifications:

```bash
pip install pystray
```

### Шаг 2 — Установка языковых пакетов

HAMIOS ships with English as the built-in language. All other languages are in separate `.json` files.

**Download:**
Get the language files from the [latest release](https://github.com/fvdijke/HAMIOS/releases) — download `langs.zip`.

**Directory structure:**
```
HAMIOS.exe  (or HAMIOS.py)
langs\
  lang_nl.json    ← Nederlands
  lang_de.json    ← Deutsch
  lang_fr.json    ← Français
  lang_it.json    ← Italiano
  lang_es.json    ← Español
  lang_no.json    ← Norsk
  lang_pl.json    ← Polski
  lang_sv.json    ← Svenska
  lang_da.json    ← Dansk
  lang_fi.json    ← Suomi
  lang_pt.json    ← Português
  lang_ja.json    ← 日本語
  lang_ru.json    ← Русский
```

> The `langs/` folder must be placed **next to** `HAMIOS.exe` or `HAMIOS.py`.

**Creating your own language pack:**
Copy an existing `.json` file, change `meta.code` and `meta.name`, then translate the `strings` and `solar_tips` sections. HAMIOS will detect the new pack automatically on startup.

### Шаг 3 — Запуск

```bash
python HAMIOS.py
```

### Автономный EXE (Windows) — рекомендуется

Download `HAMIOS.exe` and the `langs/` folder from the [latest release](https://github.com/fvdijke/HAMIOS/releases). No Python required.

Build from source:

```bash
pip install pyinstaller
pyinstaller HAMIOS.spec
# → dist\HAMIOS.exe
# Then copy langs\ next to the EXE
```

---

## 📁 Файлы данных

| Файл | Содержание |
|------|------------|
| `HAMIOS.ini` | Все пользовательские настройки (QTH, тема, язык, пороги предупреждений, …) |
| `hamios_layouts.json` | Предустановки макетов панелей |
| `hamios_tle.json` | Кэшированные TLE-орбитальные элементы для отслеживания спутников |
| `hamios_spy_stations.json` | База данных шпионских/цифровых станций (редактируемая) |
| `langs/*.json` | Языковые пакеты |

---

## 🔭 Модель распространения

```
foF2 = 4.0 + (SFI − 70) × 0.065 + SSN × 0.012
MUF  = foF2 × latitude-factor × day/night-factor × 3.8
LUF  = (3.5 + K × 0.8) × auroral-factor / 10^(SNR/20)
```

**Band quality**: optimum around 55 % of the MUF/LUF window → 100 %.

---

## ⌨️ Взаимодействие с мышью

| Action | Effect |
|--------|--------|
| Scroll wheel on map | Zoom 1×–8× |
| Click + drag on map | Pan viewport |
| Left-click on map | Great-circle path + path propagation |
| Right-click on map | Reset zoom/pan · clear path |
| Hover on map / bands / chart | Detailed tooltip |
| Click on legend label | Toggle band in history chart |

---

## 💻 Системные требования

| | Minimum | Recommended |
|-|---------|------------|
| OS | Windows 10 | Windows 11 |
| Screen resolution | 1280 × 900 | 1920 × 1080 or wider |
| Python | 3.10 | 3.12+ |
| Internet | Required (data feeds) | — |

> v4.0.1 использует свободный холст панелей. Размещайте панели свободно на экране любого размера. Широкий дисплей (≥ 1920 px) обеспечивает наиболее комфортное рабочее пространство.

---

## 🔧 Планы на будущее

- Stabilise CAT interface (Yaesu/Kenwood/Icom)
- SDR integration
- Logging connection (ADIF/WSJTX)

---

## 📜 Лицензия

Бесплатно для личного некоммерческого использования в любительской радиосвязи.

---

