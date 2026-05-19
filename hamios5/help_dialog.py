"""HAMIOS v5 — Help venster

Doorzoekbare help met categorieën die uitleggen wat het programma doet
en hoe het werkt.
"""

from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QFont, QColor, QPixmap, QPainter
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QSplitter,
    QLabel, QLineEdit, QPushButton, QListWidget, QListWidgetItem,
    QTextEdit, QFrame, QWidget
)

from .theme import ACCENT, BG_PANEL, BG_SURFACE, BG_ROOT, TEXT_H1, TEXT_DIM, TEXT_BODY, BORDER
from .geometry import save_geom, restore_geom
from .i18n import tr, get_language, language_changed

# ── Help-inhoud per taal ──────────────────────────────────────────────────────
# Elk item: (categorie, titel, html_inhoud)

_HELP = [
    # ── Aan de slag ───────────────────────────────────────────────────────────
    ("🚀 Aan de slag", "Welkom", """
<h3>Welkom bij HF Propagation &amp; Atmosphere Monitor</h3>
<p>Een real-time HF-propagatie- en DX-monitor voor radioamateurs.
Het toont solar-data, bandcondities, live DX-spots, satelliettracking,
bliksemdetectie en meer — alles op één scherm.</p>

<h4>Eerste stappen</h4>
<ol>
<li>Stel uw <b>roepletters, QTH en antenne</b> in via <b>⚙ Instellingen → Station</b>.</li>
<li>Voer uw <b>Maidenhead-locator</b> in (bijv. JO22NC) of gebruik lat/lon.</li>
<li>Pas het <b>refresh-interval</b> aan in de header (standaard 5 minuten).</li>
<li>Sleep en resize de <b>panelen</b> naar wens. Sla de layout op via Instellingen → Layout.</li>
</ol>
"""),

    ("🚀 Aan de slag", "Panelen en layout", """
<h3>Panelen en layout</h3>
<p>Het programma heeft <b>15 vrijbeweegbare panelen</b> op een virtueel bureaublad:</p>
<ul>
<li>Sleep een paneel aan de titelbalk.</li>
<li>Vergroot/verklein via de rechter-onderhoek.</li>
<li>Sluit een paneel via het ✕ in de titelbalk; heropen via <b>Instellingen → Panelen</b>.</li>
<li>Sla de huidige layout op als standaard of als benoemd profiel via <b>Instellingen → Layout</b>.</li>
</ul>

<h4>Snap-to-grid</h4>
<p>Panelen snappen bij loslaten aan een raster (instelbaar in Instellingen → Kaart).
Standaard 10 px.</p>
"""),

    # ── Kaart ─────────────────────────────────────────────────────────────────
    ("🌍 Kaart", "Wereldkaart en overlays", """
<h3>Wereldkaart</h3>
<p>De kaart is een equirectangulaire NASA-kaart (worldmap_eq.jpg). Overlays zijn
in- en uitschakelbaar via de <b>🗺 Overlays</b>-knop in de header.</p>

<h4>Beschikbare overlays</h4>
<ul>
<li><b>Dag/nacht terminator</b> — geeft aan waar het dag of nacht is.</li>
<li><b>Grayline</b> — schemerband van ~1000 km, ideaal voor DX.</li>
<li><b>Aurora-ovaal</b> — gebaseerd op de actuele K-index (IGRF-2025 model).</li>
<li><b>Zon-positie</b> — geocentrisch berekend, met stralenpictogram.</li>
<li><b>Maan-positie</b> — met live maanfase-icoon en QTH-horizonaanduiding (▲/▼).</li>
<li><b>Live DX-spots</b> — gekleurde stippen per band, van DXWatch.</li>
<li><b>Satelliet-paden</b> — positie, orbitpad en footprint van geselecteerde satellieten.</li>
<li><b>Bliksem</b> — live ontladingen van Blitzortung.org.</li>
<li><b>Maidenhead-raster</b> — 20°×10°-velden met 2-letter labels.</li>
</ul>

<h4>Lettergroottes overlays</h4>
<p>Instelbaar via <b>Instellingen → Kaart → Overlay lettergroottes</b>.</p>
"""),

    ("🌍 Kaart", "QTH en grootcirkelpad", """
<h3>QTH-markering</h3>
<p>Uw QTH wordt weergegeven als een blauw kruis op de kaart.
Stel uw locatie in via Instellingen → Station (lat/lon of Maidenhead-locator).</p>

<h4>Grootcirkelpad</h4>
<p>Klik op een punt op de kaart om het grootcirkelpad van uw QTH naar dat punt
te tekenen. Het toont ook de afstand (km), peiling en de beste band voor dat pad.</p>
"""),

    # ── Solar / propagatie ────────────────────────────────────────────────────
    ("☀ Solar & Propagatie", "Solar / Ionosfeer paneel", """
<h3>Solar / Ionosfeer</h3>
<p>Dit paneel toont de actuele solar-parameters die propagatie bepalen.
Elke rij heeft <b>vijf kolommen</b>:</p>
<ol>
<li><b>Afkorting</b> — bijv. SFI, SSN, K, A, Bz</li>
<li><b>Waarde</b> — actuele meetwaarde (vet)</li>
<li><b>Eenheid</b> — bijv. SFU, nT, km/s</li>
<li><b>Duiding</b> — kleurgecodeerde beoordeling (laag / matig / hoog / storm)</li>
<li><b>Volledige naam</b> — uitgeschreven betekenis van de afkorting (cursief)</li>
</ol>

<h4>Parameters</h4>
<ul>
<li><b>SFI</b> — <i>Solar Flux Index</i> — maat voor ionosferische ionisatie. Hoog = betere HF-condities.</li>
<li><b>SSN</b> — <i>Sunspot Number</i> — zonnevlekgetal. Correleert met SFI.</li>
<li><b>K</b> — <i>K-index</i> — geomagnetische activiteit (0–9). Laag = stabiel. ≥5 = storm.</li>
<li><b>A</b> — <i>A-index</i> — daggemiddelde geomagnetische activiteit.</li>
<li><b>Bz</b> — <i>IMF Bz-component</i> — Z-component van het interplanetair magneetveld (nT).
  Negatief = verhoogde kans op storm.</li>
<li><b>Vsw</b> — <i>Zonnewindsnelheid</i> — snelheid van de zonnewind (km/s).</li>
<li><b>Nsw</b> — <i>Zonnewinddichtheid</i> — deeltjesdichtheid van de zonnewind (p/cm³).</li>
<li><b>Xray</b> — <i>X-straling klasse</i> — actuele klasse (A/B/C/M/X). M en X = zonnevlam.</li>
</ul>
<p>Bronnen: NOAA SWPC, bijgewerkt elke <i>N</i> minuten (instelbaar in header).</p>
"""),

    ("☀ Solar & Propagatie", "Band Betrouwbaarheid", """
<h3>HF Band Betrouwbaarheid</h3>
<p>Toont voor elke HF-band (160m–6m) de berekende betrouwbaarheid als percentage,
plus de huidige MUF en LUF.</p>

<h4>Hoe werkt het?</h4>
<p>Het propagatiemodel gebruikt SFI, SSN, K-index, QTH-breedte, antenne-versterking,
zendvermogen en dag/nacht-correctie om per band een percentage te berekenen:</p>
<ul>
<li><b>≥ 75%</b> — Uitstekend (groen)</li>
<li><b>50–74%</b> — Goed</li>
<li><b>25–49%</b> — Matig (oranje)</li>
<li><b>< 25%</b> — Slecht (rood)</li>
<li><b>0%</b> — Gesloten (grijs)</li>
</ul>

<h4>Klik op een balk</h4>
<p>Klikken op een band opent een popup met kiesbare frequenties (SSB/CW/FT8/WSPR)
voor directe CAT-afstemming.</p>
"""),

    ("☀ Solar & Propagatie", "Bandcondities en Bandopeningsschema", """
<h3>Bandcondities</h3>
<p>Toont voor elke band de conditie overdag en 's nachts als tekst (Uitstekend/Goed/Matig/Slecht/Dicht).
Klik op een bandnaam om de frequentie naar uw radio te sturen via CAT.</p>

<h3>Bandopenings-schema</h3>
<p>Een 24-uursraster dat per band de betrouwbaarheid per uur van de dag toont.
Groen = open, oranje = matig, rood = slecht, donker = gesloten.
De huidige lokale tijd is omrand in amber.</p>
<p>Hover voor details (band, tijdstip, %). Klik om de frequentie naar uw radio te sturen.</p>
"""),

    ("☀ Solar & Propagatie", "Propagatie Advies", """
<h3>Propagatie Advies</h3>
<p>AI-stijl analysekaarten die samengevat advies geven per band.
De kaarten worden bijgewerkt bij elke solar-refresh.</p>
<p>Wijzigingen in het advies worden ook naar het <b>Meldingen-paneel</b> gestuurd.</p>
"""),

    # ── Geschiedenis ──────────────────────────────────────────────────────────
    ("📈 Geschiedenis", "Band Verloop en Solar Verloop", """
<h3>Band Verloop (historiek)</h3>
<p>Toont de berekende band-betrouwbaarheid voor alle 11 HF-banden over de afgelopen
24u (instelbaar). Data wordt elke refresh opgeslagen in <b>HAMIOS_history.csv</b>
(90 dagen bewaard).</p>
<p><b>Klik op een band in de legenda</b> om die band aan/uit te zetten.</p>

<h3>Solar Verloop</h3>
<p>Toont het SFI-verloop in de tijd. Rode verticale strepen duiden momenten aan
met verhoogde K-index (geomagnetische storm).</p>

<h4>Tijdbereik</h4>
<p>Het tijdbereik is via de <code>set_hours()</code>-methode aanpasbaar in de
toekomst (v5.1). Momenteel: 24u.</p>
"""),

    # ── DX ────────────────────────────────────────────────────────────────────
    ("📡 DX Spots", "Live DX Spots", """
<h3>Live DX Spots</h3>
<p>Real-time DX-clusterdata van <b>DXWatch.com</b>. De tabel wordt bijgewerkt bij elke
solar-refresh (standaard 5 minuten).</p>

<h4>Kolommen</h4>
<ul>
<li><b>UTC</b> — tijdstip van de spot</li>
<li><b>Band</b> — HF-band (kleurgecodeerd)</li>
<li><b>MHz</b> — exacte frequentie</li>
<li><b>DX</b> — DX-roepletters (gekleurde bandkleur)</li>
<li><b>Spotter</b> — wie de spot maakte</li>
<li><b>Comment</b> — eventuele opmerking</li>
</ul>

<h4>Filteren</h4>
<ul>
<li><b>Eigen continent</b> — toon alleen spots door spotters op uw continent.</li>
<li><b>Heatmap</b> — schakel naar een bandactiviteitsgrafiek over 24u.</li>
</ul>

<h4>CAT-afstemming</h4>
<p>Klik op een rij om uw radio direct op de spotfrequentie af te stemmen (SSB).</p>
"""),

    # ── Satelliet ─────────────────────────────────────────────────────────────
    ("🛰 Satellieten", "Satelliet Tracking", """
<h3>Satelliet Tracking</h3>
<p>Real-time positie, orbitpaden en footprints van HAM-satellieten, ISS, weersat. etc.
TLE-data van <b>CelesTrak</b>.</p>

<h4>Gebruik</h4>
<ol>
<li>Klik op <b>🛰 Satellite</b> in de header.</li>
<li>Kies een categorie (Alle/Amateur/ISS/Weather/CubeSat).</li>
<li>Vink <b>Positie</b> aan om de satelliet op de kaart te tonen.</li>
<li>Vink <b>Pad</b> aan om het orbitpad te tonen (verleden + toekomst instelbaar).</li>
<li>Vink <b>Footprint</b> aan om het dekkingsgebied te tonen
  (geel = QTH buiten bereik, groen = QTH in bereik).</li>
</ol>

<h4>Geselecteerd-filter</h4>
<p>Het vinkje <b>Geselecteerd</b> filtert de lijst op uw geselecteerde satellieten.
Standaard <b>uitgeschakeld</b> (alle satellieten zichtbaar). De instelling wordt
onthouden tussen sessies.</p>

<h4>TLE vernieuwen</h4>
<p>Klik <b>↻ TLE vernieuwen</b> voor verse baanelementendata van CelesTrak.</p>

<h4>Orbitpaden</h4>
<p>Verleden (standaard <b>1u</b>) en toekomst (standaard <b>1u</b>) zijn afzonderlijk
instelbaar. Waarde 0 = geen pad weergeven.</p>

<h4>Satelliet melding</h4>
<p>Via <b>Instellingen → Meldingen → Satelliet ping</b> kunt u een geluidssignaal
inschakelen wanneer een geselecteerde satelliet boven uw horizon komt.</p>
"""),

    # ── Bliksem ───────────────────────────────────────────────────────────────
    ("⚡ Bliksem", "Bliksemdetectie en QRN", """
<h3>Bliksemdetectie</h3>
<p>Live bliksemontladingen van het wereldwijde <b>Blitzortung.org</b>-netwerk.
Elke ontlading verschijnt als een animerende ring op de kaart en een stip die langzaam vervaagt.</p>

<h4>QRN-advies</h4>
<p>Het Onweer-paneel toont het QRN-niveau op basis van het aantal ontladingen
binnen <b>2000 km</b> van uw QTH:</p>
<ul>
<li><b>Geen activiteit</b> — geen ontladingen nabij</li>
<li><b>Laag</b> — weinig QRN verwacht</li>
<li><b>Matig</b> — enige QRN op LF/MF/160m</li>
<li><b>Hoog</b> — QRN op 160m/80m/40m</li>
<li><b>Zwaar</b> — sterke QRN op alle lage banden</li>
</ul>

<h4>Aantal ontladingen</h4>
<p>Het paneel toont het <b>totaal aantal ontladingen</b> binnen de ingestelde periode,
bijv. <code>127 /10m</code>. De periode is gelijk aan de <b>Fade duur</b> in
Instellingen → Bliksem (standaard 10 minuten).</p>

<h4>Meest nabije ontlading</h4>
<p>De afstand tot de dichtstbijzijnde recente ontlading wordt getoond als
<b>Meest nabije ontlading</b> met km-afstand en richting.</p>

<h4>Radius-meldingen</h4>
<p>Stel in <b>Instellingen → Bliksem</b> een drempelafstand in voor:</p>
<ul>
<li><b>Header-melding (rood)</b> — ⚡ ONWEER X km verschijnt gecentreerd in de header.</li>
<li><b>Geluidssignaal (oranje)</b> — kort tick-geluid (Geigerteller-stijl) bij ontladingen
binnen de ingestelde straal.</li>
</ul>
<p>Beide cirkels zijn zichtbaar op de kaart zolang bliksemdetectie is ingeschakeld.
Wanneer bliksemdetectie is uitgeschakeld zijn de meldingscirkels verborgen.</p>

<h4>Prestaties</h4>
<p>Het update-interval (Instellingen → Bliksem → Prestaties) bepaalt hoe vaak
de overlay hertekend wordt. 100 ms = vloeiend, 500 ms = normaal, 2000 ms = zuinig.</p>
"""),

    # ── SpyStations ───────────────────────────────────────────────────────────
    ("🕵 SpyStations", "SpyStations en nummerstations", """
<h3>SpyStations</h3>
<p>Een database met bekende nummerstations, militaire seinstations, tijdsignalen
en weerdiensten op HF.</p>

<h4>Gebruik</h4>
<ul>
<li>Zoek op naam, land of frequentie via de zoekbalk.</li>
<li>Filter op Actief/Inactief.</li>
<li>Klik op een kolom-header om te sorteren (↑/↓).</li>
<li>Klik op een station → frequentieknoppen verschijnen rechtsonder.
  Klik een frequentie om uw radio direct af te stemmen via CAT.</li>
</ul>

<h4>Categorieën</h4>
<ul>
<li>Russische nummerstations (UVB-76, M14a, M03, G06...)</li>
<li>Cubaanse/Noord-Koreaanse stations (Atencion, HM01...)</li>
<li>Marine seinstations (4XZ, RDL, XSL, NDT...)</li>
<li>Tijdsignalen (WWV, WWVH, CHU, DCF77, RWM...)</li>
<li>Weerfax (DDH47, GFA, JMH)</li>
<li>Historisch inactief (Lincolnshire Poacher, Swedish Rhapsody...)</li>
</ul>
"""),

    # ── EIBI ─────────────────────────────────────────────────────────────────
    ("📻 EIBI", "EIBI Kortegolf-frequentielijst", """
<h3>EIBI Kortegolf-frequentielijst</h3>
<p>De actuele kortegolf-omroepplanning van <b>eibispace.de</b> (Eike Bierwirth).
Duizenden frequenties van internationale omroepen wereldwijd.</p>

<h4>Gebruik</h4>
<ul>
<li>Klik <b>⬇ Lijst bijwerken</b> om de laatste planning te downloaden.</li>
<li>Zoek op station, taal, land of frequentie.</li>
<li>Filter op band of schakel <b>Alleen nu actief</b> in voor het huidige tijdstip.</li>
<li>Klik op een rij om uw radio af te stemmen (AM-modus via CAT).</li>
</ul>

<h4>Taalcodes</h4>
<p>Zet <b>Volledige namen</b> aan om taal- en doelgebied-codes te vertalen
(bijv. <i>E = Engels</i>, <i>FE = Verre Oosten</i>).</p>
"""),

    # ── FT8 / Digitaal ────────────────────────────────────────────────────────
    ("📡 FT8/Digitaal", "Digitale modi frequenties", """
<h3>FT8 / Digitale modi frequenties</h3>
<p>Standaard dial-frequenties voor FT8, FT4, WSPR, JS8Call, MSK144, Q65, JT65 en JT9
op alle banden (2200m t/m 23cm).</p>

<h4>Gebruik</h4>
<ul>
<li>Filter op band of modus.</li>
<li>Kleurcodering: amber=FT8, groen=FT4, blauw=WSPR, oranje=JS8Call, enz.</li>
<li>Klik op een rij om uw radio af te stemmen (USB-modus via CAT).</li>
</ul>

<h4>Vinkje "USB instellen"</h4>
<p>Standaard ingeschakeld: de modus wordt automatisch op USB gezet bij klikken.</p>
"""),

    # ── CAT ───────────────────────────────────────────────────────────────────
    ("📟 CAT", "CAT radio-interface", """
<h3>CAT Radio-interface</h3>
<p>CAT (Computer Aided Transceiver) maakt directe besturing van uw radio mogelijk
via de seriële poort. HAMIOS ondersteunt:</p>
<ul>
<li><b>Yaesu FT-950/2000/DX/3000/5000</b> — FA-commando (8 cijfers), standaard 38400 baud</li>
<li><b>Yaesu FT-817/857/897</b> — FA-commando</li>
<li><b>Kenwood / Elecraft</b> — FA-commando (11 cijfers)</li>
<li><b>Icom CI-V</b> — binair BCD-protocol</li>
</ul>

<h4>Instellen (Instellingen → CAT)</h4>
<ol>
<li>Klik op <b>⚙ Instellingen → CAT</b>.</li>
<li>Selecteer de seriële poort (wordt automatisch gescand).</li>
<li>Kies uw radiotype of gebruik een <b>Preset</b> (FT-950, FT-817, TS-590, K3/KX3).</li>
<li>Stel baudrate, databits, pariteit en stopbits in (of gebruik de preset-standaarden).</li>
<li>Schakel <b>CAT inschakelen</b> in.</li>
<li>Test de verbinding met de <b>Verbinding testen</b>-knop.</li>
</ol>

<h4>Seriële terminal</h4>
<p>Open de seriële terminal via <b>⚙ Instellingen → CAT → Seriële terminal openen</b>.
Het terminal-venster toont de verbindingsstatus en laat u handmatig CAT-commando's
typen en de raw radio-respons bekijken. Alle seriële parameters worden uitsluitend
in Instellingen → CAT ingesteld.</p>

<h4>Frequentie in header</h4>
<p>Zodra CAT verbonden is, verschijnt de actuele VFO-A-frequentie van uw radio
rechts van de CAT-knop in de header. De radio wordt elke 2 seconden gepeild.</p>
"""),

    # ── Meldingen ─────────────────────────────────────────────────────────────
    ("🔔 Meldingen", "Meldingen-paneel", """
<h3>Meldingen-paneel</h3>
<p>Verzamelt alle waarschuwingen op één plek:</p>
<ul>
<li><b>K-storm</b> — bij K-index ≥ drempel (instelbaar)</li>
<li><b>X-zonnevlam</b> — bij M- of X-klasse zonnevlam</li>
<li><b>QRN-niveau</b> — bij stijging van het lokale QRN-niveau</li>
<li><b>Onweer nabij</b> — bij bliksem binnen de ingestelde straal</li>
<li><b>Satelliet boven QTH</b> — als een geselecteerde satelliet in uw footprint zit</li>
<li><b>Propagatie-advies</b> — bij wijzigingen in de bandanalyse</li>
</ul>

<h4>FIFO-limiet</h4>
<p>Stel in Instellingen → Meldingen het maximale aantal te bewaren meldingen in.
Oudste meldingen worden automatisch verwijderd (standaard 50).</p>

<h4>Wis alles</h4>
<p>Klik op <b>Wis alles</b> om alle actieve meldingen te verwijderen.</p>
"""),

    # ── Instellingen ──────────────────────────────────────────────────────────
    ("⚙ Instellingen", "Instellingen overzicht", """
<h3>Instellingen</h3>
<p>Alle configuratie via <b>⚙ Instellingen</b> in de header. Alle wijzigingen
zijn <b>live</b> — u ziet het resultaat direct zonder opnieuw opstarten.</p>

<h4>Tabbladen</h4>
<ul>
<li><b>📡 Station</b> — roepletters, QTH, modus, vermogen, antenne</li>
<li><b>🪟 Panelen</b> — panelen tonen/verbergen</li>
<li><b>🗺 Kaart</b> — snap-raster, fontgroottes overlays</li>
<li><b>⚡ Bliksem</b> — fade-duur, nabijheidsmelding, geluid, prestaties</li>
<li><b>🔔 Meldingen</b> — K-drempel, X-flare, band-drempel, FIFO-limiet</li>
<li><b>📟 CAT</b> — seriële poort, radiotype, presets, terminal</li>
<li><b>📐 Layout</b> — standaard layout opslaan/herstellen, profielen</li>
<li><b>📦 Over</b> — versie-info, afhankelijkheden, bestandsstatus</li>
</ul>

<h4>Instellingen worden bewaard in</h4>
<p><code>hamios_config.json</code> in de programmamap. Alle instellingen — inclusief
vensterposities, CAT-configuratie, blikseminstellingen en satellietdata — staan
in dit één bestand.</p>
"""),

    ("⚙ Instellingen", "Layout-profielen", """
<h3>Layout-profielen</h3>
<p>Sla meerdere paneelindelingen op als profiel (bijv. "Contest", "DX-jagen", "Portable").</p>
<ol>
<li>Schik de panelen naar wens.</li>
<li>Ga naar <b>Instellingen → Layout → Profielen</b>.</li>
<li>Voer een naam in en klik <b>Opslaan als profiel</b>.</li>
<li>Later: klik <b>Laden</b> naast het gewenste profiel.</li>
</ol>

<h4>Standaard layout</h4>
<p>Klik <b>Opslaan als standaard</b> om de huidige indeling als startindeling in te stellen.
<b>Reset naar standaard</b> herstelt die indeling.</p>
"""),

    # ── Technisch ─────────────────────────────────────────────────────────────
    ("🔧 Technisch", "Vereisten en bestanden", """
<h3>Technische vereisten</h3>
<ul>
<li><b>Windows 10/11</b> (64-bit)</li>
<li><b>PySide6</b> ≥ 6.4 (vereist)</li>
<li><b>pyserial</b> (optioneel, voor CAT)</li>
<li><b>websocket-client</b> (optioneel, voor bliksemdetectie)</li>
</ul>

<h4>Bestanden</h4>
<ul>
<li><code>HAMIOS5.exe</code> — uitvoerbaar programma</li>
<li><code>worldmap_eq.jpg</code> — wereldkaart (vereist naast de EXE)</li>
<li><code>hamios_config.json</code> — alle instellingen en vensterposities</li>
<li><code>hamios_layouts.json</code> — paneelposities (legacy kopie)</li>
<li><code>hamios_spy_stations.json</code> — SpyStations database</li>
<li><code>hamios_tle.json</code> — satelliet TLE (wordt gedownload)</li>
<li><code>hamios_eibi.csv</code> — EIBI-planning (wordt gedownload)</li>
<li><code>HAMIOS_history.csv</code> — band-historiek (90 dagen)</li>
</ul>

<h4>Bestandsstatus</h4>
<p>Zie <b>Instellingen → Over → Bestanden</b> voor een live overzicht van alle bestanden.</p>
"""),

    ("🔧 Technisch", "Databronnen", """
<h3>Databronnen</h3>
<ul>
<li><b>NOAA SWPC</b> — solar-data, K-index, Bz, X-straling, stormprognose</li>
<li><b>DXWatch.com</b> — live DX-clusterdata</li>
<li><b>Blitzortung.org</b> — wereldwijd bliksemdetectienetwerk (WebSocket)</li>
<li><b>eibispace.de</b> — EIBI kortegolf-omroepplanning (Eike Bierwirth)</li>
<li><b>CelesTrak</b> — satelliet TLE-data (Dr. T.S. Kelso)</li>
<li><b>NASA Blue Marble</b> — equirectangulaire wereldkaart</li>
</ul>
<p>Alle externe verbindingen verlopen via standaard HTTPS/WebSocket.
Het programma verstuurt geen persoonlijke gegevens.</p>
"""),
]

