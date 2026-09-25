"""
HAMIOS v5 — EIBI taal- en doelgebied-vertaling

Vertaalt EIBI-afkortingen naar volledige namen (Nederlands/Engels).
De originele EIBI-data wordt NIET gewijzigd; deze module levert alleen
vertalingen voor weergave als tooltip of in vertaalde kolommen.
"""

# ── Taalcodes ─────────────────────────────────────────────────────────────────
# Bron: EIBI documentatie + ISO 639
LANG = {
    # Meest voorkomende in EIBI
    "E":    "Engels",
    "M":    "Mandarijn (Chinees)",
    "S":    "Spaans",
    "R":    "Russisch",
    "F":    "Frans",
    "A":    "Arabisch",
    "D":    "Duits",
    "P":    "Portugees",
    "J":    "Japans",
    "K":    "Koreaans",
    "I":    "Italiaans",
    "NL":   "Nederlands",
    "NO":   "Noors",
    "SWE":  "Zweeds",
    "FI":   "Fins",
    "DA":   "Deens",
    # Aziatisch
    "VN":   "Vietnamees",
    "TB":   "Tibetaans",
    "HI":   "Hindi",
    "UR":   "Urdu",
    "CA":   "Kantonees",
    "PS":   "Pashto",
    "DR":   "Dari / Farsi",
    "MO":   "Mongools",
    "HA":   "Hausa",
    "AM":   "Amhaars",
    "UI":   "Oeigoers",
    "KH":   "Khmer",
    "TH":   "Thais",
    "BU":   "Birmees",
    "SI":   "Singalees",
    "TA":   "Tamil",
    "GU":   "Gujarati",
    "BE":   "Bengaals",
    "HK":   "Hakkien",
    "IN":   "Indonesisch / Maleis",
    "TU":   "Turks",
    "AZ":   "Azeri",
    "KZ":   "Kazachs",
    "UZ":   "Oezbeeks",
    "KG":   "Kirgizisch",
    "TK":   "Turkmeen",
    "GE":   "Georgisch",
    "AR":   "Armeens",
    "RO":   "Roemeens",
    "BR":   "Bulgaars",
    "BL":   "Wit-Russisch",
    "UK":   "Oekraïens",
    "LT":   "Litouws",
    "LV":   "Lets",
    "EE":   "Ests",
    "FS":   "Farsi / Perzisch",
    "BO":   "Tibetaans (Bod)",
    "HU":   "Hongaars",
    "PL":   "Pools",
    "CZ":   "Tsjechisch",
    "SK":   "Slowaaks",
    "SL":   "Sloveens",
    "HR":   "Kroatisch",
    "SR":   "Servisch",
    "BS":   "Bosnisch",
    "AL":   "Albanees",
    "MK":   "Macedonisch",
    "GR":   "Grieks",
    "TR":   "Turks",
    "HE":   "Hebreeuws",
    "KU":   "Koerdisch",
    # Afrikaans
    "SWA":  "Swahili",
    "ZU":   "Zoeloe",
    "SO":   "Somalisch",
    "OR":   "Oromo",
    "TI":   "Tigrinya",
    "IG":   "Igbo",
    "YO":   "Yoruba",
    "FR":   "Fulani",
    # Data/Morse
    "-CW":  "Morse (CW)",
    "-HF":  "HF digitaal",
    "-TS":  "RTTY / teletype",
    "-TY":  "TDM / tijdelijk",
    "-DM":  "Digitale modus",
    "-PI":  "PACTOR",
    # Speciale gevallen
    "F,E":  "Frans / Engels",
    "E,F":  "Engels / Frans",
    "E,S":  "Engels / Spaans",
    "M,C":  "Mandarijn / Kantonees",
}

