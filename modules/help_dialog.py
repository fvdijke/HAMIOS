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
ionosfeer, propagatie-advies en -voorspelling, zonnedata, live DX-, WSPR- en PSKReporter-spots,
waar uw eigen signaal gehoord wordt, satellieten met Doppler, bliksem en meer — alles op één scherm.</p>
<h4>Eerste stappen</h4>
<ol>
<li>Stel uw <b>roepletters, QTH, mode, vermogen en antenne</b> in via <b>⚙ Instellingen → Station</b>
  — het propagatiemodel rekent met uw station, en met uw roepletters ziet u in
  <i>Mijn signaal</i> waar u gehoord wordt.</li>
<li>Voer uw <b>Maidenhead-locator</b> in (bijv. JO21DN) of gebruik lat/lon.</li>
<li>Kies een indeling via <b>🪟 Panelen</b> (Kaart centraal, Operating, Analyse of Standaard) en
  richt hem naar wens in (zie <i>Panelen en indeling</i>).</li>
<li>Zet kaartlagen aan via <b>🗺 Overlays</b> — bij een nieuwe installatie staan ze allemaal uit.</li>
<li>Optioneel: verbind uw radio via <b>⚙ Instellingen → CAT</b> om met één klik af te stemmen.</li>
</ol>
<h4>Snel de weg vinden</h4>
<ul>
<li><b>Wanneer kan ik … werken?</b> — klik op de kaart: <i>Padvoorspelling</i> toont de komende 24 uur.</li>
<li><b>Wat is er nu open?</b> — <i>Banden nu</i>, <i>Propagatie Advies</i> en <i>Propagatie-overzicht</i>.</li>
<li><b>Waar word ik gehoord?</b> — <i>Mijn signaal</i>.</li>
<li><b>Een gezocht land in de lucht?</b> — <i>Watchlist</i>.</li>
</ul>
<p>Gebruik het zoekveld hierboven om in alle helpteksten te zoeken.</p>
"""),

    ("🚀 Aan de slag", "Panelen en indeling", """
<h3>Panelen en indeling</h3>
<p>Alle panelen samen vormen een <b>getegelde indeling</b>: ze sluiten altijd op elkaar aan,
zonder gaten of overlap, en schalen mee met het venster. U kunt de indeling volledig naar
eigen smaak inrichten.</p>

<h4>Grootte aanpassen</h4>
<p>Sleep de dunne <b>scheidingslijn</b> tussen twee panelen: beide buren passen zich tegelijk aan.</p>

<h4>Panelen verslepen, splitsen en samenvoegen</h4>
<p>Pak een paneel aan de <b>titelbalk</b> — of, in een groep met tabbladen, aan zijn
<b>tab</b> — en sleep het naar een ander paneel. Tijdens het slepen ziet u een kleine afbeelding
van het paneel en een <b>gekleurd vlak</b> dat laat zien waar het terechtkomt:</p>
<ul>
<li><b>Rand</b> van een paneel (links, rechts, boven of onder) → het paneel wordt <b>ernaast
  geplaatst</b>: de plek wordt <b>gesplitst</b> in twee helften.</li>
<li><b>Midden</b> van een paneel → het paneel komt er <b>als tabblad</b> bij; zo ontstaat
  een <b>tabgroep</b>.</li>
<li><b>Ctrl ingedrukt + midden</b> → de twee panelen <b>wisselen van plek</b>.</li>
<li>Een <b>tab uit een tabgroep</b> slepen naar de rand van diezelfde groep maakt hem
  <b>los</b>: de groep wordt gesplitst in het losse paneel en de rest.</li>
</ul>

<h4>Tabgroepen</h4>
<ul>
<li>Klik op een tab om dat paneel te tonen.</li>
<li>Is het krap, dan tonen de niet-actieve tabs <b>alleen hun icoon</b>; de volledige naam
  staat in de tooltip.</li>
<li>Blijft er in een groep maar één zichtbaar paneel over, dan ziet u gewoon een paneel met
  titelbalk; de tabs komen terug zodra er weer een tweede bij komt.</li>
</ul>

<h4>Panelen sluiten en terughalen</h4>
<ul>
<li>Sluit een paneel met <b>✕</b> in de titelbalk (of op de actieve tab). De buren vullen de
  vrijgekomen ruimte.</li>
<li>Haal het terug via <b>🪟 Panelen</b> (vinkje aan): het komt op <b>dezelfde plek en in dezelfde
  grootte</b> terug.</li>
<li>Nieuwe panelen na een update verschijnen als tabblad naast een verwant paneel, zonder uw
  indeling te verschuiven of het tabblad dat u open had te vervangen.</li>
</ul>

<h4>🪟 Panelen-menu</h4>
<ul>
<li>Vier kant-en-klare indelingen: <b>Kaart centraal</b> (dagelijks gebruik), <b>Operating</b>
  (kaart zo groot mogelijk), <b>Analyse</b> (grafieken groot) en <b>Standaard</b> (de klassieke
  HAMIOS-indeling). Op kleine schermen krijgt elke indeling een compacte variant met meer tabbladen.</li>
<li><b>Indeling vergrendelen</b>: geen slepen meer en vaste scheidingslijnen — handig als alles
  goed staat.</li>
<li>Panelen tonen of verbergen met de vinkjes.</li>
</ul>
<p>Het menu (en het Overlays-menu) sluit vanzelf als u ergens anders klikt. Uw indeling wordt bij
afsluiten bewaard; meerdere indelingen bewaart u als <i>Layout-profiel</i>.</p>
"""),

    ("🚀 Aan de slag", "Opstartscherm en updates", """
<h3>Opstartscherm en updates</h3>
<p>Bij het opstarten controleert HAMIOS maprechten, bestanden, afhankelijkheden en de online
bronnen, en kijkt het op GitHub of er een <b>nieuwere versie</b> is.</p>
<ul>
<li>Is er een update, dan verschijnt <b>UPDATE BESCHIKBAAR</b> — op het opstartscherm én als
  label in de header. Klik erop om de downloadpagina te openen; de muis erop toont het
  nieuwe versienummer.</li>
<li>Tijdens het gebruik wordt elke 12 uur opnieuw gekeken.</li>
<li><b>Instellingen → Over</b> toont uw versie en of er een nieuwere is.</li>
<li>Zonder internet blijft alles stil: er volgt geen foutmelding.</li>
</ul>
<p>Het opstartscherm kunt u uitzetten in <b>Instellingen → Over</b>.</p>
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
grootcirkelpad (kortste pad) vanaf uw QTH te tekenen, met de afstand. Hetzelfde punt wordt het doel
van de <b>Padvoorspelling</b> en verschijnt op de <b>Azimutale kaart</b>.
<b>Rechtsklik</b> zet de kaart terug op het hele wereldbeeld.</p>
<h4>Zoomen en pannen</h4>
<p>Scrollwiel = zoomen, slepen = pannen. Klik op een <b>DX-spot</b> of <b>PSKReporter</b>-stip voor
details (roepnaam, frequentie, band, spotter).</p>
"""),

    ("🌍 Kaart", "Azimutale kaart en rotor", """
