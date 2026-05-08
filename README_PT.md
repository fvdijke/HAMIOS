# 📡 HAMIOS v4.0.1

**Monitor de propagação HF e DX para Windows**

> v4.0.1 — Painéis arrastáveis e redimensionáveis · Caixa de diálogo de Configurações unificada · Otimizações de desempenho · Gráfico histórico solar

*Conceived by Frank van Dijke · Developed with Claude AI*

HAMIOS fornece aos radioamadores informações em tempo real sobre propagação HF, atividade solar e oportunidades DX — numa interface gráfica moderna e escura.

---

## ✨ Funcionalidades

### 🌍 Mapa mundial interativo *(centralizado na janela)*
- Mapa NASA equiretangular, descarregado automaticamente no primeiro uso
- **Altura fixa (380 px)** com renderização 2:1 correta — sem distorção horizontal
- **Terminador dia/noite** com zona de transição suave
- **Linha cinzenta** (banda âmbar, ~1000 km de largura)
- **Posição do sol e da lua** (cálculo geocêntrico)
- **Marcador QTH** (retículo azul) — lat/lon configurável no cabeçalho
- **Caminho círculo máximo**: clique no mapa → distância + rumo + **qualidade de banda para esse percurso**
- **Sobreposição regiões UIT** R1/R2/R3 (oficial UIT RR Art. 5)
- **Grelha de localizadores Maidenhead** (20° × 10°, etiquetas AA–RR)
- **Camada de prefixos de indicativos** (~110 entidades DXCC)
- **Zoom/panorâmica**: roda do rato 1×–8×, clicar+arrastar para panorâmica, clique direito para repor
- **Sobreposições do mapa agrupadas** abaixo do mapa:
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

### 🖥️ Sistema de painéis *(v4.0.1)*
- **11 painéis livremente arrastáveis e redimensionáveis** numa tela de ambiente de trabalho livre
- Cada painel tem uma borda âmbar de 1px, barra de título com botão ✕ de fechar e puxador ◢ de redimensionamento
- **Ajuste à grelha** (2px) ao soltar após arrastar/redimensionar para alinhamento limpo
- Painéis: Fiabilidade das bandas HF · Mapa mundial · Solar/Ionosfera · Alertas · Horário das bandas · Histórico das bandas · Kp 48h · Bz 24h · Raios X 24h · Spots DX · Conselhos de propagação
- **⚙ Caixa de diálogo Configurações** contém toda a configuração: QTH · Idioma · Tema · Dicas de ferramentas · Ticker · Horário de verão · Visibilidade dos painéis · Gestão de layouts
- **Predefinições de layout**: guardar/carregar/substituir/eliminar perfis com nome em `hamios_layouts.json`
- **Guardar como predefinição**: guarda o layout atual como layout de arranque

### 🛰 Rastreamento de satélites *(botão 🛰 Sat no cabeçalho)*
- Dados TLE descarregados do **Celestrak** (Amateur / ISS / Weather / CubeSat)
- **Filtro por categoria**: Todos · Amateur · ISS · Weather · CubeSat
- Por satélite: alternar **ponto de posição** (●), **trajetória orbital** (~) e **pegada** no mapa
- **A pegada fica verde** quando o QTH está dentro da zona de cobertura do satélite
- **Painel de notificações** mostra os satélites atualmente acima do QTH com ângulo de elevação
- Horários das trajetórias em hora local (CEST / CET)
- Botão **↻ TLE** para atualização manual dos elementos orbitais
- Em cache em `hamios_tle.json`

### 🕵 Estações espiã / de números *(botão 🕵 Spy no cabeçalho)*
- Tabela com deslocamento de 24 estações de números e estações de rádio espiã conhecidas
- Colunas: estado (● ativo / histórico), nome, país, frequências, modo
- **Colunas ordenáveis** — clique em qualquer cabeçalho para ordenar; clique novamente para inverter
- **Filtro** por estado ativo/inativo e pesquisa de texto livre (nome, país, frequência)
- **Passar o rato** sobre uma linha para ver descrição completa + horário de emissão
- Ficheiro de dados: `hamios_spy_stations.json` (editável)

### 🔵 WSPR / PSKReporter Spots on Map
- Live propagation paths from **wspr.rocks** (WSPR) and **pskreporter.info** (FT8/FT4)
- Connection lines: **colour = band**, **thickness = SNR**

### 📍 DX Spot Markers on Map
- Active DX cluster spots: dot at DX location + line to spotter, colour-coded by band
- Click a dot to show callsign, frequency and comment

### 🌞 Dados solares e ionosféricos

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
| 🛰 Satélite sobre QTH | Sempre ativo | Mostra quais satélites selecionados estão acima do QTH com elevação |

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