# ── English help content ──────────────────────────────────────────────────────

_HELP_EN = [
    ("🚀 Getting started", "Welcome", """
<h3>Welcome to HF Propagation &amp; Atmosphere Monitor</h3>
<p>A real-time HF propagation and DX monitor for amateur radio operators.
Displays solar data, band conditions, live DX spots, satellite tracking,
lightning detection and more — all on one screen.</p>
<h4>First steps</h4>
<ol>
<li>Set your <b>callsign, QTH and antenna</b> via <b>⚙ Settings → Station</b>.</li>
<li>Enter your <b>Maidenhead locator</b> (e.g. JO22NC) or use lat/lon.</li>
<li>Adjust the <b>refresh interval</b> in the header (default 5 minutes).</li>
<li>Drag and resize <b>panels</b> as desired. Save layout via Settings → Layout.</li>
</ol>
"""),
    ("🚀 Getting started", "Panels and layout", """
<h3>Panels and layout</h3>
<p>The application has <b>15 freely moveable panels</b> on a virtual desktop:</p>
<ul>
<li>Drag a panel by its title bar.</li>
<li>Resize via the bottom-right corner grip (visible on hover).</li>
<li>Close a panel via ✕ in the title bar; reopen via <b>Settings → Panels</b>.</li>
<li>Save the current layout as default or as a named profile via <b>Settings → Layout</b>.</li>
</ul>
"""),
    ("🌍 Map", "World map and overlays", """
<h3>World map</h3>
<p>Equirectangular NASA map (auto-downloaded at first start). Overlays are
toggled via the <b>🗺 Overlays</b> button in the header.</p>
<h4>Available overlays</h4>
<ul>
<li><b>Day/night terminator</b> — shows where it is day or night.</li>
<li><b>Gray line</b> — twilight band of ~1000 km, ideal for DX.</li>
<li><b>Aurora oval</b> — based on current K-index (IGRF-2025 model).</li>
<li><b>Sun position</b> — with ray icon.</li>
<li><b>Moon position</b> — live phase icon and QTH horizon indicator (▲/▼).</li>
<li><b>Live DX spots</b> — colour-coded dots per band.</li>
<li><b>Satellite paths</b> — position, orbit path and footprint.</li>
<li><b>Lightning</b> — live discharges from Blitzortung.org.</li>
<li><b>Maidenhead grid</b> — 20°×10° fields with 2-letter labels.</li>
</ul>
"""),
    ("🌍 Map", "QTH and great-circle path", """
<h3>QTH marker</h3>
<p>Your QTH is shown as a blue cross on the map.
Set your location via Settings → Station (lat/lon or Maidenhead locator).</p>
<h4>Great-circle path</h4>
<p>Click any point on the map to draw the great-circle path from your QTH to that point,
showing distance (km), bearing and best band for that path.</p>
"""),
    ("☀ Solar &amp; Propagation", "Solar / Ionosphere panel", """
<h3>Solar / Ionosphere</h3>
<p>This panel shows current solar parameters that determine propagation.
Each row has <b>five columns</b>:</p>
<ol>
<li><b>Abbreviation</b> — e.g. SFI, SSN, K, A, Bz</li>
<li><b>Value</b> — current measurement (bold)</li>
<li><b>Unit</b> — e.g. SFU, nT, km/s</li>
<li><b>Indication</b> — colour-coded assessment</li>
<li><b>Full name</b> — expanded meaning of the abbreviation (italic)</li>
</ol>
<h4>Parameters</h4>
<ul>
<li><b>SFI</b> — <i>Solar Flux Index</i> — ionospheric ionisation. High = better HF conditions.</li>
<li><b>SSN</b> — <i>Sunspot Number</i> — correlates with SFI.</li>
<li><b>K</b> — <i>K-index</i> — geomagnetic activity (0–9). Low = stable. ≥5 = storm.</li>
<li><b>A</b> — <i>A-index</i> — daily average geomagnetic activity.</li>
<li><b>Bz</b> — <i>IMF Bz component</i> — negative = increased storm risk.</li>
<li><b>Vsw</b> — <i>Solar wind speed</i> (km/s).</li>
<li><b>Nsw</b> — <i>Solar wind density</i> (p/cm³).</li>
<li><b>Xray</b> — <i>X-ray class</i> (A/B/C/M/X). M and X = solar flare.</li>
</ul>
<p>Source: NOAA SWPC, updated every <i>N</i> minutes (set in header).</p>
"""),
    ("☀ Solar &amp; Propagation", "Band Reliability", """
<h3>HF Band Reliability</h3>
<p>Shows calculated reliability percentage for each HF band (160m–6m), plus current MUF and LUF.</p>
<h4>Colour coding</h4>
<ul>
<li><b>≥ 75%</b> — Excellent (green)</li>
<li><b>50–74%</b> — Good</li>
<li><b>25–49%</b> — Fair (orange)</li>
<li><b>< 25%</b> — Poor (red)</li>
<li><b>0%</b> — Closed (grey)</li>
</ul>
<h4>Click a bar</h4>
<p>Clicking a band opens a popup with frequencies (SSB/CW/FT8/WSPR) for direct CAT tuning.</p>
"""),
    ("☀ Solar &amp; Propagation", "Band Conditions and Schedule", """
<h3>Band Conditions</h3>
<p>Shows day/night condition per band (Excellent/Good/Fair/Poor/Closed).
Click a band name to tune your radio via CAT.</p>
<h3>Band Opening Schedule</h3>
<p>A 24-hour grid showing reliability per band per hour.
Green = open, orange = fair, red = poor, dark = closed.
Current local time is highlighted in amber.</p>
<p>Hover for details. Click to tune via CAT.</p>
"""),
    ("☀ Solar &amp; Propagation", "Propagation Advice", """
<h3>Propagation Advice</h3>
<p>AI-style analysis cards giving summarised advice per band.
Cards are updated on each solar refresh.</p>
<p>Changes in advice are also forwarded to the <b>Alerts panel</b>.</p>
"""),
    ("📈 History", "Band History and Solar History", """
<h3>Band History</h3>
<p>Shows calculated band reliability for all 11 HF bands over the past 24h (configurable).
Data is saved on each refresh in <b>HAMIOS_history.csv</b> (90 days retained).</p>
<p><b>Click a band in the legend</b> to toggle it on/off.</p>
<p>Use the <b>range selector</b> (top right) to switch between 24h / 7d / 30d / 1y.</p>
<h3>Solar History</h3>
<p>Shows SFI trend over time. K-index shown as a red line on the right axis.
Red background shading indicates elevated K-index periods.</p>
"""),
    ("📡 DX Spots", "Live DX Spots", """
<h3>Live DX Spots</h3>
<p>Real-time DX cluster data from <b>DXWatch.com</b>.
Table is updated on each solar refresh (default 5 minutes).</p>
<h4>Columns</h4>
<ul>
<li><b>UTC</b> — spot time</li>
<li><b>Band</b> — HF band (colour coded)</li>
<li><b>MHz</b> — exact frequency</li>
<li><b>DX</b> — DX callsign</li>
<li><b>Spotter</b> — who spotted it</li>
<li><b>Comment</b> — optional remark</li>
</ul>
<h4>Filters</h4>
<ul>
<li><b>Own continent</b> — show only spots by spotters on your continent.</li>
<li><b>Heatmap</b> — switch to a band activity chart over 24h.</li>
</ul>
<h4>CAT tuning</h4>
<p>Click any row to tune your radio directly to the spot frequency (SSB mode).</p>
"""),
    ("🛰 Satellites", "Satellite Tracking", """
<h3>Satellite Tracking</h3>
<p>Real-time position, orbit paths and footprints of HAM satellites, ISS, weather sats.
TLE data from <b>CelesTrak</b>.</p>
<h4>Usage</h4>
<ol>
<li>Click <b>🛰 Satellite</b> in the header.</li>
<li>Choose a category (All/Amateur/ISS/Weather/CubeSat).</li>
<li>Tick <b>Position</b> to show the satellite on the map.</li>
<li>Tick <b>Path</b> to show the orbit path (past + future configurable).</li>
<li>Tick <b>Footprint</b> to show the coverage area
  (yellow = QTH outside range, green = QTH in range).</li>
</ol>
<h4>Selected filter</h4>
<p>Tick <b>Selected</b> to show only your selected satellites.
Unticked = all satellites visible. Setting is remembered between sessions.</p>
<h4>TLE refresh</h4>
<p>Click <b>↻ Refresh TLE</b> for fresh orbital elements from CelesTrak.</p>
<h4>Orbit paths</h4>
<p>Past (default 1h) and future (default 1h) are independently configurable.
Value 0 = no path displayed.</p>
<h4>Satellite alert</h4>
<p>Via <b>Settings → Alerts → Satellite ping</b> you can enable a tone
when a selected satellite enters your QTH zone (ascending tone) or leaves it (descending tone).</p>
"""),
    ("⚡ Lightning", "Lightning detection and QRN", """
<h3>Lightning detection</h3>
<p>Live lightning discharges from the worldwide <b>Blitzortung.org</b> network.
Each discharge appears as an animated ring on the map that slowly fades.</p>
<h4>QRN advice</h4>
<p>The Lightning panel shows the QRN level based on the number of discharges
within <b>2000 km</b> of your QTH:</p>
<ul>
<li><b>No activity</b> — no discharges nearby</li>
<li><b>Low</b> — little QRN expected</li>
<li><b>Moderate</b> — some QRN on LF/MF/160m</li>
<li><b>High</b> — QRN on 160m/80m/40m</li>
<li><b>Severe</b> — strong QRN on all low bands</li>
</ul>
<h4>Discharge count</h4>
<p>The panel shows the <b>total discharges</b> within the fade duration period,
e.g. <code>127 /10m</code>.</p>
<h4>Nearest discharge</h4>
<p>The distance to the closest recent discharge is shown as <b>Nearest discharge</b>.</p>
<h4>Radius alerts</h4>
<p>Set a threshold distance in <b>Settings → Lightning</b> for:</p>
<ul>
<li><b>Header alert (red)</b> — ⚡ LIGHTNING X km appears centred in the header.</li>
<li><b>Acoustic alert (orange)</b> — Geiger-counter tick sound for discharges within the set radius.</li>
</ul>
<p>Both circles are visible on the map while lightning detection is enabled.</p>
"""),
    ("🕵 SpyStations", "SpyStations and numbers stations", """
<h3>SpyStations</h3>
<p>A database of known numbers stations, military signal stations, time signals
and weather services on HF.</p>
<h4>Usage</h4>
<ul>
<li>Search by name, country or frequency via the search bar.</li>
<li>Filter by Active/Inactive.</li>
<li>Click a column header to sort (↑/↓).</li>
<li>Click a station → frequency buttons appear bottom right.
  Click a frequency to tune your radio directly via CAT.</li>
</ul>
"""),
    ("📻 EIBI", "EIBI Shortwave Frequency List", """
<h3>EIBI Shortwave Frequency List</h3>
<p>Current shortwave broadcast schedule from <b>eibispace.de</b> (Eike Bierwirth).
Thousands of frequencies from international broadcasters worldwide.</p>
<h4>Usage</h4>
<ul>
<li>Click <b>⬇ Update list</b> to download the latest schedule.</li>
<li>Search by station, language, country or frequency.</li>
<li>Filter by band or enable <b>Active now</b> for the current time.</li>
<li>Click a row to tune your radio (AM mode via CAT).</li>
</ul>
"""),
    ("📡 FT8/Digital", "Digital mode frequencies", """
<h3>FT8 / Digital mode frequencies</h3>
<p>Standard dial frequencies for FT8, FT4, WSPR, JS8Call, MSK144, Q65, JT65 and JT9
on all bands (2200m through 23cm).</p>
<h4>Usage</h4>
<ul>
<li>Filter by band or mode.</li>
<li>Click a row to tune your radio (USB mode via CAT).</li>
</ul>
<h4>"Set USB mode" checkbox</h4>
<p>Enabled by default: mode is automatically set to USB when clicking.</p>
"""),
    ("📟 CAT", "CAT radio interface", """
<h3>CAT Radio Interface</h3>
<p>CAT (Computer Aided Transceiver) enables direct control of your radio
via the serial port. Supported radios:</p>
<ul>
<li><b>Yaesu FT-950/2000/DX/3000/5000</b> — FA command (8 digits), default 38400 baud</li>
<li><b>Yaesu FT-817/857/897</b> — FA command</li>
<li><b>Kenwood / Elecraft</b> — FA command (11 digits)</li>
<li><b>Icom CI-V</b> — binary BCD protocol</li>
</ul>
<h4>Configuration (Settings → CAT)</h4>
<ol>
<li>Click <b>⚙ Settings → CAT</b>.</li>
<li>Select the serial port (auto-scanned).</li>
<li>Choose your radio type or use a <b>Preset</b> (FT-950, FT-817, TS-590, K3/KX3).</li>
<li>Set baud rate, data bits, parity and stop bits (or use preset defaults).</li>
<li>Enable <b>CAT</b> and test with <b>Test connection</b>.</li>
</ol>
<h4>Serial terminal</h4>
<p>Open via <b>Settings → CAT → Open serial terminal</b>.
Shows connection status and lets you type CAT commands manually.
All serial parameters are configured exclusively in Settings → CAT.</p>
<h4>Frequency in header</h4>
<p>Once CAT is connected, the current VFO-A frequency appears in the header bar.
The radio is polled every 2 seconds.</p>
"""),
    ("🔔 Alerts", "Alerts panel", """
<h3>Alerts panel</h3>
<p>Collects all alerts in one place:</p>
<ul>
<li><b>K-storm</b> — when K-index ≥ threshold (configurable)</li>
<li><b>X-flare</b> — on M- or X-class solar flare</li>
<li><b>QRN level</b> — when local QRN level rises</li>
<li><b>Lightning nearby</b> — when lightning is within set radius</li>
<li><b>Satellite above QTH</b> — when a selected satellite enters your footprint</li>
<li><b>Propagation advice</b> — when band analysis changes</li>
</ul>
<h4>FIFO limit</h4>
<p>Set the maximum number of alerts to retain in Settings → Alerts (default 50).
Oldest alerts are automatically removed.</p>
"""),
    ("⚙ Settings", "Settings overview", """
<h3>Settings</h3>
<p>All configuration via <b>⚙ Settings</b> in the header.
All changes are <b>live</b> — visible immediately without restarting.</p>
<h4>Tabs</h4>
<ul>
<li><b>📡 Station</b> — callsign, QTH, mode, power, antenna</li>
<li><b>🪟 Panels</b> — show/hide panels</li>
<li><b>🗺 Map</b> — snap grid, overlay font sizes, icon sizes</li>
<li><b>⚡ Lightning</b> — fade duration, proximity alert, sound, animation scale</li>
<li><b>🔔 Alerts</b> — K-threshold, X-flare, band threshold, FIFO limit</li>
<li><b>📟 CAT</b> — serial port, radio type, presets, terminal</li>
<li><b>📐 Layout</b> — save/restore default, profiles, snap grid</li>
<li><b>📦 About</b> — version, dependencies, file status, language</li>
</ul>
<h4>Settings stored in</h4>
<p><code>hamios_config.json</code> in the application folder. All settings —
panel positions, CAT configuration, lightning settings and satellite data — are
in this single file.</p>
"""),
    ("⚙ Settings", "Layout profiles", """
<h3>Layout profiles</h3>
<p>Save multiple panel layouts as profiles (e.g. "Contest", "DX hunting", "Portable").</p>
<ol>
<li>Arrange panels as desired.</li>
<li>Go to <b>Settings → Layout → Profiles</b>.</li>
<li>Enter a name and click <b>Save as profile</b>.</li>
<li>Later: click <b>Load</b> next to the desired profile.</li>
</ol>
"""),
    ("🔧 Technical", "Requirements and files", """
<h3>Technical requirements</h3>
<ul>
<li><b>Windows 10/11</b> (64-bit)</li>
<li><b>PySide6</b> ≥ 6.4 (required)</li>
<li><b>pyserial</b> (optional, for CAT)</li>
<li><b>websocket-client</b> (optional, for lightning detection)</li>
</ul>
<h4>Auto-created files</h4>
<ul>
<li><code>HAMIOS5.exe</code> — executable</li>
<li><code>worldmap_eq.jpg</code> — world map (auto-downloaded)</li>
<li><code>worldmap_eq_hires.jpg</code> — 4K world map (auto-downloaded)</li>
<li><code>hamios_config.json</code> — all settings and window positions</li>
<li><code>hamios_spy_stations.json</code> — SpyStations database</li>
<li><code>hamios_tle.json</code> — satellite TLE (downloaded)</li>
<li><code>hamios_eibi.csv</code> — EIBI schedule (downloaded)</li>
<li><code>HAMIOS_history.csv</code> — band history (90 days)</li>
</ul>
"""),
    ("🔧 Technical", "Data sources", """
<h3>Data sources</h3>
<ul>
<li><b>NOAA SWPC</b> — solar data, K-index, Bz, X-ray, storm forecast</li>
<li><b>DXWatch.com</b> — live DX cluster data</li>
<li><b>Blitzortung.org</b> — worldwide lightning detection network (WebSocket)</li>
<li><b>eibispace.de</b> — EIBI shortwave schedule (Eike Bierwirth)</li>
<li><b>CelesTrak</b> — satellite TLE data (Dr. T.S. Kelso)</li>
<li><b>Wikimedia Commons</b> — NASA Blue Marble world map</li>
</ul>
<p>All external connections use standard HTTPS/WebSocket.
No personal data is transmitted.</p>
"""),
]