# ── Doelgebied-codes ──────────────────────────────────────────────────────────
TARGET = {
    # Wereld / continenten
    "Eu":   "Europa",
    "WEu":  "West-Europa",
    "NEu":  "Noord-Europa",
    "EEu":  "Oost-Europa",
    "SEu":  "Zuid-Europa",
    "CEu":  "Centraal-Europa",
    "SEE":  "Zuidoost-Europa",
    "ME":   "Midden-Oosten",
    "NAm":  "Noord-Amerika",
    "ENA":  "Oost-Noord-Amerika",
    "WNA":  "West-Noord-Amerika",
    "Car":  "Caraïben",
    "CAm":  "Centraal-Amerika",
    "LAm":  "Latijns-Amerika",
    "SAm":  "Zuid-Amerika",
    "Af":   "Afrika",
    "NAf":  "Noord-Afrika",
    "WAf":  "West-Afrika",
    "EAf":  "Oost-Afrika",
    "CAf":  "Centraal-Afrika",
    "SAf":  "Zuid-Afrika",
    "FE":   "Verre Oosten",
    "CHN":  "China",
    "SEA":  "Zuidoost-Azië",
    "SAs":  "Zuid-Azië",
    "CAs":  "Centraal-Azië",
    "RUS":  "Rusland",
    "Sib":  "Siberië",
    "Oc":   "Oceanië",
    "WOc":  "West-Oceanië",
    "NOc":  "Noord-Oceanië",
    "NAO":  "Noord-Atlantische Oceaan",
    "INS":  "Indonesië",
    "KRE":  "Korea",
    "TWN":  "Taiwan",
    "IRN":  "Iran",
    "AFG":  "Afghanistan",
    "HNG":  "Hongarije",
    # Landen (ISO/ITU)
    "B":    "Brazilië",
    "AUS":  "Australië",
    "IND":  "India",
    "JPN":  "Japan",
    "USA":  "Verenigde Staten",
    "CAN":  "Canada",
    "GBR":  "Groot-Brittannië",
    "DEU":  "Duitsland",
    "FRA":  "Frankrijk",
    "ESP":  "Spanje",
    "NLD":  "Nederland",
    "PAK":  "Pakistan",
    "BGD":  "Bangladesh",
    "UKR":  "Oekraïne",
    "TUR":  "Turkije",
    "SAU":  "Saudi-Arabië",
    "NGA":  "Nigeria",
    "ETH":  "Ethiopië",
}

