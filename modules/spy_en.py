"""
HAMIOS — Engelse teksten voor de SpyStations-lijst

De standaardlijst (spy_dialog._DEFAULTS, ook in config/hamios_spy_stations.json)
is Nederlands. Bij een Engelse interface worden naam, land, schema en info per
station hier opgezocht op de (Nederlandse) stationsnaam; zelf toegevoegde
stations blijven zoals ingevoerd (alleen het land wordt waar mogelijk vertaald).
"""

# naam (NL) → (naam EN, land EN, schema EN, info EN)
SPY_EN = {
    "UVB-76 (The Buzzer)": (
        "UVB-76 (The Buzzer)", "Russia", "Continuous 24/7.",
        "Best-known numbers station. Continuous buzzing tone (approx. 25 beeps/min), "
        "occasional Russian voice messages. GRU or FSB."),
    "M14a (The Pip)": (
        "M14a (The Pip)", "Russia", "Continuous 24/7.",
        "Short 'pip' tone every two seconds. Russian military. Similar to UVB-76."),
    "M03 (Russian Man)": (
        "M03 (Russian Man)", "Russia", "Irregular 04:00-08:00 UTC.",
        "Russian male voice with 5-digit groups. Probably FSB/SVR."),
    "G06 (Russian Lady)": (
        "G06 (Russian Lady)", "Russia", "Irregular, various times.",
        "Russian female voice reading numbers in Russian. Probably GRU."),
    "M98": (
        "M98", "Russia", "Irregular.",
        "Russian numbers station. Male voice with digit groups in Russian."),
    "S30 (The Alarm / Squeaky Wheel)": (
        "S30 (The Alarm / Squeaky Wheel)", "Russia", "Irregular.",
        "Squeaking/creaking sound as ID tone, followed by Russian numbers. Military origin."),
    "RDL (Russische marine)": (
        "RDL (Russian Navy)", "Russia", "Daily 06:00-10:00 UTC.",
        "Russian naval signal station. Morse navigation messages and orders for submarines."),
    "RJH69 / ENIGMA S06s": (
        "RJH69 / ENIGMA S06s", "Russia", "Irregular.",
        "Russian RTTY/digital transmissions with encrypted traffic. Military intelligence."),
    "V24 / Atencion": (
        "V24 / Atencion", "Cuba", "Tue/Thu/Sat 21:30 UTC.",
        "Cuban intelligence service (DGI). Spanish-language 5-digit groups. "
        "'Atención' as announcement."),
    "VC01 (Cuban Lady Counts)": (
        "VC01 (Cuban Lady Counts)", "Cuba", "Mon/Wed/Fri 01:00 UTC.",
        "Cuban female voice counting numbers in Spanish. DGI station for agents in the US."),
    "HM01": (
        "HM01", "North Korea", "Mon/Wed/Fri 00:00 UTC and 18:00 UTC.",
        "North Korean female voice with numbers, preceded by traditional music. "
        "Instructions for agents in South Korea."),
    "V07 (Cuban Numbers / Spaans)": (
        "V07 (Cuban Numbers / Spanish)", "Cuba", "Various times, mainly at night UTC.",
        "Spanish-language female voice with 5-digit numbers. Cuban DGI."),
    "4XZ (Israëlische marine)": (
        "4XZ (Israeli Navy)", "Israel", "Continuous 24/7.",
        "IDF Navy signal station. Morse navigation messages and security traffic."),
    "XSL (Chinese marine)": (
        "XSL (Chinese Navy)", "China", "Regular, various times.",
        "Chinese naval signal station. Morse and digital messages for naval units."),
    "NDT (Japanse marine)": (
        "NDT (Japanese Navy)", "Japan", "Several times a day.",
        "Japan Maritime Self-Defense Force signal station. Navigation warnings in Morse."),
    "NWC (Australische marine)": (
        "NWC (Australian Navy)", "Australia", "Regular.",
        "Royal Australian Navy VLF/HF signal station. Navigation warnings and defence traffic."),
    "GYA (Britse marine)": (
        "GYA (British Navy)", "United Kingdom", "Regular.",
        "UK Royal Navy NAVTEX signal station. Navigation messages and weather warnings."),
    "WWV (NIST tijdsignaal)": (
        "WWV (NIST time signal)", "USA", "Continuous 24/7.",
        "NIST time signal station Fort Collins, Colorado. UTC time ticks, weather, "
        "propagation bulletins."),
    "WWVH (NIST tijdsignaal Hawaï)": (
        "WWVH (NIST time signal Hawaii)", "USA", "Continuous 24/7.",
        "NIST time signal station Kekaha, Hawaii. Female voice instead of male voice "
        "to distinguish it from WWV."),
    "CHU (Canadees tijdsignaal)": (
        "CHU (Canadian time signal)", "Canada", "Continuous 24/7.",
        "National Research Council Canada time signal, Ottawa. UTC + French-language "
        "time announcements."),
    "DCF77 (Duits tijdsignaal)": (
        "DCF77 (German time signal)", "Germany", "Continuous 24/7.",
        "German LF time signal station Mainflingen. Encoded time code for clocks and receivers."),
    "MSF60 (UK tijdsignaal)": (
        "MSF60 (UK time signal)", "United Kingdom", "Continuous 24/7.",
        "NPL time signal Anthorn, Cumbria. Encoded time code for British clocks."),
    "RWM (Russisch tijdsignaal)": (
        "RWM (Russian time signal)", "Russia", "Continuous 24/7.",
        "VNIIFTRI time signal station Moscow. Morse time ticks and UTC announcements."),
    "BPM (Chinees tijdsignaal)": (
        "BPM (Chinese time signal)", "China", "Continuous 24/7.",
        "NTSC time signal station Xi'an. UTC + Chinese and English time announcements."),
    "DDH47 / DDK2 (DWD weerfax)": (
        "DDH47 / DDK2 (DWD weather fax)", "Germany", "Regular schedule.",
        "Deutscher Wetterdienst. Weather fax charts for the North Atlantic and European waters."),
    "GFA / GFE (UK Met Office weerfax)": (
        "GFA / GFE (UK Met Office weather fax)", "United Kingdom", "Regular schedule.",
        "UK Met Office Bracknell. Weather fax charts for the North Atlantic."),
    "JMH (Japan Meteorological Agency)": (
        "JMH (Japan Meteorological Agency)", "Japan", "Regular schedule.",
        "Japan Meteorological Agency weather fax. Charts for the Pacific and surroundings."),
    "M12a (Lincolnshire Poacher)": (
        "M12a (Lincolnshire Poacher)", "United Kingdom", "Stopped approx. 2008.",
        "English-language numbers station. Music intro 'Lincolnshire Poacher', 5-digit "
        "groups. GCHQ/MI6 Cyprus."),
    "SK01 (Cherry Ripe)": (
        "SK01 (Cherry Ripe)", "Australia", "Stopped approx. 2009.",
        "Australian numbers station. Music intro 'Cherry Ripe', 5-digit groups. ASIS."),
    "E10 (Swedish Rhapsody)": (
        "E10 (Swedish Rhapsody)", "Czechia/CIA", "Stopped approx. 2006.",
        "Well-known numbers station with a mechanical child's voice and a Swedish folk "
        "melody intro. Czech StB/CIA."),
    "E11 (Oblique)": (
        "E11 (Oblique)", "Czechia", "Stopped approx. 2007.",
        "Czech numbers station. Female voice with German-language 5-digit groups."),
    "E03 (Czech Lady)": (
        "E03 (Czech Lady)", "Czechia", "Stopped approx. 2000.",
        "Czech StB numbers station. Female voice with digit groups. Target: Germany/Austria."),
    "P03 (Attention!)": (
        "P03 (Attention!)", "Romania/Russia", "Stopped approx. 2002.",
        "Romanian/Russian numbers station. Typical 'Achtung/Attention' announcement, "
        "followed by numbers."),
    "S11a (Cynthia)": (
        "S11a (Cynthia)", "Romania", "Stopped approx. 1991.",
        "Romanian numbers station (Securitate). Female voice with 3-digit groups."),
    "F06 (Magnetic Fields)": (
        "F06 (Magnetic Fields)", "France", "Stopped approx. 2002.",
        "French numbers station (DGSE). 5-digit groups preceded by synthesizer music."),
    "E06 (Yosemite Sam)": (
        "E06 (Yosemite Sam)", "USA", "Stopped approx. 2004.",
        "American numbers station. Quote from the cartoon character Yosemite Sam as "
        "intro. CIA/NSA."),
    "V02a (The Counting Station)": (
        "V02a (The Counting Station)", "Cuba", "Stopped approx. 2008.",
        "Cuban numbers station. Female voice simply reading numbers in groups of five."),
    "HM08 (North Korean Lady)": (
        "HM08 (North Korean Lady)", "North Korea", "Stopped approx. 2000.",
        "North Korean numbers station. Female voice with digit groups in Korean."),
    "XPB (Chinese People's Liberation Army)": (
        "XPB (Chinese People's Liberation Army)", "China", "Stopped approx. 2015.",
        "Chinese PLA station. Morse with digit groups for military units."),
    "E07 / E07a (Spanish Lady)": (
        "E07 / E07a (Spanish Lady)", "Spain", "Stopped approx. 2011.",
        "Spanish-language numbers station. Female voice with 5-digit groups, intro melody."),
}