# ── Index bouwen ──────────────────────────────────────────────────────────────

def _build_index(items):
    import re
    idx = []
    for cat, title, html in items:
        plain = re.sub(r'<[^>]+>', ' ', html)
        idx.append((cat, title, html, (cat + " " + title + " " + plain).lower()))
    return idx

_INDEX_NL = _build_index(_HELP)
_INDEX_EN = _build_index(_HELP_EN)

def _get_index():
    return _INDEX_EN if get_language() == "en" else _INDEX_NL

# Legacy alias
_INDEX = _INDEX_NL


_QSS = f"""
QDialog   {{ background: {BG_PANEL}; }}
QListWidget {{
    background: {BG_SURFACE}; color: {TEXT_BODY};
    border: 1px solid {BORDER}; font-size: 8pt;
    outline: none;
}}
QListWidget::item {{ padding: 5px 8px; border-bottom: 1px solid {BG_ROOT}; }}
QListWidget::item:selected {{ background: {ACCENT}; color: {BG_PANEL}; }}
QListWidget::item:hover {{ background: #32373F; }}
QTextEdit {{
    background: {BG_SURFACE}; color: {TEXT_BODY};
    border: 1px solid {BORDER}; font-size: 9pt;
    padding: 8px;
}}
QLineEdit {{
    background: {BG_ROOT}; color: {TEXT_H1};
    border: 1px solid {BORDER}; padding: 6px 10px;
    border-radius: 3px; font-size: 9pt;
}}
QLineEdit:focus {{ border-color: {ACCENT}; }}
QLabel {{ color: {TEXT_DIM}; background: transparent; }}
QPushButton {{
    background: {BG_SURFACE}; color: {TEXT_H1};
    border: 1px solid {BORDER}; padding: 4px 14px; border-radius: 3px;
}}
QPushButton:hover {{ background: #32373F; border-color: {ACCENT}; }}
"""


