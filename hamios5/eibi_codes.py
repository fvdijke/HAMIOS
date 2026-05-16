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
    "SW":   "Zweeds",
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
    "SW":   "Swahili",
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


def translate_lang(code: str) -> str:
    """Vertaal EIBI taalcode naar volledige naam. Geeft '' terug als onbekend."""
    code = code.strip()
    return LANG.get(code, "")


def translate_target(code: str) -> str:
    """Vertaal EIBI doelgebied-code naar volledige naam."""
    code = code.strip()
    return TARGET.get(code, "")


def translate_itu(code: str) -> str:
    """Vertaal ITU landcode naar volledige landnaam."""
    code = code.strip()
    return ITU.get(code, "")


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