<h3>Azimutale kaart</h3>
<p>Een wereldkaart <b>gecentreerd op uw QTH</b> (azimutaal-equidistant): elke rechte lijn vanuit het
midden is een grootcirkel. De <b>richting</b> op de kaart is dus precies de richting waarin u uw
antenne draait, de <b>afstand</b> tot het midden de echte afstand. Ringen per 5000 km; de rand is
het antipode van uw QTH (20 000 km).</p>
<ul>
<li><b>Muis</b> op de kaart: richting (kort en lang pad), afstand en positie.</li>
<li><b>Klik</b>: pad en padvoorspelling naar dat punt.</li>
<li>Blauwe stippen = actuele DX-spots.</li>
</ul>
<h4>Rotor</h4>
<p>Met een rotor ingesteld (<b>Instellingen → CAT → Rotor</b>) draait de antenne mee als u
klikt. Ondersteund: <b>Yaesu GS-232</b> (en compatibele interfaces, via een COM-poort) en
<b>Hamlib rotctld</b> (netwerk, standaard 127.0.0.1:4533). Het groene streepje toont de laatst
gevraagde richting.</p>
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
<p>Klik op een band om een frequentie te kiezen en via CAT naar de radio te sturen.</p>
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

    ("☀ Solar & Propagatie", "Propagatie-overzicht", """
<h3>Propagatie-overzicht</h3>
<p>Elf vaste kaartjes met een samenvatting van dit moment: beste banden, geomagnetische toestand,
zonactiviteit, zonnewind en Bz, zonnevlammen, dagdeel, mode/vermogen, absorptie op hoge breedte,
sporadic-E (seizoen volgt uw halfrond), <b>DX-routes vanaf uw QTH</b> (uit het propagatiemodel) en
een algeheel oordeel.</p>
<p>Een kaartje waarvan de inhoud verandert krijgt <b>5 minuten een knipperende stip</b>.
Het aantal kolommen past zich aan de paneelbreedte aan (1–3); in een laag paneel kunt u scrollen.</p>
"""),

    ("☀ Solar & Propagatie", "Padvoorspelling", """
<h3>Padvoorspelling — wanneer kan ik daar werken?</h3>
<p>De <b>kans per band voor de komende 24 uur</b> op het pad van uw QTH naar één plek, met
hetzelfde padmodel als de aanbevelingen.</p>
<ul>
<li><b>Doel kiezen</b>: klik op de kaart of de azimutale kaart, klik een aanbeveling of een
  melding in <i>Mijn signaal</i> — of typ een <b>locator</b> (JO21DN) of <b>roepnaam</b> (het land
  wordt via cty.dat gevonden) en klik <b>Voorspel</b>.</li>
<li>Bovenaan: afstand, richting (kort en lang pad).</li>
<li>Raster: banden × uren (lokale tijd, eerste kolom = dit uur); groen = goede kans, oranje = matig,
  rood = slecht, donker = dicht. Muis op een vak voor het percentage.</li>
<li>Onderaan de <b>beste vensters</b>: aaneengesloten uren met ≥ 50 % kans, hoogste kans eerst.</li>
</ul>
<p>Het model houdt rekening met de absorptie overdag bij zender én ontvanger: lage banden naar de
andere kant van de wereld gaan open als het aan beide kanten donker (of schemerig) is.</p>
"""),

    ("☀ Solar & Propagatie", "Model vs werkelijkheid", """
<h3>Model vs werkelijkheid</h3>
<p>Hoe vaak klopt het propagatiemodel met wat er écht gehoord wordt? Elke WSPR-spot rond uw QTH en
elk PSKReporter-pad met één kant binnen 500 km is een pad dat op dat moment open wás.</p>
<ul>
<li><b>Gehoord</b> — aantal waarnemingen (paden ≥ 1000 km).</li>
<li><b>Model eens</b> — deel daarvan waarvoor het model ≥ 50 % kans gaf (groen ≥ 70 %).</li>
<li><b>Gem. kans</b> — gemiddelde modelkans op de gehoorde paden.</li>
<li><b>Open, stil</b> — uren waarin het model de band open gaf terwijl er niets gehoord werd
  (alleen uren waarin op andere banden wél iets gehoord werd).</li>
</ul>
<p>Kies 1, 7 of 30 dagen. De cijfers lopen door over herstarts heen (30 dagen bewaard).
Let op: stilte kan ook betekenen dat er niemand actief was.</p>
"""),

    ("☀ Solar & Propagatie", "Stormprognose en 27 dagen", """
<h3>Stormprognose en 27-dagen-vooruitzicht</h3>
<p>De <b>3-daagse NOAA-prognose</b>: kans op <b>Actief</b> (Kp 4), <b>G1</b> (Kp 5), <b>G2</b> (Kp 6)
en <b>G3+</b> (Kp ≥ 7) per dag. NOAA geeft G3 t/m G5 als één kans; in de rij G4+ staat daarom "—".
Kleur: geel ≥ 10 %, oranje ≥ 25 %, rood ≥ 50 %.</p>
<p>Daaronder het <b>27-dagen-vooruitzicht</b>: per dag de verwachte maximale Kp (kleur) en de
zonneflux (balkje); vandaag is omkaderd. De tooltip noemt de rustigste dagen met de hoogste
flux — handig voor het plannen van contests en DX.</p>
"""),

    ("☀ Solar & Propagatie", "Kp, Bz en röntgen", """
<h3>Kp-, Bz- en röntgengrafieken</h3>
<ul>
<li><b>Kp 48u</b> — officiële planetaire K-index per 3 uur; de oranje lijn is de stormdrempel (Kp 5).
  Rechtsboven de actuele waarde.</li>
<li><b>Bz 24u</b> — de noord-zuidcomponent van het interplanetaire magneetveld. Langdurig
  <b>negatief (rood)</b> = verhoogde kans op geomagnetische storm.</li>
<li><b>Röntgen 24u</b> — GOES-zonneflux op logaritmische schaal (A–X). Rechtsboven de actuele
  klasse; M en X = zonnevlam (kans op radio-blackout aan de dagzijde).</li>
</ul>
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
<p>De berekende kans per HF-band in de tijd. Bij elke verversing wordt een punt opgeslagen in
<b>config/HAMIOS_history.csv</b> (90 dagen bewaard).</p>
<ul>
<li>Kies het tijdbereik rechtsboven: <b>24h, 7d, 30d of 1j</b>.</li>
<li><b>Klik op een band in de legenda</b> om die band aan of uit te zetten.</li>
<li>Gaten (HAMIOS stond uit) worden niet met een rechte lijn overbrugd.</li>
</ul>
<h3>Solar Verloop</h3>
<p>Het verloop van SFI en K-index in de tijd, met hetzelfde tijdbereik.</p>
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
<p>Real-time DX-clusterdata van <b>DXWatch.com</b>, elke 2 minuten ververst. De spots staan ook op
de kaart (lijn van spotter naar DX, gekleurd per band); het land van elke roepnaam komt uit de
DXCC-database (cty.dat).</p>
<h4>Kolommen</h4>
<ul>
<li><b>UTC</b> — tijdstip van de spot</li>
<li><b>Band</b> — HF-band (kleurgecodeerd)</li>
<li><b>MHz</b> — exacte frequentie</li>
<li><b>DX</b> — DX-roepletters</li>
<li><b>Spotter</b> — wie de spot maakte</li>
<li><b>Comment</b> — eventuele opmerking</li>
</ul>
<h4>Filteren</h4>
<ul>
<li><b>Eigen continent</b> — alleen spots van spotters op uw continent (geldt ook voor de kaart).</li>
<li><b>Heatmap</b> — bandactiviteit per uur over 24 uur.</li>
</ul>
<h4>CAT-afstemming</h4>
<p>Klik op een rij om uw radio op de spotfrequentie af te stemmen (SSB).</p>
"""),

    ("📡 DX Spots", "Mijn signaal", """
<h3>Mijn signaal — waar word ik gehoord?</h3>
<p>Waar uw eigen roepnaam het <b>afgelopen uur</b> ontvangen is, via <b>PSKReporter</b>
(FT8, FT4, CW-skimmers e.d.) en <b>WSPR</b> (uw WSPR-baken).</p>
<ul>
<li>Bovenaan per band: aantal ontvangers, <b>verste afstand</b> en <b>beste SNR</b>.</li>
<li>Daaronder elke melding: tijd, band, ontvanger, afstand, SNR en mode.</li>
<li><b>Klik</b> op een melding: het pad op de kaart (en in de padvoorspelling).</li>
</ul>
<p>Vereist uw roepletters in <b>Instellingen → Station</b>. Ververst elke 5 minuten (de afspraak
met PSKReporter). Dit is de directe controle of uw antenne en het advies kloppen.</p>
"""),

    ("📡 DX Spots", "Watchlist", """
<h3>Watchlist — gezochte stations en landen</h3>
<p>Zet stations of landen die u zoekt op de lijst; HAMIOS let op het DX-cluster.</p>
<ul>
<li><b>Roepnaam</b> (bijv. 3Y0J) — precies die roepnaam, ook als /P of /MM.</li>
<li><b>Prefix</b> (tot 4 tekens, bijv. VK9) — alle roepnamen die zo beginnen.</li>
<li><b>Land</b> (bijv. Bouvet) — deel van de DXCC-naam, minstens 4 letters.</li>
</ul>
<p>Typ een regel en klik <b>Toevoegen</b>; selecteer een regel en klik <b>Verwijderen</b>.</p>
<h4>Meldingen</h4>
<p>Wordt een gezocht station gespot, dan volgt een melding in het meldingen-paneel, een
<b>Windows-melding</b> (ook als HAMIOS geminimaliseerd is) en een geluid. Standaard
<b>alleen als de band op dat pad open is</b> (≥ 50 % volgens het model) — uitvinken voor alle spots.
Per roepnaam en band hooguit één melding per 30 minuten.</p>
<p>In de tabel: <b>klik</b> = pad op de kaart, <b>dubbelklik</b> = afstemmen via CAT.</p>
"""),

    ("📡 DX Spots", "DXCC-database (cty.dat)", """
<h3>DXCC-database (cty.dat)</h3>
<p>HAMIOS gebruikt de volledige DXCC-lijst van <b>country-files.com</b> (AD1C) om van elke
roepnaam het land, het continent, de CQ/ITU-zone en de positie te bepalen — ook bij lastige
gevallen als <i>EA8/DL1ABC</i> (Canarische Eilanden) of <i>R9…</i> (Aziatisch Rusland).</p>
<p>Gebruikt voor de DX-spots op de kaart, het eigen-continentfilter, de watchlist en de
padvoorspelling op roepnaam. Het bestand staat in <code>config/cty.dat</code> en wordt maandelijks
automatisch ververst; zonder internet blijft de bewaarde versie gelden.</p>
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

    ("🛰 Satellieten", "Doppler", """
<h3>Doppler</h3>
<p>Voor uw gevolgde satellieten de <b>zenders uit de SatNOGS-database</b> met de
<b>Doppler-gecorrigeerde frequenties van dit moment</b>:</p>
<ul>
<li><b>Downlink nu</b> — waar u moet luisteren (nadert de satelliet, dan hoger; verwijdert hij, lager).</li>
<li><b>Uplink nu</b> — waarop u moet zenden zodat de satelliet de nominale frequentie ontvangt.</li>
</ul>
<p>Kies de satelliet bovenaan; de regel toont elevatie, azimut en naderingssnelheid.
Selecteer een zender en klik <b>Afstemmen</b> om de downlink via CAT op de radio te zetten; met
<b>Volgen</b> blijft de radio tijdens de overkomst bijgestemd (elke 2 s, alleen bij &gt; 50 Hz
verschil).</p>
<p>Satellieten volgt u via <b>🛰 Satellite</b> (vinkje <b>Positie</b>).</p>
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

    ("📐 Antenne", "HAM Antenna Designer", """
<h3>HAM Antenna Designer</h3>
<p>Via de knop <b>📡 Antenna</b> in de header opent u de meegeleverde <b>HAM Antenna Designer</b>
(apart venster, volgt de taal van HAMIOS).</p>
<ul>
<li><b>20+ gedocumenteerde ontwerpen</b>: verticals, dipolen, EFHW, loops, Yagi, Moxon, quad,
  J-pole en SWL-ontvangstantennes — met onderbouwde formules en bouwadvies.</li>
<li><b>Draadlengtes</b> met de juiste correctie voor geïsoleerde draad; bandplan van IARU-regio 1 of 2.</li>
<li><b>SWR</b> (uit de complexe impedantie, achter de balun/unun), <b>SWR-sweep</b>, Smith-diagram en
  <b>stralingspatronen</b> boven echte bodem.</li>
<li><b>Aanpasnetwerken</b> met E12-waarden en <b>kabelverlies</b> voor 44 kabeltypes (inclusief extra
  verlies door SWR).</li>
<li>Antennetekeningen in 2D/3D, dag/nacht-thema, printbare SVG-export.</li>
</ul>
"""),

    # ── CAT ───────────────────────────────────────────────────────────────────
    ("📟 CAT", "CAT radio-interface", """
<h3>CAT Radio-interface</h3>
<p>CAT (Computer Aided Transceiver) laat HAMIOS uw radio afstemmen en de frequentie uitlezen.
Ondersteunde radiotypes:</p>
<ul>
<li><b>Yaesu FT-950/2000/DX/3000/5000</b> — FA-commando (8 cijfers), standaard 38400 baud</li>
<li><b>Yaesu FT-991/710/DX10/DX101</b> — FA-commando (9 cijfers)</li>
<li><b>Yaesu FT-817/857/897</b> — binair 5-byte-protocol (8N2)</li>
<li><b>Kenwood / Elecraft</b> — FA-commando (11 cijfers), modus via MD</li>
<li><b>Icom CI-V</b> — binair BCD-protocol, frequentie én modus (adres instelbaar)</li>
<li><b>Hamlib rigctld</b> — via het netwerk: vrijwel elke radio die Hamlib kent (200+)</li>
<li><b>flrig</b> — via het netwerk (XML-RPC)</li>
</ul>

<h4>Instellen (Instellingen → CAT)</h4>
<ol>
<li>Kies uw radiotype of gebruik een <b>Preset</b> (FT-950, FT-817, TS-590, K3/KX3).</li>
<li>Seriële radio: kies de poort (wordt gescand) en stel baudrate, databits, pariteit en
  stopbits in. <b>rigctld/flrig</b>: typ het adres in het poortveld, bijv.
  <code>127.0.0.1:4532</code> (rigctld) of <code>127.0.0.1:12345</code> (flrig).</li>
<li>Kies bij <b>Data-modus</b> welke radiomodus FT8/FT4/WSPR krijgt (USB of PKT-U/DATA-U).</li>
<li>Schakel <b>CAT inschakelen</b> in en test met <b>Verbinding testen</b>.</li>
</ol>

<h4>Seriële terminal</h4>
<p>Via <b>⚙ Instellingen → CAT → Seriële terminal openen</b> ziet u het verkeer met de radio en kunt
u zelf opdrachten typen (bij rigctld: rigctld-opdrachten zoals <code>f</code>).</p>

<h4>Frequentie in header</h4>
<p>Zodra CAT verbonden is, verschijnt de actuele frequentie van uw radio in de header
(elke 2 seconden gepeild).</p>

<h4>Rotor</h4>
<p>In hetzelfde tabblad stelt u een rotor in (Yaesu GS-232 via COM-poort, of Hamlib rotctld via
het netwerk) — zie <i>Azimutale kaart en rotor</i>.</p>
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
<li><b>Watchlist</b> — een gezocht station of land is gespot (ook als Windows-melding)</li>
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
<p>Alle configuratie via <b>⚙ Instellingen</b> in de header. Wijzigingen worden
<b>direct toegepast</b> — u ziet het resultaat zonder opnieuw op te starten (behalve een nieuw thema).</p>
<h4>Tabbladen</h4>
<ul>
<li><b>📡 Station</b> — roepletters, QTH/locator, mode, vermogen, antenne, dag/nacht</li>
<li><b>🗺 Kaart</b> — rasterstap, lettergroottes van de kaartlagen, grootte zon- en maanicoon</li>
<li><b>⚡ Bliksem</b> — aan/uit, fade-duur, nabijheidsmelding, geluid, prestaties</li>
<li><b>🔔 Meldingen</b> — K-drempel, X-flare, band-drempel, satellietovergangen, FIFO-limiet</li>
<li><b>📟 CAT</b> — radiotype (ook rigctld/flrig), poort of adres, presets, data-modus, rotor, terminal</li>
<li><b>🌐 Resources</b> — online resources URL's, test en onderzoek endpoints</li>
<li><b>📐 Layout</b> — thema (Nacht, Dag, Goed leesbaar, eigen thema via de thema-designer; actief na
  herstart), standaard layout opslaan/herstellen, profielen</li>
<li><b>📦 Over</b> — versie en update-status, afhankelijkheden, bestandsstatus, opstartscherm aan/uit</li>
</ul>
<p>Panelen tonen/verbergen en de indeling kiezen doet u via <b>🪟 Panelen</b> in de header.</p>
<h4>Instellingen worden bewaard in</h4>
<p><code>config/hamios_config.json</code> in de programmamap — inclusief vensterposities,
CAT- en rotorinstellingen, watchlist en blikseminstellingen.</p>
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
<li><b>Windows 10/11</b> (64-bit) — de EXE bevat alles wat nodig is</li>
<li>Vanuit de broncode: <b>Python 3.10+</b> met <b>PySide6</b> (vereist), en optioneel
  <b>pyserial</b> (CAT, GS-232-rotor), <b>websocket-client</b> (bliksem),
  <b>timezonefinder</b> (lokale tijdzone van de QTH) en <b>numpy</b> (snellere azimutale kaart)</li>
</ul>
<h4>Bestanden (map config/)</h4>
<ul>
<li><code>hamios_config.json</code> — alle instellingen en vensterposities</li>
<li><code>hamios_profiles.json</code> — layout-profielen</li>
<li><code>HAMIOS_history.csv</code> — band-historiek (90 dagen)</li>
<li><code>hamios_tle.json</code> — satelliet-TLE (handmatig vernieuwd)</li>
<li><code>hamios_transmitters.json</code> — satellietzenders voor Doppler (SatNOGS, 30 dagen)</li>
<li><code>cty.dat</code> — DXCC-database (maandelijks ververst)</li>
<li><code>hamios_verify.json</code> — model vs werkelijkheid (30 dagen)</li>
<li><code>hamios_eibi.csv</code> — EIBI-planning</li>
<li><code>hamios_spy_stations.json</code> — SpyStations-database</li>
<li><code>hamios_tz_cache.json</code> — tijdzone per QTH (sneller opstarten)</li>
</ul>
<p>Naast de EXE: <code>worldmap_eq.jpg</code> (wereldkaart; wordt zo nodig gedownload).</p>
<h4>Bestandsstatus</h4>
<p>Zie <b>Instellingen → Over → Bestanden</b> voor een live overzicht.</p>
"""),

    ("🔧 Technisch", "Databronnen", """
<h3>Databronnen</h3>
<ul>
<li><b>NOAA SWPC</b> — zonnedata, K-index, realtime zonnewind (Bz), X-straling, stormprognose,
  R/S/G-schalen, OVATION-aurora, D-RAP-absorptie, 27-daagse vooruitblik</li>
<li><b>HamQSL</b> — SFI en zonnevlekgetal</li>
<li><b>prop.kc2g.com</b> — ionosondemetingen van het GIRO-netwerk (foF2, MUF, foEs)</li>
<li><b>wspr.live</b> — WSPR-spots (alle WSPRnet-spots), ook voor <i>Mijn signaal</i></li>
<li><b>PSKReporter.info</b> — ontvangstrapporten van digitale modes, ook voor <i>Mijn signaal</i></li>
<li><b>DXWatch.com</b> — live DX-clusterdata</li>
<li><b>country-files.com</b> — DXCC-database cty.dat (AD1C)</li>
<li><b>Blitzortung.org</b> — wereldwijd bliksemdetectienetwerk (WebSocket)</li>
<li><b>eibispace.de</b> — EIBI kortegolf-omroepplanning (Eike Bierwirth)</li>
<li><b>SatNOGS DB</b> en <b>AMSAT</b> — satelliet-TLE's en satellietzenders (Doppler)</li>
<li><b>NASA Blue Marble</b> (Wikimedia) — equirectangulaire wereldkaart</li>
<li><b>GitHub</b> — versiecontrole (version.json)</li>
</ul>
<p>Alle externe verbindingen verlopen via standaard HTTPS/WebSocket. Het programma verstuurt geen
persoonlijke gegevens; alleen voor <i>Mijn signaal</i> wordt uw roepnaam als zoekterm naar
PSKReporter en wspr.live gestuurd.</p>
"""),
]