class HelpDialog(QDialog):
    """Help dialog — searchable by category, bilingual."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle(tr("help.title"))
        self.setMinimumSize(820, 560)
        self.resize(920, 640)
        self.setStyleSheet(_QSS)
        self._build_ui()
        self._populate(None)
        restore_geom(self, "HelpDialog")
        language_changed.connect(self._on_language_changed)

    def _on_language_changed(self, _lang: str):
        self.setWindowTitle(tr("help.title"))
        self._title_lbl.setText(tr("help.header"))
        self._search.setPlaceholderText(tr("help.search"))
        self._close_btn.setText(tr("help.close"))
        self._populate(None)

    def _build_ui(self):
        v = QVBoxLayout(self)
        v.setContentsMargins(0, 0, 0, 0)
        v.setSpacing(0)

        # ── Header ───────────────────────────────────────────────────────────
        hdr = QFrame()
        hdr.setFixedHeight(52)
        hdr.setStyleSheet(f"background: #1A1D22; border-bottom: 2px solid {ACCENT};")
        hdr_lay = QHBoxLayout(hdr)
        hdr_lay.setContentsMargins(16, 0, 16, 0)

        self._title_lbl = QLabel(tr("help.header"))
        self._title_lbl.setFont(QFont("Segoe UI", 14, QFont.Bold))
        self._title_lbl.setStyleSheet(f"color: {ACCENT}; background: transparent;")
        hdr_lay.addWidget(self._title_lbl)
        hdr_lay.addStretch()

        self._search = QLineEdit()
        self._search.setPlaceholderText(tr("help.search"))
        self._search.setFixedWidth(260)
        self._search.setStyleSheet(
            f"background: #2A2D32; color: {TEXT_H1}; border: 1px solid {BORDER};"
            f" padding: 6px 10px; border-radius: 3px; font-size: 9pt;")
        self._search.textChanged.connect(self._on_search)
        hdr_lay.addWidget(self._search)
        v.addWidget(hdr)

        # ── Inhoud ────────────────────────────────────────────────────────────
        body = QWidget()
        body.setStyleSheet(f"background: {BG_PANEL};")
        body_lay = QVBoxLayout(body)
        body_lay.setContentsMargins(12, 12, 12, 12)
        body_lay.setSpacing(8)
        v.addWidget(body, 1)

        splitter = QSplitter(Qt.Horizontal)

        # Linker lijst
        self._list = QListWidget()
        self._list.setMinimumWidth(220)
        self._list.setMaximumWidth(300)
        self._list.currentRowChanged.connect(self._on_select)
        splitter.addWidget(self._list)

        # Rechter tekst
        self._text = QTextEdit()
        self._text.setReadOnly(True)
        self._text.document().setDefaultStyleSheet(f"""
            body  {{ color: {TEXT_BODY}; font-family: 'Segoe UI', sans-serif;
                     font-size: 9pt; margin: 4px; }}
            h3    {{ color: {ACCENT}; margin-bottom: 4px; }}
            h4    {{ color: {TEXT_H1}; margin-top: 8px; margin-bottom: 2px; }}
            ul, ol {{ margin-left: 16px; }}
            li    {{ margin-bottom: 2px; }}
            code  {{ background: {BG_ROOT}; padding: 1px 4px; border-radius: 2px;
                     font-family: Consolas; }}
            b     {{ color: {TEXT_H1}; }}
            p     {{ margin-top: 4px; margin-bottom: 4px; }}
        """)
        splitter.addWidget(self._text)
        splitter.setSizes([240, 660])
        body_lay.addWidget(splitter, 1)

        bot = QHBoxLayout()
        bot.addStretch()
        self._close_btn = QPushButton(tr("help.close"))
        self._close_btn.setObjectName("close")
        self._close_btn.clicked.connect(self.accept)
        bot.addWidget(self._close_btn)
        body_lay.addLayout(bot)

    def _populate(self, query: str | None):
        """Fill list based on search query (None = all)."""
        self._list.clear()
        self._entries = []
        idx = _get_index()

        if query:
            q = query.lower().strip()
            matches = [(cat, title, html) for cat, title, html, plain in idx
                       if q in plain]
        else:
            matches = [(cat, title, html) for cat, title, html, _ in idx]

        last_cat = None
        for cat, title, html in matches:
            if cat != last_cat:
                # Categorie-header
                cat_item = QListWidgetItem(cat)
                cat_item.setFlags(Qt.NoItemFlags)
                cat_item.setFont(QFont("Segoe UI", 8, QFont.Bold))
                cat_item.setForeground(QColor(ACCENT))
                cat_item.setBackground(QColor(BG_PANEL))
                self._list.addItem(cat_item)
                last_cat = cat
            item = QListWidgetItem("   " + title)
            item.setData(Qt.UserRole, html)
            item.setFont(QFont("Segoe UI", 8))
            self._list.addItem(item)
            self._entries.append(item)

        if self._entries:
            # Selecteer eerste echte item
            self._list.setCurrentItem(self._entries[0])

    def _on_search(self, text: str):
        self._populate(text if text.strip() else None)

    def _on_select(self, row: int):
        item = self._list.item(row)
        if item:
            html = item.data(Qt.UserRole)
            if html:
                self._text.setHtml(html)

    def done(self, result):
        save_geom(self, "HelpDialog")
        super().done(result)