### ⚙️ Outros
- **Temas dinâmicos**: Midnight · DeepOcean · HighContrast
- **Bandeja do sistema**: minimizar para a bandeja, notificações
- **Dicas de ferramentas** com explicação por parâmetro solar
- **Atualização automática**: Desativado / 30 s / 1 min / 5 min / 10 min / 30 min / 1 hora
- **Ticker deslizante** com dicas de propagação atuais
- **Sistema de painéis arrastáveis**: organize e redimensione livremente todos os painéis
- **Predefinições de layout**: guarde e alterne entre disposições de painéis personalizadas
- Todas as configurações guardadas em `HAMIOS.ini`

---

## 🖥️ Layout (v4.0.1) — Painéis flutuantes livres

```
┌─────────────────────────────────────────────────────────────────────────┐
│  ⚙ Configurações  (QTH · Idioma · Tema · Dicas · Ticker · Hora verão · Painéis · Layouts) │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  ┌──────────────┐  ┌──────────────────────────────┐  ┌──────────────┐  │
│  │Solar/Ionosfer│  │      Mapa mundial         ✕  │  │Bandas HF ✕  │  │
│  │     ✕    ◢  │  │   zoom/pan · sobrep.      ◢  │  │Fiabilidade◢ │  │
│  └──────────────┘  └──────────────────────────────┘  └──────────────┘  │
│                                                                         │
│  ┌─────────────┐  ┌─────────────┐  ┌──────────┐  ┌──────────────────┐  │
│  │HorBandas    │  │HistBandas   │  │  Kp 48h  │  │  Spots DX    ✕  │  │
│  │    ✕    ◢  │  │    ✕    ◢  │  │  ✕    ◢  │  │             ◢  │  │
│  └─────────────┘  └─────────────┘  └──────────┘  └──────────────────┘  │
│                                                                         │
│  ┌──────────┐  ┌──────────┐  ┌──────────────────────────────────────┐  │
│  │  Bz 24h  │  │RaiosX 24h│  │  Conselhos de propagação         ✕  │  │
│  │  ✕    ◢  │  │  ✕    ◢  │  │                               ◢  │  │
│  └──────────┘  └──────────┘  └──────────────────────────────────────┘  │
│                                                                         │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │  Alertas  ✕  ◢                                                  │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                                                                         │
│  Todos os painéis: borda âmbar · ✕ fechar · ◢ tamanho · grelha (2px)  │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## 🖥️ Instalação

### Passo 1 — Requisitos Python

```bash
pip install pillow
```

Optional for system tray notifications:

```bash
pip install pystray
```

### Passo 2 — Instalar pacotes de idioma

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

### Passo 3 — Executar

```bash
python HAMIOS.py
```

### EXE autónomo (Windows) — recomendado

Download `HAMIOS.exe` and the `langs/` folder from the [latest release](https://github.com/fvdijke/HAMIOS/releases). No Python required.

Build from source:

```bash
pip install pyinstaller
pyinstaller HAMIOS.spec
# → dist\HAMIOS.exe
# Then copy langs\ next to the EXE
```

---

## 📁 Ficheiros de dados

| Ficheiro | Conteúdo |
|----------|----------|
| `HAMIOS.ini` | Todas as configurações do utilizador (QTH, tema, idioma, limiares de alerta, …) |
| `hamios_layouts.json` | Predefinições de layout dos painéis |
| `hamios_tle.json` | Elementos orbitais TLE em cache para rastreamento de satélites |
| `hamios_spy_stations.json` | Base de dados de estações espiã/números (editável) |
| `langs/*.json` | Pacotes de idioma |

---

## 🔭 Modelo de propagação

```
foF2 = 4.0 + (SFI − 70) × 0.065 + SSN × 0.012
MUF  = foF2 × latitude-factor × day/night-factor × 3.8
LUF  = (3.5 + K × 0.8) × auroral-factor / 10^(SNR/20)
```

**Band quality**: optimum around 55 % of the MUF/LUF window → 100 %.

---

## ⌨️ Interação com o rato

| Action | Effect |
|--------|--------|
| Scroll wheel on map | Zoom 1×–8× |
| Click + drag on map | Pan viewport |
| Left-click on map | Great-circle path + path propagation |
| Right-click on map | Reset zoom/pan · clear path |
| Hover on map / bands / chart | Detailed tooltip |
| Click on legend label | Toggle band in history chart |

---

## 💻 Requisitos do sistema

| | Minimum | Recommended |
|-|---------|------------|
| OS | Windows 10 | Windows 11 |
| Screen resolution | 1280 × 900 | 1920 × 1080 or wider |
| Python | 3.10 | 3.12+ |
| Internet | Required (data feeds) | — |

> v4.0.1 usa uma tela de painéis livre. Organize os painéis livremente em qualquer tamanho de ecrã. Um ecrã largo (≥ 1920 px) oferece o espaço de trabalho mais confortável.

---

## 🔧 Ideias futuras

- Stabilise CAT interface (Yaesu/Kenwood/Icom)
- SDR integration
- Logging connection (ADIF/WSJTX)

---

## 📜 Licença

Gratuito para uso pessoal e não comercial em rádio amadorismo.

---