# ── English help content ──────────────────────────────────────────────────────

_HELP_EN = [
    ("🚀 Getting started", "Welcome", """
<h3>Welcome to HF Propagation &amp; Atmosphere Monitor</h3>
<p>A real-time HF propagation and atmosphere monitor for radio amateurs: measured ionosphere,
propagation advice and forecasts, solar data, live DX, WSPR and PSKReporter spots, where your own
signal is heard, satellites with Doppler, lightning and more — all on one screen.</p>
<h4>First steps</h4>
<ol>
<li>Set your <b>callsign, QTH, mode, power and antenna</b> in <b>⚙ Settings → Station</b>
  — the propagation model uses your station, and with your callsign <i>My signal</i> shows where
  you are heard.</li>
<li>Enter your <b>Maidenhead locator</b> (e.g. JO21DN) or use lat/lon.</li>
<li>Pick a layout via <b>🪟 Panels</b> (Map centre, Operating, Analysis or Default) and arrange it
  to your liking (see <i>Panels and layout</i>).</li>
<li>Turn map layers on via <b>🗺 Overlays</b> — on a new installation they are all off.</li>
<li>Optional: connect your radio in <b>⚙ Settings → CAT</b> to tune with one click.</li>
</ol>
<h4>Finding your way</h4>
<ul>
<li><b>When can I work …?</b> — click the map: <i>Path forecast</i> shows the next 24 hours.</li>
<li><b>What is open now?</b> — <i>Bands now</i>, <i>Propagation Advice</i> and <i>Propagation overview</i>.</li>
<li><b>Where am I heard?</b> — <i>My signal</i>.</li>
<li><b>A wanted country on the air?</b> — <i>Watchlist</i>.</li>
</ul>
<p>Use the search field above to search all help topics.</p>
"""),
    ("🚀 Getting started", "Panels and layout", """
<h3>Panels and layout</h3>
<p>All panels together form a <b>tiled layout</b>: they always fit together, without gaps or
overlap, and scale with the window. You can arrange the layout entirely to your own taste.</p>

<h4>Resizing</h4>
<p>Drag the thin <b>divider</b> between two panels: both neighbours adjust at the same time.</p>

<h4>Moving, splitting and merging panels</h4>
<p>Grab a panel by its <b>title bar</b> — or, in a tab group, by its <b>tab</b> — and drag it onto
another panel. While dragging you see a small image of the panel and a <b>coloured area</b> showing
where it will go:</p>
<ul>
<li><b>Edge</b> of a panel (left, right, top or bottom) → the panel is placed <b>next to it</b>:
  that spot is <b>split</b> into two halves.</li>
<li><b>Centre</b> of a panel → the panel is added <b>as a tab</b>, forming a <b>tab group</b>.</li>
<li><b>Ctrl held + centre</b> → the two panels <b>swap places</b>.</li>
<li>Dragging a <b>tab out of a tab group</b> to the edge of that same group <b>detaches</b> it:
  the group is split into the loose panel and the rest.</li>
</ul>

<h4>Tab groups</h4>
<ul>
<li>Click a tab to show that panel.</li>
<li>When space is tight, inactive tabs show <b>only their icon</b>; the full name is in the tooltip.</li>
<li>If only one visible panel remains in a group, you simply see a panel with a title bar; the tabs
  return as soon as a second one is shown again.</li>
</ul>

<h4>Closing and restoring panels</h4>
<ul>
<li>Close a panel with <b>✕</b> in its title bar (or on the active tab). Its neighbours fill the
  space.</li>
<li>Bring it back via <b>🪟 Panels</b> (tick it): it returns to <b>the same place and size</b>.</li>
<li>New panels after an update appear as a tab next to a related panel, without shifting your layout
  or replacing the tab you had open.</li>
</ul>

<h4>🪟 Panels menu</h4>
<ul>
<li>Four ready-made layouts: <b>Map centre</b> (everyday use), <b>Operating</b> (map as large as
  possible), <b>Analysis</b> (charts large) and <b>Default</b> (the classic HAMIOS layout). On small
  screens each layout gets a compact variant with more tabs.</li>
<li><b>Lock layout</b>: no more dragging and fixed dividers — handy once everything is in place.</li>
<li>Show or hide panels with the check boxes.</li>
</ul>
<p>The menu (and the Overlays menu) closes when you click elsewhere. Your layout is saved on exit;
keep several layouts as <i>Layout profiles</i>.</p>
"""),

    ("🚀 Getting started", "Start screen and updates", """
<h3>Start screen and updates</h3>
<p>At start-up HAMIOS checks folder access, files, dependencies and the online sources, and looks on
GitHub for a <b>newer version</b>.</p>
<ul>
<li>When there is an update, <b>UPDATE AVAILABLE</b> appears — on the start screen and as a badge
  in the header. Click it to open the download page; hovering shows the new version number.</li>
<li>While running, HAMIOS checks again every 12 hours.</li>
<li><b>Settings → About</b> shows your version and whether a newer one exists.</li>
<li>Without internet everything stays silent: no error message.</li>
</ul>
<p>The start screen can be turned off in <b>Settings → About</b>.</p>
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
<p>Your QTH is the blue cross on the map (set in Settings → Station). The circles show the
thunderstorm warning radii.</p>
<p><b>Click the map</b> or a <b>recommendation</b> in the propagation advice to draw the great-circle
path (short path) from your QTH, with the distance. The same point becomes the target of the
<b>Path forecast</b> and appears on the <b>Azimuthal map</b>. <b>Right-click</b> resets the map to
the whole world.</p>
<h4>Zooming and panning</h4>
<p>Scroll wheel = zoom, drag = pan. Click a <b>DX spot</b> or <b>PSKReporter</b> dot for details
(callsign, frequency, band, spotter).</p>
"""),

    ("🌍 Map", "Azimuthal map and rotator", """
<h3>Azimuthal map</h3>
<p>A world map <b>centred on your QTH</b> (azimuthal equidistant): every straight line from the
centre is a great circle. So the <b>direction</b> on the map is exactly the heading to turn your
antenna to, and the <b>distance</b> from the centre is the true distance. Rings every 5000 km; the
edge is the antipode of your QTH (20,000 km).</p>
<ul>
<li><b>Hover</b>: bearing (short and long path), distance and position.</li>
<li><b>Click</b>: path and path forecast to that point.</li>
<li>Blue dots = current DX spots.</li>
</ul>
<h4>Rotator</h4>
<p>With a rotator configured (<b>Settings → CAT → Rotator</b>) the antenna turns when you click.
Supported: <b>Yaesu GS-232</b> (and compatible interfaces, via a COM port) and <b>Hamlib rotctld</b>
(network, default 127.0.0.1:4533). The green stroke shows the last requested heading.</p>
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
<p>For each band (160m–6m) the <b>chance that the band is open now</b>, plus a rating for
<b>daytime</b> and <b>night</b> and the <b>trend</b> (▲ opening, ▼ closing).</p>
<p>At the top: the current <b>MUF</b> and <b>LUF</b> at your QTH, your station margin (dB) and
whether it is day or night. The percentage comes from the propagation model (see
<i>Propagation model</i>) and takes your mode, power and antenna into account.</p>
<p>Click a band to pick a frequency and send it to the radio via CAT.</p>
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

    ("☀ Solar &amp; Propagation", "Propagation overview", """
<h3>Propagation overview</h3>
<p>Eleven fixed cards summarising the moment: best bands, geomagnetic conditions, solar activity,
solar wind and Bz, flares, time of day, mode/power, high-latitude absorption, Sporadic-E (the season
follows your hemisphere), <b>DX routes from your QTH</b> (from the propagation model) and an overall
rating.</p>
<p>A card whose content changes shows a <b>blinking dot for 5 minutes</b>. The number of columns
follows the panel width (1–3); in a low panel you can scroll.</p>
"""),

    ("☀ Solar &amp; Propagation", "Path forecast", """
<h3>Path forecast — when can I work it?</h3>
<p>The <b>chance per band for the next 24 hours</b> on the path from your QTH to one place, with the
same path model as the recommendations.</p>
<ul>
<li><b>Choosing a target</b>: click the map or the azimuthal map, click a recommendation or a report
  in <i>My signal</i> — or type a <b>locator</b> (JO21DN) or <b>callsign</b> (its country is found via
  cty.dat) and click <b>Forecast</b>.</li>
<li>At the top: distance and bearing (short and long path).</li>
<li>Grid: bands × hours (local time, first column = this hour); green = good chance, orange = fair,
  red = poor, dark = closed. Hover a cell for the percentage.</li>
<li>At the bottom the <b>best windows</b>: consecutive hours with ≥ 50 % chance, highest first.</li>
</ul>
<p>The model accounts for daytime absorption at both the transmitter and the receiver: low bands to
the other side of the world open when it is dark (or twilight) at both ends.</p>
"""),

    ("☀ Solar &amp; Propagation", "Model vs reality", """
<h3>Model vs reality</h3>
<p>How often does the propagation model agree with what is really heard? Every WSPR spot around your
QTH and every PSKReporter path with one end within 500 km is a path that was open at that moment.</p>
<ul>
<li><b>Heard</b> — number of observations (paths ≥ 1000 km).</li>
<li><b>Model agrees</b> — share of them for which the model gave ≥ 50 % (green ≥ 70 %).</li>
<li><b>Avg. chance</b> — average model chance on the paths heard.</li>
<li><b>Open, silent</b> — hours in which the model rated the band open while nothing was heard
  (only hours in which other bands did have observations).</li>
</ul>
<p>Choose 1, 7 or 30 days. The figures continue across restarts (kept for 30 days). Note: silence can
also mean nobody was active.</p>
"""),

    ("☀ Solar &amp; Propagation", "Storm forecast and 27 days", """
<h3>Storm forecast and 27-day outlook</h3>
<p>The <b>3-day NOAA forecast</b>: chance of <b>Active</b> (Kp 4), <b>G1</b> (Kp 5), <b>G2</b> (Kp 6)
and <b>G3+</b> (Kp ≥ 7) per day. NOAA gives G3 to G5 as one probability, so the G4+ row shows "—".
Colour: yellow ≥ 10 %, orange ≥ 25 %, red ≥ 50 %.</p>
<p>Below it the <b>27-day outlook</b>: per day the expected maximum Kp (colour) and the solar flux
(bar); today is framed. The tooltip names the calmest days with the highest flux — handy for planning
contests and DX.</p>
"""),

    ("☀ Solar &amp; Propagation", "Kp, Bz and X-ray", """
<h3>Kp, Bz and X-ray charts</h3>
<ul>
<li><b>Kp 48h</b> — official planetary K-index per 3 hours; the orange line is the storm threshold
  (Kp 5). Current value top right.</li>
<li><b>Bz 24h</b> — the north-south component of the interplanetary magnetic field. Long periods of
  <b>negative (red)</b> = higher chance of a geomagnetic storm.</li>
<li><b>X-ray 24h</b> — GOES solar flux on a log scale (A–X). Current class top right; M and X = flare
  (risk of radio blackout on the day side).</li>
</ul>
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
<p>The calculated chance per HF band over time. A point is stored at every refresh in
<b>config/HAMIOS_history.csv</b> (kept for 90 days).</p>
<ul>
<li>Pick the time range top right: <b>24h, 7d, 30d or 1y</b>.</li>
<li><b>Click a band in the legend</b> to toggle it.</li>
<li>Gaps (HAMIOS was not running) are not bridged with a straight line.</li>
</ul>
<h3>Solar History</h3>
<p>SFI and K-index over time, with the same time range.</p>
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
<p>Real-time DX cluster data from <b>DXWatch.com</b>, refreshed every 2 minutes. The spots are also on
the map (line from spotter to DX, coloured by band); the country of every callsign comes from the
DXCC database (cty.dat).</p>
<h4>Columns</h4>
<ul>
<li><b>UTC</b> — time of the spot</li>
<li><b>Band</b> — HF band (colour coded)</li>
<li><b>MHz</b> — exact frequency</li>
<li><b>DX</b> — DX callsign</li>
<li><b>Spotter</b> — who made the spot</li>
<li><b>Comment</b> — any remark</li>
</ul>
<h4>Filtering</h4>
<ul>
<li><b>Own continent</b> — only spots from spotters on your continent (also on the map).</li>
<li><b>Heatmap</b> — band activity per hour over 24 hours.</li>
</ul>
<h4>CAT tuning</h4>
<p>Click a row to tune your radio to the spot frequency (SSB).</p>
"""),

    ("📡 DX Spots", "My signal", """
<h3>My signal — where am I heard?</h3>
<p>Where your own callsign was received in the <b>last hour</b>, from <b>PSKReporter</b>
(FT8, FT4, CW skimmers etc.) and <b>WSPR</b> (your WSPR beacon).</p>
<ul>
<li>At the top per band: number of receivers, <b>farthest distance</b> and <b>best SNR</b>.</li>
<li>Below: every report with time, band, receiver, distance, SNR and mode.</li>
<li><b>Click</b> a report: the path on the map (and in the path forecast).</li>
</ul>
<p>Requires your callsign in <b>Settings → Station</b>. Refreshes every 5 minutes (as agreed with
PSKReporter). This is the direct check whether your antenna and the advice are right.</p>
"""),

    ("📡 DX Spots", "Watchlist", """
<h3>Watchlist — wanted stations and countries</h3>
<p>Put stations or countries you are looking for on the list; HAMIOS watches the DX cluster.</p>
<ul>
<li><b>Callsign</b> (e.g. 3Y0J) — exactly that callsign, also as /P or /MM.</li>
<li><b>Prefix</b> (up to 4 characters, e.g. VK9) — all callsigns starting with it.</li>
<li><b>Country</b> (e.g. Bouvet) — part of the DXCC name, at least 4 letters.</li>
</ul>
<p>Type an entry and click <b>Add</b>; select an entry and click <b>Remove</b>.</p>
<h4>Alerts</h4>
<p>When a wanted station is spotted you get an alert in the Alerts panel, a <b>Windows
notification</b> (also when HAMIOS is minimised) and a sound. By default <b>only when the band is
open on that path</b> (≥ 50 % according to the model) — untick for all spots. At most one alert per
callsign and band per 30 minutes.</p>
<p>In the table: <b>click</b> = path on the map, <b>double-click</b> = tune via CAT.</p>
"""),

    ("📡 DX Spots", "DXCC database (cty.dat)", """
<h3>DXCC database (cty.dat)</h3>
<p>HAMIOS uses the full DXCC list from <b>country-files.com</b> (AD1C) to determine the country,
continent, CQ/ITU zone and position of every callsign — including tricky cases such as
<i>EA8/DL1ABC</i> (Canary Islands) or <i>R9…</i> (Asiatic Russia).</p>
<p>Used for the DX spots on the map, the own-continent filter, the watchlist and the path forecast by
callsign. The file is <code>config/cty.dat</code> and is refreshed automatically every month; without
internet the stored version stays in use.</p>
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

    ("🛰 Satellites", "Doppler", """
<h3>Doppler</h3>
<p>For your tracked satellites the <b>transmitters from the SatNOGS database</b> with the
<b>Doppler-corrected frequencies right now</b>:</p>
<ul>
<li><b>Downlink now</b> — where to listen (approaching satellite: higher; receding: lower).</li>
<li><b>Uplink now</b> — where to transmit so the satellite receives its nominal frequency.</li>
</ul>
<p>Choose the satellite at the top; the line shows elevation, azimuth and range rate. Select a
transmitter and click <b>Tune</b> to set the downlink on the radio via CAT; with <b>Follow</b> the
radio stays tuned during the pass (every 2 s, only when the change is &gt; 50 Hz).</p>
<p>Track satellites via <b>🛰 Satellite</b> (tick <b>Position</b>).</p>
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

    ("📐 Antenna", "HAM Antenna Designer", """
<h3>HAM Antenna Designer</h3>
<p>The <b>📡 Antenna</b> button in the header opens the bundled <b>HAM Antenna Designer</b>
(separate window, follows the HAMIOS language).</p>
<ul>
<li><b>20+ documented designs</b>: verticals, dipoles, EFHW, loops, Yagi, Moxon, quad, J-pole and SWL
  receiving antennas — with sound formulas and building advice.</li>
<li><b>Wire lengths</b> with the correct correction for insulated wire; band plan of IARU region 1 or 2.</li>
<li><b>SWR</b> (from the complex impedance, behind the balun/unun), <b>SWR sweep</b>, Smith chart and
  <b>radiation patterns</b> over real ground.</li>
<li><b>Matching networks</b> with E12 values and <b>cable loss</b> for 44 cable types (including the
  extra loss due to SWR).</li>
<li>Antenna drawings in 2D/3D, day/night theme, printable SVG export.</li>
</ul>
"""),
    ("📟 CAT", "CAT radio interface", """
<h3>CAT radio interface</h3>
<p>CAT (Computer Aided Transceiver) lets HAMIOS tune your radio and read its frequency.
Supported radio types:</p>
<ul>
<li><b>Yaesu FT-950/2000/DX/3000/5000</b> — FA command (8 digits), default 38400 baud</li>
<li><b>Yaesu FT-991/710/DX10/DX101</b> — FA command (9 digits)</li>
<li><b>Yaesu FT-817/857/897</b> — binary 5-byte protocol (8N2)</li>
<li><b>Kenwood / Elecraft</b> — FA command (11 digits), mode via MD</li>
<li><b>Icom CI-V</b> — binary BCD protocol, frequency and mode (address configurable)</li>
<li><b>Hamlib rigctld</b> — over the network: practically every radio Hamlib knows (200+)</li>
<li><b>flrig</b> — over the network (XML-RPC)</li>
</ul>
<h4>Setup (Settings → CAT)</h4>
<ol>
<li>Choose your radio type or use a <b>Preset</b> (FT-950, FT-817, TS-590, K3/KX3).</li>
<li>Serial radio: pick the port (scanned automatically) and set baud rate, data bits, parity and stop
  bits. <b>rigctld/flrig</b>: type the address in the port field, e.g. <code>127.0.0.1:4532</code>
  (rigctld) or <code>127.0.0.1:12345</code> (flrig).</li>
<li>Under <b>Data mode</b> choose the radio mode for FT8/FT4/WSPR (USB or PKT-U/DATA-U).</li>
<li>Tick <b>Enable CAT</b> and test with <b>Test connection</b>.</li>
</ol>
<h4>Serial terminal</h4>
<p>Via <b>⚙ Settings → CAT → Open serial terminal</b> you see the traffic with the radio and can type
commands yourself (with rigctld: rigctld commands such as <code>f</code>).</p>
<h4>Frequency in the header</h4>
<p>Once CAT is connected, the current radio frequency appears in the header (polled every 2 seconds).</p>
<h4>Rotator</h4>
<p>The same tab sets up a rotator (Yaesu GS-232 via COM port, or Hamlib rotctld over the network) —
see <i>Azimuthal map and rotator</i>.</p>
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
<p>Collects all warnings in one place:</p>
<ul>
<li><b>K storm</b> — when the K-index ≥ threshold (configurable)</li>
<li><b>X flare</b> — on an M- or X-class flare</li>
<li><b>QRN level</b> — when the local QRN level rises</li>
<li><b>Thunderstorm nearby</b> — lightning within the configured radius</li>
<li><b>Satellite over QTH</b> — a selected satellite has your QTH in its footprint</li>
<li><b>Satellite pass</b> — five minutes before a pass (threshold configurable)</li>
<li><b>Watchlist</b> — a wanted station or country was spotted (also as a Windows notification)</li>
<li><b>Events</b> from the advice — radiation, shock, southward Bz, Sporadic-E</li>
<li><b>Propagation advice</b> — when the band analysis changes</li>
</ul>
<h4>FIFO limit</h4>
<p>Set the maximum number of stored alerts in Settings → Alerts. The oldest are removed
automatically (default 50).</p>
<h4>Clear all</h4>
<p>Click <b>Clear all</b> to remove all active alerts.</p>
"""),
    ("⚙ Settings", "Settings overview", """
<h3>Settings</h3>
<p>All configuration via <b>⚙ Settings</b> in the header. Changes are <b>applied immediately</b> —
you see the result without restarting (except a new theme).</p>
<h4>Tabs</h4>
<ul>
<li><b>📡 Station</b> — callsign, QTH/locator, mode, power, antenna, day/night</li>
<li><b>🗺 Map</b> — grid step, font sizes of the map layers, size of the sun and moon icons</li>
<li><b>⚡ Lightning</b> — on/off, fade time, proximity alert, sound, performance</li>
<li><b>🔔 Alerts</b> — K threshold, X flare, band threshold, satellite passes, FIFO limit</li>
<li><b>📟 CAT</b> — radio type (also rigctld/flrig), port or address, presets, data mode, rotator,
  terminal</li>
<li><b>🌐 Resources</b> — online resource URLs, test and research endpoints</li>
<li><b>📐 Layout</b> — theme (Night, Day, High readability, your own via the theme designer; applied
  after a restart), save/restore default layout, profiles</li>
<li><b>📦 About</b> — version and update status, dependencies, file status, start screen on/off</li>
</ul>
<p>Showing/hiding panels and choosing a layout is done via <b>🪟 Panels</b> in the header.</p>
<h4>Settings are stored in</h4>
<p><code>config/hamios_config.json</code> in the program folder — including window positions, CAT and
rotator settings, watchlist and lightning settings.</p>
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
<li><b>Windows 10/11</b> (64-bit) — the EXE contains everything needed</li>
<li>From source: <b>Python 3.10+</b> with <b>PySide6</b> (required), and optionally <b>pyserial</b>
  (CAT, GS-232 rotator), <b>websocket-client</b> (lightning), <b>timezonefinder</b> (local time zone of
  the QTH) and <b>numpy</b> (faster azimuthal map)</li>
</ul>
<h4>Files (config/ folder)</h4>
<ul>
<li><code>hamios_config.json</code> — all settings and window positions</li>
<li><code>hamios_profiles.json</code> — layout profiles</li>
<li><code>HAMIOS_history.csv</code> — band history (90 days)</li>
<li><code>hamios_tle.json</code> — satellite TLEs (refreshed manually)</li>
<li><code>hamios_transmitters.json</code> — satellite transmitters for Doppler (SatNOGS, 30 days)</li>
<li><code>cty.dat</code> — DXCC database (refreshed monthly)</li>
<li><code>hamios_verify.json</code> — model vs reality (30 days)</li>
<li><code>hamios_eibi.csv</code> — EIBI schedule</li>
<li><code>hamios_spy_stations.json</code> — SpyStations database</li>
<li><code>hamios_tz_cache.json</code> — time zone per QTH (faster start-up)</li>
</ul>
<p>Next to the EXE: <code>worldmap_eq.jpg</code> (world map; downloaded if needed).</p>
<h4>File status</h4>
<p>See <b>Settings → About → Files</b> for a live overview.</p>
"""),
    ("🔧 Technical", "Data sources", """
<h3>Data sources</h3>
<ul>
<li><b>NOAA SWPC</b> — solar data, K-index, real-time solar wind (Bz), X-rays, storm forecast,
  R/S/G scales, OVATION aurora, D-RAP absorption, 27-day outlook</li>
<li><b>HamQSL</b> — SFI and sunspot number</li>
<li><b>prop.kc2g.com</b> — ionosonde measurements from the GIRO network (foF2, MUF, foEs)</li>
<li><b>wspr.live</b> — WSPR spots (all WSPRnet spots), also for <i>My signal</i></li>
<li><b>PSKReporter.info</b> — digital-mode reception reports, also for <i>My signal</i></li>
<li><b>DXWatch.com</b> — live DX cluster data</li>
<li><b>country-files.com</b> — DXCC database cty.dat (AD1C)</li>
<li><b>Blitzortung.org</b> — worldwide lightning detection network (WebSocket)</li>
<li><b>eibispace.de</b> — EIBI shortwave broadcast schedule (Eike Bierwirth)</li>
<li><b>SatNOGS DB</b> and <b>AMSAT</b> — satellite TLEs and satellite transmitters (Doppler)</li>
<li><b>NASA Blue Marble</b> (Wikimedia) — equirectangular world map</li>
<li><b>GitHub</b> — version check (version.json)</li>
</ul>
<p>All external connections use standard HTTPS/WebSocket. The program sends no personal data; only
for <i>My signal</i> is your callsign sent as a search term to PSKReporter and wspr.live.</p>
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