# ── ITU landcodes (kolom Land) ────────────────────────────────────────────────
ITU = {
    "AFG": "Afghanistan",       "ALB": "Albanië",         "ALG": "Algerije",
    "AND": "Andorra",           "ARS": "Saudi-Arabië",     "AUS": "Australië",
    "AUT": "Oostenrijk",        "AZE": "Azerbeidzjan",     "B":   "Brazilië",
    "BEL": "België",            "BEN": "Benin",            "BFA": "Burkina Faso",
    "BGD": "Bangladesh",        "BGR": "Bulgarije",        "BHR": "Bahrein",
    "BIH": "Bosnië-Herzegovina","BLR": "Wit-Rusland",      "BOL": "Bolivia",
    "BTN": "Bhutan",            "BUL": "Bulgarije",        "BUR": "Myanmar",
    "CAF": "Centraal-Afr. Rep.","CAN": "Canada",           "CHN": "China",
    "CHL": "Chili",             "CMR": "Kameroen",         "COD": "DR Congo",
    "COG": "Congo",             "COL": "Colombia",         "COM": "Comoren",
    "CRO": "Kroatië",           "CTI": "Ivoorkust",        "CUB": "Cuba",
    "CYP": "Cyprus",            "CZE": "Tsjechië",         "D":   "Duitsland",
    "DEN": "Denemarken",        "E":   "Spanje",            "EGY": "Egypte",
    "ERI": "Eritrea",           "ETH": "Ethiopië",         "F":   "Frankrijk",
    "FIN": "Finland",           "G":   "Groot-Brittannië", "GAB": "Gabon",
    "GEO": "Georgië",           "GHA": "Ghana",            "GNE": "Equatoriaal-Guinea",
    "GRC": "Griekenland",       "GTM": "Guatemala",        "GUF": "Frans-Guyana",
    "HNG": "Hongarije",         "HOL": "Nederland",        "HRV": "Kroatië",
    "HWA": "Hawaï",             "I":   "Italië",            "IND": "India",
    "INS": "Indonesië",         "IRL": "Ierland",          "IRN": "Iran",
    "IRQ": "Irak",              "ISL": "IJsland",          "ISR": "Israël",
    "J":   "Japan",             "JOR": "Jordanië",         "KAZ": "Kazachstan",
    "KEN": "Kenia",             "KGZ": "Kirgizistan",      "KOR": "Zuid-Korea",
    "KRE": "Noord-Korea",       "KWT": "Koeweit",          "LAO": "Laos",
    "LBN": "Libanon",           "LBY": "Libië",            "LTU": "Litouwen",
    "LVA": "Letland",           "MAR": "Marokko",          "MDG": "Madagaskar",
    "MEX": "Mexico",            "MLA": "Maleisië",         "MLI": "Mali",
    "MLT": "Malta",             "MNG": "Mongolië",         "MOZ": "Mozambique",
    "MRC": "Marokko",           "MRT": "Mauritanië",       "MWI": "Malawi",
    "MYA": "Myanmar",           "NCL": "Nieuw-Caledonië",  "NGR": "Niger",
    "NIG": "Nigeria",           "NOR": "Noorwegen",        "NZL": "Nieuw-Zeeland",
    "OMA": "Oman",              "PAK": "Pakistan",         "PHL": "Filipijnen",
    "PLW": "Palau",             "PNG": "Papoea-Nieuw-Guinea",
    "POL": "Polen",             "POR": "Portugal",         "PRU": "Peru",
    "QAT": "Qatar",             "REU": "Réunion",          "ROU": "Roemenië",
    "RRW": "Rwanda",            "RUS": "Rusland",          "S":   "Zweden",
    "SDN": "Soedan",            "SEN": "Senegal",          "SNG": "Singapore",
    "SOM": "Somalië",           "SUI": "Zwitserland",      "SVK": "Slowakije",
    "SVN": "Slovenië",          "SWZ": "Swaziland",        "SYR": "Syrië",
    "TCD": "Tsjaad",            "TGO": "Togo",             "THA": "Thailand",
    "TJK": "Tadzjikistan",      "TKM": "Turkmenistan",     "TZA": "Tanzania",
    "UAE": "Ver. Arabische Emir.",
    "UGA": "Oeganda",           "UKR": "Oekraïne",         "URG": "Uruguay",
    "USA": "Verenigde Staten",  "UZB": "Oezbekistan",      "VTN": "Vietnam",
    "YEM": "Jemen",             "ZMB": "Zambia",           "ZWE": "Zimbabwe",
    # Speciale uitzenders
    "AGL": "Angola",            "SRL": "Sierra Leone",     "CLM": "Colombia",
    "NMB": "Namibië",           "MDR": "Madagaskar",       "TWN": "Taiwan",
    "VRC": "China (volksrep.)", "HON": "Honduras",         "CLN": "Sri Lanka",
}


# ── Engelse namen (zelfde codes) ──────────────────────────────────────────────
LANG_EN = {
    "E": "English", "M": "Mandarin (Chinese)", "S": "Spanish", "R": "Russian",
    "F": "French", "A": "Arabic", "D": "German", "P": "Portuguese", "J": "Japanese",
    "K": "Korean", "I": "Italian", "NL": "Dutch", "NO": "Norwegian", "SWE": "Swedish",
    "FI": "Finnish", "DA": "Danish",
    "VN": "Vietnamese", "TB": "Tibetan", "HI": "Hindi", "UR": "Urdu", "CA": "Cantonese",
    "PS": "Pashto", "DR": "Dari / Farsi", "MO": "Mongolian", "HA": "Hausa", "AM": "Amharic",
    "UI": "Uyghur", "KH": "Khmer", "TH": "Thai", "BU": "Burmese", "SI": "Sinhala",
    "TA": "Tamil", "GU": "Gujarati", "BE": "Bengali", "HK": "Hokkien",
    "IN": "Indonesian / Malay", "TU": "Turkish", "AZ": "Azeri", "KZ": "Kazakh",
    "UZ": "Uzbek", "KG": "Kyrgyz", "TK": "Turkmen", "GE": "Georgian", "AR": "Armenian",
    "RO": "Romanian", "BR": "Bulgarian", "BL": "Belarusian", "UK": "Ukrainian",
    "LT": "Lithuanian", "LV": "Latvian", "EE": "Estonian", "FS": "Farsi / Persian",
    "BO": "Tibetan (Bod)", "HU": "Hungarian", "PL": "Polish", "CZ": "Czech",
    "SK": "Slovak", "SL": "Slovenian", "HR": "Croatian", "SR": "Serbian",
    "BS": "Bosnian", "AL": "Albanian", "MK": "Macedonian", "GR": "Greek",
    "TR": "Turkish", "HE": "Hebrew", "KU": "Kurdish",
    "SWA": "Swahili", "ZU": "Zulu", "SO": "Somali", "OR": "Oromo", "TI": "Tigrinya",
    "IG": "Igbo", "YO": "Yoruba", "FR": "Fulani",
    "-CW": "Morse (CW)", "-HF": "HF digital", "-TS": "RTTY / teletype",
    "-TY": "TDM / temporary", "-DM": "Digital mode", "-PI": "PACTOR",
    "F,E": "French / English", "E,F": "English / French", "E,S": "English / Spanish",
    "M,C": "Mandarin / Cantonese",
}

