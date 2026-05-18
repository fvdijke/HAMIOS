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

# ── Help-inhoud per categorie ─────────────────────────────────────────────────
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

# Index voor zoeken
def _build_index():
    idx = []
    for cat, title, html in _HELP:
        # Strip HTML-tags voor zoektekst
        import re
        plain = re.sub(r'<[^>]+>', ' ', html)
        idx.append((cat, title, html, (cat + " " + title + " " + plain).lower()))
    return idx

_INDEX = _build_index()


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
    """HAMIOS5 Help — doorzoekbaar per categorie."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("HF Propagation & Atmosphere Monitor — Help")
        self.setMinimumSize(820, 560)
        self.resize(920, 640)
        self.setStyleSheet(_QSS)
        self._build_ui()
        self._populate(None)
        restore_geom(self, "HelpDialog")

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

        title = QLabel("📖  HF Propagation & Atmosphere Monitor — Help")
        title.setFont(QFont("Segoe UI", 14, QFont.Bold))
        title.setStyleSheet(f"color: {ACCENT}; background: transparent;")
        hdr_lay.addWidget(title)
        hdr_lay.addStretch()

        # Zoekbalk in header
        self._search = QLineEdit()
        self._search.setPlaceholderText("🔍  Zoeken in help…")
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

        # Sluitknop
        bot = QHBoxLayout()
        bot.addStretch()
        btn = QPushButton("Sluiten"); btn.setObjectName("close")
        btn.clicked.connect(self.accept)
        bot.addWidget(btn)
        body_lay.addLayout(bot)

    def _populate(self, query: str | None):
        """Vul de lijst op basis van zoekterm (None = alles)."""
        self._list.clear()
        self._entries = []

        if query:
            q = query.lower().strip()
            matches = [(cat, title, html) for cat, title, html, plain in _INDEX
                       if q in plain]
        else:
            matches = [(cat, title, html) for cat, title, html, _ in _INDEX]

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