# Landnamen (voor zelf toegevoegde stations)
COUNTRY_EN = {
    "Rusland": "Russia", "Noord-Korea": "North Korea", "Israël": "Israel",
    "Australië": "Australia", "Verenigd Koninkrijk": "United Kingdom",
    "Duitsland": "Germany", "Tsjechië": "Czechia", "Roemenië": "Romania",
    "Frankrijk": "France", "Spanje": "Spain", "Tsjechië/CIA": "Czechia/CIA",
    "Roemenië/Rusland": "Romania/Russia", "Verenigde Staten": "United States",
    "Polen": "Poland", "Oekraïne": "Ukraine", "Italië": "Italy", "België": "Belgium",
    "Nederland": "Netherlands", "Zweden": "Sweden", "Noorwegen": "Norway",
}


def localize(stations: list) -> list:
    """Kopie van de stationslijst in de interfacetaal (het bestand blijft ongewijzigd)."""
    from .i18n import get_language
    if get_language() != "en":
        return stations
    out = []
    for s in stations:
        d = dict(s)
        en = SPY_EN.get(s.get("name", ""))
        if en:
            d["name"], d["country"], d["schedule"], d["info"] = en
        else:
            d["country"] = COUNTRY_EN.get(s.get("country", ""), s.get("country", ""))
        out.append(d)
    return out
