"""HAMIOS v5 — Help venster

Doorzoekbare help met categorieën die uitleggen wat het programma doet
en hoe het werkt.
"""

from PySide6.QtCore import Qt
from PySide6.QtGui import QFont, QColor
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
<p>Een realtime HF-propagatie- en atmosfeermonitor voor radioamateurs: gemeten
ionosfeer, propagatie-advies, zonnedata, live DX-, WSPR- en PSKReporter-spots,
satellieten, bliksem en meer — alles op één scherm.</p>
<h4>Eerste stappen</h4>
<ol>
<li>Stel uw <b>roepletters, QTH, mode, vermogen en antenne</b> in via <b>⚙ Instellingen → Station</b>
  — het propagatiemodel rekent met uw station.</li>
<li>Voer uw <b>Maidenhead-locator</b> in (bijv. JO22NC) of gebruik lat/lon.</li>
<li>Kies een indeling via <b>🪟 Panelen</b> (Kaart centraal, Operating, Analyse of Standaard).</li>
<li>Zet kaartlagen aan via <b>🗺 Overlays</b> — bij een nieuwe installatie staan ze allemaal uit.</li>
</ol>
"""),

    ("🚀 Aan de slag", "Panelen en indeling", """
<h3>Panelen en indeling</h3>
<p>De panelen vormen een <b>getegelde indeling</b>: ze sluiten altijd op elkaar aan, zonder
gaten of overlap, en schalen mee met het venster.</p>
<ul>
<li><b>Verslepen</b>: pak een paneel aan de titel (of tab) en laat het los op een ander paneel —
  rand = ernaast, midden = als tabblad, Ctrl + midden = van plaats wisselen.</li>
<li><b>Grootte</b>: sleep de scheidingslijnen tussen panelen.</li>
<li><b>Tabbladen</b>: passen zich aan de breedte aan; is het krap, dan tonen de niet-actieve tabs
  alleen hun icoon (naam in de tooltip). Sluiten via ✕ op de actieve tab.</li>
</ul>
<h4>🪟 Panelen-menu</h4>
<ul>
<li>Vier indelingen: <b>Kaart centraal</b>, <b>Operating</b>, <b>Analyse</b> en
  <b>Standaard</b> (de klassieke HAMIOS-indeling).</li>
<li><b>Indeling vastzetten</b> voorkomt per ongeluk verslepen.</li>
<li>Panelen tonen of verbergen met de vinkjes.</li>
</ul>
<p>Het menu (en het Overlays-menu) sluit vanzelf als u ergens anders klikt.</p>
"""),

    # ── Kaart ─────────────────────────────────────────────────────────────────
    ("🌍 Kaart", "Wereldkaart en overlays", """
<h3>Wereldkaart en overlays</h3>
<p>Kaartlagen zet u aan en uit via de <b>🗺 Overlays</b>-knop in de header.</p>
<ul>
<li><b>Dag/nacht-grens</b> en <b>grayline</b> — nauwkeurig volgens de NOAA-zonnecalculator
  (zie <i>Grayline, zon en maan</i>).</li>
<li><b>Aurora</b> — gemeten kans volgens NOAA OVATION, vloeiend groen → geel → rood.</li>
<li><b>Propagatiekaart</b> — kans dat de gekozen band het pad van uw QTH naar elk punt op aarde
  draagt. Kies de band naast het vinkje. Groen = goed, oranje = matig, rood = marginaal,
  geen kleur = dicht. Rond uw QTH ziet u de <i>dode zone</i>. Ververst elke 10 minuten.</li>
<li><b>HF-absorptie (NOAA D-RAP)</b> — waar HF door de D-laag wordt geabsorbeerd na een zonnevlam
  of protonen-event. Kleur = hoogste weggevreten frequentie (geel ~2, oranje ~6, rood ~12,
  magenta 20+ MHz). Bij een rustige zon blijft de laag leeg.</li>
<li><b>Zon en maan</b> — met tooltip (stand, op/ondergang, grayline-vensters, maanfase).</li>
<li><b>Live DX-spots</b> en <b>PSKReporter</b>-paden, gekleurd per band.</li>
<li><b>Satellieten</b> — positie, baanpad en footprint.</li>
<li><b>Bliksem</b> — live ontladingen van Blitzortung.org.</li>
<li><b>Maidenhead-raster</b> — met de muis ziet u de subsquares en de 6-tekens locator.</li>
<li><b>Callsign-landcodes</b> — muis op een land toont alle DXCC-prefixen.</li>
</ul>
<p>Lettergroottes: <b>Instellingen → Kaart</b>.</p>
"""),

    ("🌍 Kaart", "QTH en grootcirkelpad", """