TARGET_EN = {
    "Eu": "Europe", "WEu": "Western Europe", "NEu": "Northern Europe",
    "EEu": "Eastern Europe", "SEu": "Southern Europe", "CEu": "Central Europe",
    "SEE": "South-East Europe", "ME": "Middle East", "NAm": "North America",
    "ENA": "Eastern North America", "WNA": "Western North America", "Car": "Caribbean",
    "CAm": "Central America", "LAm": "Latin America", "SAm": "South America",
    "Af": "Africa", "NAf": "North Africa", "WAf": "West Africa", "EAf": "East Africa",
    "CAf": "Central Africa", "SAf": "Southern Africa", "FE": "Far East", "CHN": "China",
    "SEA": "South-East Asia", "SAs": "South Asia", "CAs": "Central Asia",
    "RUS": "Russia", "Sib": "Siberia", "Oc": "Oceania", "WOc": "Western Oceania",
    "NOc": "Northern Oceania", "NAO": "North Atlantic Ocean", "INS": "Indonesia",
    "KRE": "Korea", "TWN": "Taiwan", "IRN": "Iran", "AFG": "Afghanistan",
    "HNG": "Hungary",
    "B": "Brazil", "AUS": "Australia", "IND": "India", "JPN": "Japan",
    "USA": "United States", "CAN": "Canada", "GBR": "United Kingdom", "DEU": "Germany",
    "FRA": "France", "ESP": "Spain", "NLD": "Netherlands", "PAK": "Pakistan",
    "BGD": "Bangladesh", "UKR": "Ukraine", "TUR": "Turkey", "SAU": "Saudi Arabia",
    "NGA": "Nigeria", "ETH": "Ethiopia",
}

