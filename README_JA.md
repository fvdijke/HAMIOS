# 📡 HAMIOS v3.3

**Windows向けHF伝搬・DXモニター**

> v3.3 — フットプリントオーバーレイ付き衛星追跡 · スパイ局/ナンバーズ局データベース · 嵐予報修正 · テーマ改善 · パフォーマンス

*Conceived by Frank van Dijke · Developed with Claude AI*

HAMIOSはアマチュア無線家にHF伝搬、太陽活動、DXの機会についてのリアルタイム情報を提供します — モダンなダークGUIで。

---

## ✨ 機能

### 🌍 インタラクティブ世界地図 *(ウィンドウ中央)*
- 正距円筒図法NASAマップ、初回起動時に自動ダウンロード
- **固定高さ（380px）**による正確な2:1レンダリング — 水平歪みなし
- **昼夜境界線**と柔らかい移行ゾーン
- **グレーライン**（琥珀色帯、約1000km幅）
- **太陽・月の位置**（地心計算）
- **QTHマーカー**（青い照準点）— ヘッダーで緯度/経度設定可
- **大圏路**: 地図クリック → 距離 + 方位 + **その経路のバンド品質**
- **ITU地域オーバーレイ** R1/R2/R3（公式 ITU RR 第5条）
- **メイデンヘッドロケーターグリッド**（20° × 10°、AA–RRラベル）
- **コールサインプレフィックスレイヤー**（約110 DXCC エンティティ）
- **ズーム/パン**: マウスホイール1×–8×、クリック+ドラッグでパン、右クリックでリセット
- **地図オーバーレイのグループ化**（地図下部）:
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

### 🛰 衛星追跡 *(ヘッダーの🛰 Satボタン)*
- **Celestrak**からTLEデータをダウンロード (Amateur / ISS / Weather / CubeSat)
- **カテゴリフィルター**: すべて · Amateur · ISS · Weather · CubeSat
- 衛星ごと: **位置ドット** (●)、**軌道パス** (~)、**フットプリント**を地図上で切替
- QTHが衛星の**カバレッジゾーン内**に入ると**フットプリントが緑色**になる
- **通知パネル**に現在QTH上空の衛星と仰角を表示
- 軌道パス時刻はローカル時間で表示 (CEST / CET)
- **↻ TLE**ボタンで軌道要素をオンデマンド更新
- `hamios_tle.json`にキャッシュ

### 🕵 スパイ局/ナンバーズ局 *(ヘッダーの🕵 Spyボタン)*
- 24の既知ナンバーズ局およびスパイ無線局のスクロール可能なテーブル
- 列: ステータス (● アクティブ / 過去)、名称、国、周波数、モード
- **ソート可能な列** — 任意のヘッダーをクリックでソート; 再クリックで逆順
- **フィルター**: アクティブ/非アクティブ状態、フリーテキスト検索 (名称、国、周波数)
- 行にホバーすると詳細な説明と放送スケジュールを表示
- データファイル: `hamios_spy_stations.json` (編集可能)

### 🔵 WSPR / PSKReporter Spots on Map
- Live propagation paths from **wspr.rocks** (WSPR) and **pskreporter.info** (FT8/FT4)
- Connection lines: **colour = band**, **thickness = SNR**

### 📍 DX Spot Markers on Map
- Active DX cluster spots: dot at DX location + line to spotter, colour-coded by band
- Click a dot to show callsign, frequency and comment

### 🌞 太陽・電離層データ

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
| 🛰 衛星がQTH上空 | 常時アクティブ | 選択した衛星のうちQTH上空にある衛星と仰角を表示 |

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

### ⚙️ Other
- **Dynamic themes**: Midnight · DeepOcean · HighContrast
- **System tray**: minimise to tray, tray notifications
- **Tooltips** with explanation per solar parameter
- **Auto-refresh**: Off / 30 s / 1 min / 5 min / 10 min / 30 min / 1 hour
- **Scrolling ticker** with current propagation tips
- All settings saved to `HAMIOS.ini`

---

## 🖥️ Layout (v3.0)

```
┌─────────────────────────────────────────────────────────────────────────┐
│ HEADER  (title · exit · CAT · interval · lang · QTH · theme · Sat · Spy · time) │
├──────────┬──────────────────────────────────┬────────────┬──────────────┤
│  Solar   │      World Map (central)         │    HF      │              │
│ Ionosph. │      380 px tall, zoom/pan       │    Band    │   DX Spots   │
│  200 px  │   Display: Sun Moon Graylijn     │ Reliability│  (full       │
│          │   Data: WSPR Spots CS Locator    │   420 px   │  height)     │
│          ├──────────────────────────────────┤            │   360 px     │
│          │  Schedule │  Band Hist  │  Bz   │            │              │
│          │   (1/3)   │    (1/3)    │ (1/3) │            │              │
├──────────┴──────────────────────────────────┴────────────┤              │
│              Propagation Analysis & Advice                │              │
├───────────────────────────────────────────────────────────┴──────────────┤
│ TICKER                                                                    │
└──────────────────────────────────────────────────────────────────────────┘
```

---

## 🖥️ インストール

### ステップ1 — Python要件

```bash
pip install pillow
```

Optional for system tray notifications:

```bash
pip install pystray
```

### ステップ2 — 言語パックのインストール

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

### ステップ3 — 実行

```bash
python HAMIOS.py
```

### スタンドアロン EXE（Windows）— 推奨

Download `HAMIOS.exe` and the `langs/` folder from the [latest release](https://github.com/fvdijke/HAMIOS/releases). No Python required.

Build from source:

```bash
pip install pyinstaller
pyinstaller HAMIOS.spec
# → dist\HAMIOS.exe
# Then copy langs\ next to the EXE
```

---

## 🔭 伝搬モデル

```
foF2 = 4.0 + (SFI − 70) × 0.065 + SSN × 0.012
MUF  = foF2 × latitude-factor × day/night-factor × 3.8
LUF  = (3.5 + K × 0.8) × auroral-factor / 10^(SNR/20)
```

**Band quality**: optimum around 55 % of the MUF/LUF window → 100 %.

---

## ⌨️ マウス操作

| Action | Effect |
|--------|--------|
| Scroll wheel on map | Zoom 1×–8× |
| Click + drag on map | Pan viewport |
| Left-click on map | Great-circle path + path propagation |
| Right-click on map | Reset zoom/pan · clear path |
| Hover on map / bands / chart | Detailed tooltip |
| Click on legend label | Toggle band in history chart |

---

## 💻 システム要件

| | Minimum | Recommended |
|-|---------|------------|
| OS | Windows 10 | Windows 11 |
| Screen resolution | 1280 × 900 | 1920 × 1080 or wider |
| Python | 3.10 | 3.12+ |
| Internet | Required (data feeds) | — |

> v3.0 makes best use of a wide display (≥ 1768 px) with the DX column as an additive right panel. On narrower screens the window scales proportionally and all panels remain usable.

---

## 🔧 将来のアイデア

- Stabilise CAT interface (Yaesu/Kenwood/Icom)
- SDR integration
- Logging connection (ADIF/WSJTX)

---

## 📜 ライセンス

個人的・非商業的なアマチュア無線利用に限り無料。

---