<h3>QTH en grootcirkelpad</h3>
<p>Uw QTH is het blauwe kruis op de kaart (instellen via Instellingen → Station).
De cirkels geven de waarschuwingsstralen voor onweer aan.</p>
<p><b>Klik op de kaart</b> of op een <b>aanbeveling</b> in het propagatie-advies om het
grootcirkelpad (kortste pad) vanaf uw QTH te tekenen, met de afstand.</p>
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

    ("☀ Solar & Propagatie", "Banden nu", """
<h3>Banden nu</h3>
<p>Voor elke band (160m–6m) de <b>kans dat de band nu open is</b>, plus een oordeel voor
<b>overdag</b> en <b>'s nachts</b> en de <b>trend</b> (▲ gaat open, ▼ gaat dicht).</p>
<p>Bovenaan staan de actuele <b>MUF</b> en <b>LUF</b> op uw QTH, de marge van uw station (dB)
en of het dag of nacht is. Het percentage komt uit het propagatiemodel (zie
<i>Propagatiemodel</i>) en houdt rekening met uw mode, vermogen en antenne.</p>
<p>Klik op een band om de frequentie via CAT naar de radio te sturen.</p>
"""),

    ("☀ Solar & Propagatie", "Komende 24 uur", """
<h3>Komende 24 uur</h3>
<p>Een <b>rollende heatmap</b> vanaf nu: per band en per uur de verwachte kans
(groen = open, oranje = matig, rood = slecht, donker = dicht).</p>
<p>Daaronder de <b>MUF/LUF-curve</b> op dezelfde tijdas: waar de band tussen LUF en MUF valt, is hij
bruikbaar. Hover voor details.</p>
"""),

    ("☀ Solar & Propagatie", "Propagatie Advies", """
<h3>Propagatie-advies</h3>
<p>Het advies combineert het propagatiemodel met <b>wat er nu echt gehoord wordt</b>
(WSPR, DX-cluster, PSKReporter).</p>
<ul>
<li><b>Oordeel</b> met onderbouwing: gemeten MUF, bron-ionosonde, aantal waarnemingen.</li>
<li><b>Tot vijf aanbevelingen</b>: band → mode + frequentie → richting → tijdvenster.
  De <b>balk</b> is de effectieve kans (model + waarnemingen), het <b>witte streepje</b> het model alleen.
  👂 = open volgens waarnemingen, ook als het model pessimistisch is (bijv. TEP).</li>
<li><b>Gebeurtenissen</b>: NOAA R/S/G-schalen, zonnewind-schokgolf, zuidwaartse Bz, HF-absorptie,
  sporadic-E, meteorenzwermen, verwachting voor morgen.</li>
<li><b>Komende uren</b>: zonsopkomst/-ondergang (grayline), banden die open- of dichtgaan.</li>
</ul>
<p><b>Muis op een aanbeveling</b>: uitleg waarom de band open is (positie t.o.v. MUF en LUF,
controlepunten in daglicht of donker, waarnemingen per bron). <b>Klik</b>: pad op de kaart en,
als de radio verbonden is, afstemmen via CAT. Zie ook <b>ⓘ Hoe lees ik dit</b> in het paneel.</p>
"""),
    ("☀ Solar & Propagatie", "Propagatiemodel", """
<h3>Propagatiemodel</h3>
<p>Alle panelen en het advies gebruiken <b>één centraal model</b>:</p>
<ul>
<li><b>Gemeten ionosfeer</b>: de dichtstbijzijnde ionosonde (GIRO via prop.kc2g.com, elke 15 min)
  kalibreert het model; verder vooruit gaat het geleidelijk terug naar het model.</li>
<li><b>Gemeten absorptie</b>: NOAA D-RAP verhoogt de LUF waar HF na een zonnevlam wordt geabsorbeerd.</li>
<li><b>Dode zone</b>: op korte paden is de MUF lager (steilere invalshoek), dus een hoge band
  werkt pas vanaf een bepaalde afstand.</li>
<li><b>Dag/nacht</b> volgens de echte zonnestand op uw QTH; K-index uit de NOAA-schatting per minuut.</li>
<li><b>Uw station</b>: mode, vermogen en antenne bepalen de marge (dB) en daarmee de LUF.</li>
</ul>
"""),
    ("☀ Solar & Propagatie", "Ionosondes", """
<h3>Ionosondes</h3>
<p>Uw <b>gemeten ionosfeer</b>: de dichtstbijzijnde digisondes met hun actuele metingen.</p>
<ul>
<li><b>foF2</b> — kritieke frequentie van de F2-laag: tot ongeveer deze frequentie werkt
  <b>NVIS</b> (steil omhoog, 0–400 km).</li>
<li><b>MUF(3000)</b> — hoogste bruikbare frequentie over ~3000 km per sprong: bepaalt de hoogste
  <b>DX</b>-band.</li>
<li><b>foEs</b> — sporadic-E; boven ~5 MHz oranje: kans op korte sprongen op 10 m/6 m.</li>
<li><b>Gemeten t.o.v. model</b> — hoeveel de echte ionosfeer nu afwijkt; het model wordt hierop gekalibreerd.</li>
</ul>
<p>★ = het station waarmee het model nu gekalibreerd wordt. Metingen ouder dan 90 minuten
staan rood en worden niet gebruikt. In een smal paneel verdwijnen de kolommen foEs en leeftijd.</p>
"""),
    ("☀ Solar & Propagatie", "Grayline, zon en maan", """
<h3>Grayline, zon en maan</h3>
<p>De dag/nacht-grens en de grayline worden berekend met de <b>NOAA-zonnecalculator</b>
(inclusief tijdvereffening en refractie), dezelfde berekening als het propagatiemodel.</p>
<h4>Zon (tooltip)</h4>
<p>Stand vanaf uw QTH (hoogte en azimut), zonsopkomst en -ondergang in lokale tijd, daglengte en
de <b>grayline-vensters</b> (zon tussen −6° en +6°): de momenten met de beste kans op lange paden
op 160–40 m.</p>
<h4>Maan</h4>
<p>Het maanicoon toont de fase en de stand zoals u hem vanaf uw QTH ziet: de verlichte kant
wijst naar de zon (in Europa is een wassende maan rechts verlicht). De tooltip geeft de fasenaam,
het verlichte percentage en de hoogte boven of onder de horizon.</p>
<p>Iconengrootte: <b>Instellingen → Kaart</b>.</p>
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
    ("📡 WSPR Live", "WSPR Live-paneel", """
<h3>WSPR Live</h3>
<p>Echte WSPR-spots rond uw QTH via <b>wspr.live</b> (laatste 30 minuten, regio van ~300 km):</p>
<ul>
<li><b>→</b> uw regio is elders gehoord (zegt iets over uw uitgaande propagatie);</li>
<li><b>←</b> een ver station is in uw regio gehoord (inkomende propagatie).</li>
</ul>
<p>Kolommen: roepnaam, locator, frequentie, SNR, afstand, peiling en tijd — alle numeriek sorteerbaar.
De spots voeden ook het propagatie-advies. Lettergrootte: <b>Instellingen → Kaart</b>.</p>
"""),
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
<h3>Satelliettracking</h3>
<p>Positie, baanpaden en footprints van amateursatellieten, ISS, weersatellieten enz.
TLE-data van <b>SatNOGS</b> en <b>AMSAT</b>, met bescherming tegen downloadblokkades en een
waarschuwing als de data verouderd is. Baanmodel: Kepler + J2 (binnen ~10 km van SGP4 over een dag).</p>
<h4>Gebruik</h4>
<ol>
<li>Klik op <b>🛰 Satellite</b> in de header.</li>
<li>Kies een categorie (Alle/Amateur/CubeSat/ISS/Weer).</li>
<li>Vink <b>Positie</b> aan om de satelliet te volgen (ook voor het overkomstenpaneel).</li>
<li>Vink <b>Pad</b> aan voor het baanpad (terug/vooruit instelbaar) en <b>Footprint</b> voor het
  dekkingsgebied.</li>
</ol>
<p><b>↻ TLE vernieuwen</b> haalt verse baanelementen op.</p>
"""),
    ("🛰 Satellieten", "Satellietovergangen", """
<h3>Satellietovergangen</h3>
<p>De overkomsten van uw gevolgde satellieten in de <b>komende 24 uur</b>: opkomst (lokale tijd),
aftelling, duur, maximale elevatie en richting (opkomst → ondergang).</p>
<ul>
<li>Een overkomst die nu bezig is staat <b>groen</b>, met de tijd tot ondergang.</li>
<li>Max. elevatie: groen ≥ 45°, oranje ≥ 20°. Grijs = onder de meldingsdrempel.</li>
<li><b>Melding</b> (met geluid) vijf minuten vóór een overkomst — aan/uit en minimale elevatie in
  <b>Instellingen → Meldingen</b> (standaard 10°).</li>
</ul>
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

    ("🌐 Resources", "Online resources beheren", """
<h3>Online Resources Manager</h3>
<p>Beheer alle URL's van online resources die door HAMIOS worden gebruikt voor
real-time gegevens, satelliettracks, weerinformatie en meer.</p>

<h4>Beschikbare Resources (9 categorieën)</h4>
<ul>
<li><b>Solar &amp; Ionosphere</b> — NOAA SWPC (wind, magnetisme, Kp index), HamQSL (SFI)</li>
<li><b>Satellites</b> — SatNOGS DB en AMSAT (TLE-data voor amateurs, ISS, cubesats)</li>
<li><b>WSPR</b> — wspr.live (alle WSPRnet-spots, lage-vermogen bakens)</li>
<li><b>DX Spotting</b> — DXWatch (cluster spots), PSK Reporter (digitale modes)</li>
<li><b>Lightning</b> — Blitzortung (real-time bliksemdetectie)</li>
<li><b>Schedules</b> — EIBI Space (kortegolf uitzendschema's)</li>
<li><b>Map Data</b> — Wikimedia (NASA Blue Marble kaarten)</li>
</ul>

<h4>Resources aanpassen</h4>
<ol>
<li>Open <b>⚙ Instellingen → Resources</b>.</li>
<li>Per resource ziet u:
  <ul>
  <li>Huidge URL (bewerkbaar)</li>
  <li><b>Test</b>-knop — controleer connectiviteit en HTTP-status</li>
  <li><b>⚙</b>-knop — onderzoek alternatieve endpoints</li>
  </ul>
</li>
<li>Wijzigingen worden automatisch opgeslagen.</li>
</ol>

<h4>URL's testen</h4>
<p>Klik de <b>Test</b>-knop om directe connectiviteit te controleren.
Status toont HTTP-code en timeout-informatie.</p>

<h4>Onderzoek alternative endpoints</h4>
<p>Klik <b>⚙</b> om richtlijnen te krijgen voor het vinden van alternatieve
endpoints (bijv. spiegelservers, backup-API's).</p>

<h4>Naar standaard herstellen</h4>
<p>Klik <b>Naar standaard herstellen</b> om alle URL's naar HAMIOS defaults te resetten.</p>

<h4>Waarom Resources Manager?</h4>
<ul>
<li><b>Failover</b> — als een service down is, kunt u een spiegelserver instellen</li>
<li><b>Privacy</b> — andere API-endpoints gebruiken</li>
<li><b>Debugging</b> — langzame services vervangen door snellere testservers</li>
<li><b>Onderhoud</b> — API-endpoints die veranderen snel bijwerken</li>
</ul>
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
<li><b>Satellietovergang</b> — vijf minuten vóór een overkomst (drempel instelbaar)</li>
<li><b>Gebeurtenissen</b> uit het advies — straling, schokgolf, zuidwaartse Bz, sporadic-E</li>
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
<li><b>🗺 Kaart</b> — lettergroottes overlays, grootte zon- en maanicoon</li>
<li><b>⚡ Bliksem</b> — fade-duur, nabijheidsmelding, geluid, prestaties</li>
<li><b>🔔 Meldingen</b> — K-drempel, X-flare, band-drempel, FIFO-limiet</li>
<li><b>📟 CAT</b> — seriële poort, radiotype, presets, terminal</li>
<li><b>🌐 Resources</b> — online resources URL's, test en onderzoek endpoints</li>
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
<li><b>timezonefinder</b> (optioneel, voor lokale tijdzone op basis van QTH)</li>
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
<li><b>NOAA SWPC</b> — zonnedata, K-index, realtime zonnewind (Bz), X-straling, stormprognose,
  R/S/G-schalen, OVATION-aurora, D-RAP-absorptie, 27-daagse vooruitblik</li>
<li><b>prop.kc2g.com</b> — ionosondemetingen van het GIRO-netwerk (foF2, MUF, foEs)</li>
<li><b>wspr.live</b> — WSPR-spots (ClickHouse-database van alle WSPRnet-spots)</li>
<li><b>PSKReporter.info</b> — ontvangstrapporten van digitale modes</li>
<li><b>DXWatch.com</b> — live DX-clusterdata</li>
<li><b>Blitzortung.org</b> — wereldwijd bliksemdetectienetwerk (WebSocket)</li>
<li><b>eibispace.de</b> — EIBI kortegolf-omroepplanning (Eike Bierwirth)</li>
<li><b>SatNOGS DB</b> en <b>AMSAT</b> — satelliet-TLE-data</li>
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
<p>A real-time HF propagation and atmosphere monitor for radio amateurs: measured ionosphere,
propagation advice, solar data, live DX, WSPR and PSKReporter spots, satellites, lightning and
more — all on one screen.</p>
<h4>First steps</h4>
<ol>
<li>Set your <b>callsign, QTH, mode, power and antenna</b> in <b>⚙ Settings → Station</b>
  — the propagation model uses your station.</li>
<li>Enter your <b>Maidenhead locator</b> (e.g. JO22NC) or use lat/lon.</li>
<li>Pick a layout via <b>🪟 Panels</b> (Map centre, Operating, Analysis or Default).</li>
<li>Switch on map layers via <b>🗺 Overlays</b> — on a new installation they are all off.</li>
</ol>
"""),
    ("🚀 Getting started", "Panels and layout", """
<h3>Panels and layout</h3>
<p>The panels form a <b>tiled layout</b>: they always fit together, without gaps or overlap, and
scale with the window.</p>
<ul>
<li><b>Drag</b>: grab a panel by its title (or tab) and drop it onto another panel —
  edge = beside it, centre = as a tab, Ctrl + centre = swap places.</li>
<li><b>Size</b>: drag the dividers between panels.</li>
<li><b>Tabs</b> adapt to the available width; when it gets tight, inactive tabs show only their
  icon (name in the tooltip). Close via ✕ on the active tab.</li>
</ul>
<h4>🪟 Panels menu</h4>
<ul>
<li>Four layouts: <b>Map centre</b>, <b>Operating</b>, <b>Analysis</b> and <b>Default</b>
  (the classic HAMIOS layout).</li>
<li><b>Lock layout</b> prevents accidental dragging.</li>
<li>Show or hide panels with the checkboxes.</li>
</ul>
<p>The menu (and the Overlays menu) closes when you click anywhere else.</p>
"""),
    ("🌍 Map", "World map and overlays", """
<h3>World map and overlays</h3>
<p>Switch map layers on and off via the <b>🗺 Overlays</b> button in the header.</p>
<ul>
<li><b>Day/night terminator</b> and <b>grey line</b> — accurate, using the NOAA solar calculator
  (see <i>Grey line, sun and moon</i>).</li>
<li><b>Aurora</b> — measured probability from NOAA OVATION, smooth green → yellow → red.</li>
<li><b>Propagation map</b> — probability that the chosen band carries the path from your QTH to
  every point on Earth. Choose the band next to the checkbox. Green = good, orange = fair,
  red = marginal, no colour = closed. Around your QTH you see the <i>skip zone</i>.
  Refreshes every 10 minutes.</li>
<li><b>HF absorption (NOAA D-RAP)</b> — where HF is absorbed by the D layer after a flare or proton
  event. Colour = highest frequency being eaten (yellow ~2, orange ~6, red ~12, magenta 20+ MHz).
  With a quiet sun the layer stays empty.</li>
<li><b>Sun and moon</b> — with tooltips (position, rise/set, grey-line windows, moon phase).</li>
<li><b>Live DX spots</b> and <b>PSKReporter</b> paths, coloured per band.</li>
<li><b>Satellites</b> — position, orbit track and footprint.</li>
<li><b>Lightning</b> — live discharges from Blitzortung.org.</li>
<li><b>Maidenhead grid</b> — hover to see the sub-squares and the 6-character locator.</li>
<li><b>Callsign country codes</b> — hover a country for all its DXCC prefixes.</li>
</ul>
<p>Font sizes: <b>Settings → Map</b>.</p>
"""),
    ("🌍 Map", "QTH and great-circle path", """
<h3>QTH and great-circle path</h3>
<p>Your QTH is the blue cross on the map (set it in Settings → Station). The circles show the
lightning warning radii.</p>
<p><b>Click the map</b> or a <b>recommendation</b> in the propagation advice to draw the
great-circle (short) path from your QTH, with the distance.</p>
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
    ("☀ Solar &amp; Propagation", "Bands now", """
<h3>Bands now</h3>
<p>For each band (160m–6m) the <b>probability that the band is open now</b>, plus a rating for
<b>day</b> and <b>night</b> and the <b>trend</b> (▲ opening, ▼ closing).</p>
<p>At the top: the current <b>MUF</b> and <b>LUF</b> at your QTH, your station margin (dB) and whether
it is day or night. The percentage comes from the propagation model (see <i>Propagation model</i>)
and takes your mode, power and antenna into account.</p>
<p>Click a band to send the frequency to the radio via CAT.</p>
"""),
    ("☀ Solar &amp; Propagation", "Next 24 hours", """
<h3>Next 24 hours</h3>
<p>A <b>rolling heatmap</b> from now: the expected probability per band and per hour
(green = open, orange = fair, red = poor, dark = closed).</p>
<p>Below it the <b>MUF/LUF curve</b> on the same time axis: where a band lies between LUF and MUF,
it is usable. Hover for details.</p>
"""),
    ("☀ Solar &amp; Propagation", "Propagation Advice", """
<h3>Propagation advice</h3>
<p>The advice combines the propagation model with <b>what is actually being heard</b>
(WSPR, DX cluster, PSKReporter).</p>
<ul>
<li><b>Verdict</b> with evidence: measured MUF, source ionosonde, number of observations.</li>
<li><b>Up to five recommendations</b>: band → mode + frequency → direction → time window.
  The <b>bar</b> is the effective probability (model + observations), the <b>white tick</b> the model alone.
  👂 = open according to observations, even when the model is pessimistic (e.g. TEP).</li>
<li><b>Events</b>: NOAA R/S/G scales, solar-wind shock, southward Bz, HF absorption, sporadic-E,
  meteor showers, tomorrow's forecast.</li>
<li><b>Coming hours</b>: sunrise/sunset (grey line), bands opening or closing.</li>
</ul>
<p><b>Hover a recommendation</b>: why the band is open (position relative to MUF and LUF, control
points in daylight or darkness, observations per source). <b>Click</b>: path on the map and, if the
radio is connected, CAT tuning. See also <b>ⓘ How to read this</b> in the panel.</p>
"""),
    ("☀ Solar &amp; Propagation", "Propagation model", """
<h3>Propagation model</h3>
<p>All panels and the advice use <b>one central model</b>:</p>
<ul>
<li><b>Measured ionosphere</b>: the nearest ionosonde (GIRO via prop.kc2g.com, every 15 min)
  calibrates the model; further ahead it gradually returns to the model.</li>
<li><b>Measured absorption</b>: NOAA D-RAP raises the LUF where HF is absorbed after a flare.</li>
<li><b>Skip zone</b>: on short paths the MUF is lower (steeper angle), so a high band only works
  beyond a certain distance.</li>
<li><b>Day/night</b> from the real sun position at your QTH; K index from NOAA's per-minute estimate.</li>
<li><b>Your station</b>: mode, power and antenna set the margin (dB) and thus the LUF.</li>
</ul>
"""),
    ("☀ Solar &amp; Propagation", "Ionosondes", """
<h3>Ionosondes</h3>
<p>Your <b>measured ionosphere</b>: the nearest digisondes with their current measurements.</p>
<ul>
<li><b>foF2</b> — critical frequency of the F2 layer: <b>NVIS</b> (straight up, 0–400 km) works up
  to about this frequency.</li>
<li><b>MUF(3000)</b> — maximum usable frequency over ~3000 km per hop: sets the highest <b>DX</b> band.</li>
<li><b>foEs</b> — sporadic-E; orange above ~5 MHz: short-skip chances on 10 m/6 m.</li>
<li><b>Measured vs model</b> — how much the real ionosphere deviates now; the model is calibrated on this.</li>
</ul>
<p>★ = the station the model is currently calibrated on. Measurements older than 90 minutes are red
and not used. In a narrow panel the foEs and age columns are hidden.</p>
"""),
    ("☀ Solar &amp; Propagation", "Grey line, sun and moon", """
<h3>Grey line, sun and moon</h3>
<p>The day/night terminator and the grey line are calculated with the <b>NOAA solar calculator</b>
(including the equation of time and refraction) — the same calculation as the propagation model.</p>
<h4>Sun (tooltip)</h4>
<p>Position from your QTH (elevation and azimuth), sunrise and sunset in local time, day length and
the <b>grey-line windows</b> (sun between −6° and +6°): the times with the best long-path chances on
160–40 m.</p>
<h4>Moon</h4>
<p>The moon icon shows the phase and orientation as seen from your QTH: the lit side faces the sun
(in Europe a waxing moon is lit on the right). The tooltip gives the phase name, the illuminated
percentage and the elevation above or below the horizon.</p>
<p>Icon sizes: <b>Settings → Map</b>.</p>
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
    ("📡 WSPR Live", "WSPR Live Panel", """
<h3>WSPR Live</h3>
<p>Real WSPR spots around your QTH via <b>wspr.live</b> (last 30 minutes, region of ~300 km):</p>
<ul>
<li><b>→</b> your region was heard elsewhere (your outgoing propagation);</li>
<li><b>←</b> a distant station was heard in your region (incoming propagation).</li>
</ul>
<p>Columns: callsign, locator, frequency, SNR, distance, bearing and time — all sorted numerically.
The spots also feed the propagation advice. Font size: <b>Settings → Map</b>.</p>
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
<h3>Satellite tracking</h3>
<p>Position, orbit tracks and footprints of amateur satellites, the ISS, weather satellites etc.
TLE data from <b>SatNOGS</b> and <b>AMSAT</b>, with protection against download blocks and a warning
when the data is outdated. Orbit model: Kepler + J2 (within ~10 km of SGP4 over a day).</p>
<h4>Usage</h4>
<ol>
<li>Click <b>🛰 Satellite</b> in the header.</li>
<li>Choose a category (All/Amateur/CubeSat/ISS/Weather).</li>
<li>Tick <b>Position</b> to track the satellite (also used by the passes panel).</li>
<li>Tick <b>Path</b> for the orbit track (past/future adjustable) and <b>Footprint</b> for the
  coverage area.</li>
</ol>
<p><b>↻ Refresh TLE</b> fetches fresh orbital elements.</p>
"""),
    ("🛰 Satellites", "Satellite passes", """
<h3>Satellite passes</h3>
<p>The passes of your tracked satellites in the <b>next 24 hours</b>: rise time (local), countdown,
duration, maximum elevation and direction (rise → set).</p>
<ul>
<li>A pass in progress is <b>green</b>, with the time until it sets.</li>
<li>Max elevation: green ≥ 45°, orange ≥ 20°. Grey = below the alert threshold.</li>
<li><b>Alert</b> (with sound) five minutes before a pass — on/off and minimum elevation in
  <b>Settings → Alerts</b> (default 10°).</li>
</ul>
"""),
    ("⚡ Lightning", "Lightning detection and QRN", """
<h3>Lightning detection with dual zones</h3>
<p>Live lightning discharges from the worldwide <b>Blitzortung.org</b> network.
Each discharge appears as an animated ring on the map that slowly fades.</p>

<h4>QRN advice</h4>
<p>The Lightning panel shows the QRN level based on the number of discharges within <b>2000 km</b> of your QTH:</p>
<ul>
<li><b>No activity</b> — no discharges nearby</li>
<li><b>Low</b> — little QRN expected</li>
<li><b>Moderate</b> — some QRN on LF/MF/160m</li>
<li><b>High</b> — QRN on 160m/80m/40m</li>
<li><b>Severe</b> — strong QRN on all low bands</li>
</ul>

<h4>Discharge count</h4>
<p>The panel shows the <b>total discharges</b> within the fade duration period, e.g. <code>127 /10m</code>.</p>

<h4>Nearest discharge</h4>
<p>The distance to the closest recent discharge is shown as <b>Nearest discharge</b>.</p>

<h4>Alert Zone (inner circle) — High priority</h4>
<ul>
<li><b>Radius:</b> Configurable distance (km) around your QTH</li>
<li><b>Sound:</b> High-frequency beep when lightning strikes (5000 Hz, 10ms)</li>
<li><b>Status:</b> Enable/disable in Settings → Lightning → Alert Zone</li>
<li><b>Visual:</b> Red circle on map marking the alert zone</li>
</ul>

<h4>Warning Zone (outer circle) — Lower priority</h4>
<ul>
<li><b>Radius:</b> Configurable distance (km, larger than Alert Zone)</li>
<li><b>Sound:</b> Lower-frequency tick when lightning strikes (2800 Hz, 5ms)</li>
<li><b>Status:</b> Enable/disable in Settings → Lightning → Warning Zone</li>
<li><b>Visual:</b> Orange circle on map marking the warning zone</li>
</ul>

<h4>Customizable sound parameters</h4>
<p>For each zone:</p>
<ul>
<li><b>Pitch:</b> Frequency in Hz (300–8000)</li>
<li><b>Duration:</b> Length in milliseconds (1–100)</li>
<li>Live preview: adjust and hear the sound immediately</li>
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
    ("🌐 Resources", "Manage online resources", """
<h3>Online Resources Manager</h3>
<p>Manage all URLs of online resources used by HAMIOS for real-time data,
satellite tracking, weather information and more.</p>

<h4>Available Resources (7 categories)</h4>
<ul>
<li><b>Solar &amp; Ionosphere</b> — NOAA SWPC (wind, magnetic field, Kp index), HamQSL (SFI)</li>
<li><b>Satellites</b> — SatNOGS DB and AMSAT (TLE data for amateurs, ISS, cubesats)</li>
<li><b>WSPR</b> — wspr.live (all WSPRnet spots, low-power beacons)</li>
<li><b>DX Spotting</b> — DXWatch (cluster spots), PSK Reporter (digital modes)</li>
<li><b>Lightning</b> — Blitzortung (real-time lightning detection worldwide)</li>
<li><b>Schedules</b> — EIBI Space (shortwave broadcast schedules)</li>
<li><b>Map Data</b> — Wikimedia (NASA Blue Marble maps)</li>
</ul>

<h4>How to customize</h4>
<ol>
<li>Open <b>⚙ Settings → Resources</b>.</li>
<li>For each resource you'll see:
  <ul>
  <li>Resource name and description</li>
  <li>Current URL (editable text field)</li>
  </ul>
</li>
<li>Edit the URL directly in the text field.</li>
<li>Click <b>Save</b> to apply changes.</li>
<li>Click <b>Reset to Defaults</b> to restore all URLs to HAMIOS defaults.</li>
</ol>

<h4>Use cases</h4>
<ul>
<li><b>Failover</b> — if a service is down, configure a mirror server</li>
<li><b>Privacy</b> — use alternative API endpoints</li>
<li><b>Debugging</b> — test with alternative servers</li>
<li><b>Maintenance</b> — quickly update API endpoints that change</li>
</ul>
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
<li><b>Satellite pass</b> — five minutes before a pass (threshold adjustable)</li>
<li><b>Events</b> from the advice — radiation, shock, southward Bz, sporadic-E</li>
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

<h4>Settings tabs</h4>
<ul>
<li><b>📡 Station</b> — callsign, QTH, mode, power, antenna</li>
<li><b>🪟 Panels</b> — show/hide panels</li>
<li><b>🗺 Map</b> — overlay font sizes, sun and moon icon sizes</li>
<li><b>⚡ Lightning</b> — dual zones (Alert &amp; Warning), radius, pitch, duration, fade time</li>
<li><b>📡 WSPR Live</b> — panel font size (7–72 pt)</li>
<li><b>🔔 Alerts</b> — K-threshold, X-flare, band threshold, FIFO limit</li>
<li><b>📟 CAT</b> — serial port, radio type, presets, terminal</li>
<li><b>🌐 Resources</b> — online resource URLs, editable</li>
<li><b>📐 Layout</b> — save/restore default, profiles</li>
<li><b>📦 About</b> — version, dependencies, file status, language</li>
</ul>

<h4>v5.4 — New Settings</h4>
<ul>
<li><b>Lightning Alert Zone</b> — inner circle with high-priority sound</li>
<li><b>Lightning Warning Zone</b> — outer circle with lower-priority sound</li>
<li><b>Configurable pitch &amp; duration</b> — customize alert and warning sounds</li>
<li><b>WSPR panel font size</b> — scale the WSPR Live data table dynamically</li>
</ul>

<h4>Settings stored in</h4>
<p><code>hamios_config.json</code> in the application folder. All settings —
panel positions, CAT configuration, lightning settings, WSPR font size and satellite data — are
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
<li><b>timezonefinder</b> (optional, for local timezone based on QTH)</li>
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
<li><b>NOAA SWPC</b> — solar data, K index, real-time solar wind (Bz), X-ray, storm forecast,
  R/S/G scales, OVATION aurora, D-RAP absorption, 27-day outlook</li>
<li><b>prop.kc2g.com</b> — ionosonde measurements from the GIRO network (foF2, MUF, foEs)</li>
<li><b>wspr.live</b> — WSPR spots (ClickHouse database of all WSPRnet spots)</li>
<li><b>PSKReporter.info</b> — digital-mode reception reports</li>
<li><b>DXWatch.com</b> — live DX cluster data</li>
<li><b>Blitzortung.org</b> — worldwide lightning detection network (WebSocket)</li>
<li><b>eibispace.de</b> — EIBI shortwave schedule (Eike Bierwirth)</li>
<li><b>SatNOGS DB</b> and <b>AMSAT</b> — satellite TLE data</li>
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