ITU_EN = {
    "AFG": "Afghanistan", "ALB": "Albania", "ALG": "Algeria", "AND": "Andorra",
    "ARS": "Saudi Arabia", "AUS": "Australia", "AUT": "Austria", "AZE": "Azerbaijan",
    "B": "Brazil", "BEL": "Belgium", "BEN": "Benin", "BFA": "Burkina Faso",
    "BGD": "Bangladesh", "BGR": "Bulgaria", "BHR": "Bahrain",
    "BIH": "Bosnia and Herzegovina", "BLR": "Belarus", "BOL": "Bolivia", "BTN": "Bhutan",
    "BUL": "Bulgaria", "BUR": "Myanmar", "CAF": "Central African Rep.", "CAN": "Canada",
    "CHN": "China", "CHL": "Chile", "CMR": "Cameroon", "COD": "DR Congo",
    "COG": "Congo", "COL": "Colombia", "COM": "Comoros", "CRO": "Croatia",
    "CTI": "Ivory Coast", "CUB": "Cuba", "CYP": "Cyprus", "CZE": "Czechia",
    "D": "Germany", "DEN": "Denmark", "E": "Spain", "EGY": "Egypt", "ERI": "Eritrea",
    "ETH": "Ethiopia", "F": "France", "FIN": "Finland", "G": "United Kingdom",
    "GAB": "Gabon", "GEO": "Georgia", "GHA": "Ghana", "GNE": "Equatorial Guinea",
    "GRC": "Greece", "GTM": "Guatemala", "GUF": "French Guiana", "HNG": "Hungary",
    "HOL": "Netherlands", "HRV": "Croatia", "HWA": "Hawaii", "I": "Italy",
    "IND": "India", "INS": "Indonesia", "IRL": "Ireland", "IRN": "Iran", "IRQ": "Iraq",
    "ISL": "Iceland", "ISR": "Israel", "J": "Japan", "JOR": "Jordan",
    "KAZ": "Kazakhstan", "KEN": "Kenya", "KGZ": "Kyrgyzstan", "KOR": "South Korea",
    "KRE": "North Korea", "KWT": "Kuwait", "LAO": "Laos", "LBN": "Lebanon",
    "LBY": "Libya", "LTU": "Lithuania", "LVA": "Latvia", "MAR": "Morocco",
    "MDG": "Madagascar", "MEX": "Mexico", "MLA": "Malaysia", "MLI": "Mali",
    "MLT": "Malta", "MNG": "Mongolia", "MOZ": "Mozambique", "MRC": "Morocco",
    "MRT": "Mauritania", "MWI": "Malawi", "MYA": "Myanmar", "NCL": "New Caledonia",
    "NGR": "Niger", "NIG": "Nigeria", "NOR": "Norway", "NZL": "New Zealand",
    "OMA": "Oman", "PAK": "Pakistan", "PHL": "Philippines", "PLW": "Palau",
    "PNG": "Papua New Guinea", "POL": "Poland", "POR": "Portugal", "PRU": "Peru",
    "QAT": "Qatar", "REU": "Réunion", "ROU": "Romania", "RRW": "Rwanda",
    "RUS": "Russia", "S": "Sweden", "SDN": "Sudan", "SEN": "Senegal",
    "SNG": "Singapore", "SOM": "Somalia", "SUI": "Switzerland", "SVK": "Slovakia",
    "SVN": "Slovenia", "SWZ": "Eswatini", "SYR": "Syria", "TCD": "Chad", "TGO": "Togo",
    "THA": "Thailand", "TJK": "Tajikistan", "TKM": "Turkmenistan", "TZA": "Tanzania",
    "UAE": "United Arab Emirates", "UGA": "Uganda", "UKR": "Ukraine",
    "URG": "Uruguay", "USA": "United States", "UZB": "Uzbekistan", "VTN": "Vietnam",
    "YEM": "Yemen", "ZMB": "Zambia", "ZWE": "Zimbabwe",
    "AGL": "Angola", "SRL": "Sierra Leone", "CLM": "Colombia", "NMB": "Namibia",
    "MDR": "Madagascar", "TWN": "Taiwan", "VRC": "China (PRC)", "HON": "Honduras",
    "CLN": "Sri Lanka",
}


def _table(nl: dict, en: dict) -> dict:
    """Namentabel in de taal van de interface (Engels valt terug op Nederlands)."""
    from .i18n import get_language
    return en if get_language() == "en" else nl


def translate_lang(code: str) -> str:
    """Vertaal EIBI taalcode naar volledige naam. Geeft '' terug als onbekend."""
    code = code.strip()
    return _table(LANG, LANG_EN).get(code) or LANG.get(code, "")


def translate_target(code: str) -> str:
    """Vertaal EIBI doelgebied-code naar volledige naam."""
    code = code.strip()
    return _table(TARGET, TARGET_EN).get(code) or TARGET.get(code, "")


def translate_itu(code: str) -> str:
    """Vertaal ITU landcode naar volledige landnaam."""
    code = code.strip()
    return _table(ITU, ITU_EN).get(code) or ITU.get(code, "")


def enrich_row(row: list) -> dict:
    """Voeg vertalingen toe als dict aan een EIBI-rij.

    Retourneert {'lang_full': ..., 'target_full': ..., 'itu_full': ...}
    zodat de originele rij onaangetast blijft.
    """
    fields = (row + [""] * 8)[:8]
    return {
        "lang_full":   translate_lang(fields[5]),
        "target_full": translate_target(fields[6]),
        "itu_full":    translate_itu(fields[3]),
    }
