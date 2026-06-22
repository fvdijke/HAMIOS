"""HAMIOS Antenna Calculator - Extended Antenna Types (100+)

Complete categorized antenna type library with bilingual support.
"""

from dataclasses import dataclass
from typing import List

@dataclass
class AntennaTypeExt:
    """Extended antenna type with bilingual support."""
    id: str
    name_nl: str
    name_en: str
    category_nl: str
    category_en: str
    formula_ft: str
    formula_m: str
    impedance: str
    balun: str
    atu_needed: str
    suitable_for_rx: bool

    @property
    def name(self) -> str:
        return self.name_nl

ANTENNA_TYPES_EXTENDED = [
    # DRAADANTENNES - DIPOLES
    AntennaTypeExt("hw_dipole", "Half Wave Dipole", "Half Wave Dipole", "Dipoles", "Dipoles", "468/f", "142.65/f", "~73Ω", "1:1", "No", False),
    AntennaTypeExt("folded_dipole", "Folded Dipole", "Folded Dipole", "Dipoles", "Dipoles", "468/f", "142.65/f", "~300Ω", "4:1", "Yes", False),
    AntennaTypeExt("fan_dipole", "Fan Dipole", "Fan Dipole", "Dipoles", "Dipoles", "Per band", "Per band", "~50Ω", "1:1", "No", False),
    AntennaTypeExt("trapped_dipole", "Trapped Dipole", "Trapped Dipole", "Dipoles", "Dipoles", "Multiband", "Multiband", "~50Ω", "1:1", "No", False),
    AntennaTypeExt("loaded_dipole", "Loaded Dipole", "Loaded Dipole", "Dipoles", "Dipoles", "Shorter", "Shorter", "~50Ω", "1:1", "No", False),
    AntennaTypeExt("ocfd", "Off-Center Fed Dipole", "Off-Center Fed Dipole", "Dipoles", "Dipoles", "468/f", "142.65/f", "~200Ω", "4:1", "Optional", False),
    AntennaTypeExt("doublet", "Doublet", "Doublet", "Dipoles", "Dipoles", "468/f", "142.65/f", "~600Ω", "9:1", "Yes", False),
    AntennaTypeExt("cage_dipole", "Cage Dipole", "Cage Dipole", "Dipoles", "Dipoles", "468/f", "142.65/f", "~73Ω", "1:1", "No", False),

    # END-FED ANTENNES
    AntennaTypeExt("efhw", "EFHW", "End Fed Half Wave", "End-Fed", "End-Fed", "468/f", "142.65/f", "~2400Ω", "49:1", "Optional", False),
    AntennaTypeExt("efrw", "EFRW", "End Fed Random Wire", "End-Fed", "End-Fed", "Any", "Any", "High-Z", "9:1", "Required", False),
    AntennaTypeExt("random_wire", "Random Wire", "Random Wire", "End-Fed", "End-Fed", "Any", "Any", "High-Z", "9:1", "Required", True),
    AntennaTypeExt("long_wire", "Long Wire", "Long Wire", "End-Fed", "End-Fed", "Multiλ", "Multiλ", "High-Z", "9:1", "Required", True),
    AntennaTypeExt("zepp", "Zepp Antenna", "Zepp Antenna", "End-Fed", "End-Fed", "468/f", "142.65/f", "~600Ω", "4:1", "Yes", False),

    # INVERTED VARIATIES
    AntennaTypeExt("inverted_v", "Inverted-V", "Inverted-V", "Inverted", "Inverted", "468/f", "142.65/f", "~50Ω", "1:1", "Optional", False),
    AntennaTypeExt("inverted_l", "Inverted-L", "Inverted-L", "Inverted", "Inverted", "3λ/4", "3λ/4", "~50Ω", "1:1", "Optional", False),
    AntennaTypeExt("inverted_u", "Inverted-U", "Inverted-U", "Inverted", "Inverted", "468/f", "142.65/f", "~50Ω", "1:1", "Optional", False),

    # VERTICALE ANTENNES - MONOBAND
    AntennaTypeExt("qwave_vert", "Quarter Wave Vertical", "Quarter Wave Vertical", "Vertical Monoband", "Vertical Monoband", "234/f", "71.3/f", "~37Ω", "Direct", "Optional", False),
    AntennaTypeExt("hw_vert", "Half Wave Vertical", "Half Wave Vertical", "Vertical Monoband", "Vertical Monoband", "468/f", "142.65/f", "~73Ω", "1:1", "Optional", False),
    AntennaTypeExt("5_8_vert", "5/8 Wave Vertical", "5/8 Wave Vertical", "Vertical Monoband", "Vertical Monoband", "585/f", "178.3/f", "~52Ω", "Direct", "Optional", False),

    # VERTICALE ANTENNES - MULTIBAND
    AntennaTypeExt("trapped_vert", "Trapped Vertical", "Trapped Vertical", "Vertical Multiband", "Vertical Multiband", "Per band", "Per band", "~50Ω", "Direct", "Optional", False),
    AntennaTypeExt("ground_indep_vert", "Ground Independent", "Ground Independent", "Vertical Multiband", "Vertical Multiband", "Multiband", "Multiband", "~50Ω", "Direct", "Optional", False),
    AntennaTypeExt("multiband_vert", "Multiband Vertical", "Multiband Vertical", "Vertical Multiband", "Vertical Multiband", "Per band", "Per band", "~50Ω", "Direct", "Optional", False),

    # VERTICALE ANTENNES - SPECIALE
    AntennaTypeExt("marconi_vert", "Marconi Vertical", "Marconi Vertical", "Vertical Special", "Vertical Special", "234/f", "71.3/f", "~37Ω", "Direct", "Optional", False),
    AntennaTypeExt("elevated_vert", "Elevated Vertical", "Elevated Vertical", "Vertical Special", "Vertical Special", "234/f", "71.3/f", "~50Ω", "Direct", "Optional", False),
    AntennaTypeExt("sloper_vert", "Sloper Vertical", "Sloper Vertical", "Vertical Special", "Vertical Special", "468/f", "142.65/f", "~50Ω", "1:1", "Recommended", False),

    # LOOP ANTENNES - RESONANTE
    AntennaTypeExt("full_loop", "Full Wave Loop", "Full Wave Loop", "Loop Resonant", "Loop Resonant", "1005/f", "306.3/f", "~200Ω", "4:1", "Recommended", False),
    AntennaTypeExt("half_loop", "Half Wave Loop", "Half Wave Loop", "Loop Resonant", "Loop Resonant", "468/f", "142.65/f", "~73Ω", "1:1", "Optional", False),
    AntennaTypeExt("square_loop", "Square Loop", "Square Loop", "Loop Resonant", "Loop Resonant", "1005/f", "306.3/f", "~200Ω", "4:1", "Recommended", False),
    AntennaTypeExt("rect_loop", "Rectangular Loop", "Rectangular Loop", "Loop Resonant", "Loop Resonant", "1005/f", "306.3/f", "~200Ω", "4:1", "Recommended", False),
    AntennaTypeExt("delta_loop", "Delta Loop", "Delta Loop", "Loop Resonant", "Loop Resonant", "1005/f", "306.3/f", "~100Ω", "4:1", "Optional", False),
    AntennaTypeExt("triangle_loop", "Triangle Loop", "Triangle Loop", "Loop Resonant", "Loop Resonant", "1005/f", "306.3/f", "~100Ω", "4:1", "Optional", False),

    # LOOP ANTENNES - GROTE LOOPS
    AntennaTypeExt("horiz_loop", "Horizontal Loop", "Horizontal Loop", "Loop Large", "Loop Large", "1005/f", "306.3/f", "~200Ω", "4:1", "Recommended", False),
    AntennaTypeExt("skywire_loop", "Skywire Loop", "Skywire Loop", "Loop Large", "Loop Large", "1005/f", "306.3/f", "~200Ω", "4:1", "Recommended", False),
    AntennaTypeExt("quad_loop", "Quad Loop", "Quad Loop", "Loop Large", "Loop Large", "1005/f", "306.3/f", "~200Ω", "4:1", "Recommended", False),

    # LOOP ANTENNES - ONTVANGST
    AntennaTypeExt("log", "Loop On Ground", "Loop On Ground", "Loop RX", "Loop RX", "Varies", "Varies", "Variable", "Optional", "No", True),
    AntennaTypeExt("k9ay_loop", "K9AY Loop", "K9AY Loop", "Loop RX", "Loop RX", "Varies", "Varies", "~50Ω", "Optional", "No", True),
    AntennaTypeExt("flag_ant", "Flag Antenna", "Flag Antenna", "Loop RX", "Loop RX", "Varies", "Varies", "Variable", "Optional", "No", True),
    AntennaTypeExt("pennant_ant", "Pennant Antenna", "Pennant Antenna", "Loop RX", "Loop RX", "Varies", "Varies", "Variable", "Optional", "No", True),

    # LOOP ANTENNES - MAGNETISCHE
    AntennaTypeExt("small_mag_loop", "Small Magnetic Loop", "Small Magnetic Loop", "Loop Magnetic", "Loop Magnetic", "~0.1λ", "~0.1λ", "~50Ω", "Variable", "No", True),
    AntennaTypeExt("large_mag_loop", "Large Magnetic Loop", "Large Magnetic Loop", "Loop Magnetic", "Loop Magnetic", "0.3λ", "0.3λ", "~50Ω", "Variable", "No", True),
    AntennaTypeExt("butterfly_loop", "Butterfly Loop", "Butterfly Loop", "Loop Magnetic", "Loop Magnetic", "~0.2λ", "~0.2λ", "~50Ω", "Variable", "No", True),

    # RICHTANTENNES - YAGI
    AntennaTypeExt("yagi_2", "2 Element Yagi", "2 Element Yagi", "Directional Yagi", "Directional Yagi", "Varies", "Varies", "~50Ω", "Direct", "No", False),
    AntennaTypeExt("yagi_3", "3 Element Yagi", "3 Element Yagi", "Directional Yagi", "Directional Yagi", "Varies", "Varies", "~50Ω", "Direct", "No", False),
    AntennaTypeExt("yagi_4", "4 Element Yagi", "4 Element Yagi", "Directional Yagi", "Directional Yagi", "Varies", "Varies", "~50Ω", "Direct", "No", False),
    AntennaTypeExt("yagi_5plus", "5+ Element Yagi", "5+ Element Yagi", "Directional Yagi", "Directional Yagi", "Varies", "Varies", "~50Ω", "Direct", "No", False),

    # RICHTANTENNES - ANDERE
    AntennaTypeExt("hexbeam", "Hexbeam", "Hexbeam", "Directional Other", "Directional Other", "Varies", "Varies", "~50Ω", "Direct", "No", False),
    AntennaTypeExt("spiderbeam", "Spiderbeam", "Spiderbeam", "Directional Other", "Directional Other", "Varies", "Varies", "~50Ω", "Direct", "No", False),
    AntennaTypeExt("moxon_rect", "Moxon Rectangle", "Moxon Rectangle", "Directional Other", "Directional Other", "Varies", "Varies", "~50Ω", "Direct", "No", False),
    AntennaTypeExt("cubical_quad", "Cubical Quad", "Cubical Quad", "Directional Other", "Directional Other", "Varies", "Varies", "~50Ω", "4:1", "Optional", False),
    AntennaTypeExt("log_periodic", "Log Periodic", "Log Periodic", "Directional Other", "Directional Other", "Varies", "Varies", "~50Ω", "Direct", "No", False),

    # ONTVANGST - LF/MF/HF
    AntennaTypeExt("beverage", "Beverage", "Beverage", "RX LF/MF/HF", "RX LF/MF/HF", "Multiλ", "Multiλ", "~600Ω", "9:1", "No", True),
    AntennaTypeExt("bog", "BOG", "Beverage On Ground", "RX LF/MF/HF", "RX LF/MF/HF", "Multiλ", "Multiλ", "~600Ω", "9:1", "No", True),
    AntennaTypeExt("k9ay", "K9AY", "K9AY", "RX LF/MF/HF", "RX LF/MF/HF", "Varies", "Varies", "~50Ω", "Direct", "No", True),
    AntennaTypeExt("flag", "Flag", "Flag", "RX LF/MF/HF", "RX LF/MF/HF", "Varies", "Varies", "Variable", "Optional", "No", True),
    AntennaTypeExt("pennant", "Pennant", "Pennant", "RX LF/MF/HF", "RX LF/MF/HF", "Varies", "Varies", "Variable", "Optional", "No", True),
    AntennaTypeExt("ewe", "EWE", "EWE", "RX LF/MF/HF", "RX LF/MF/HF", "Varies", "Varies", "~50Ω", "Optional", "No", True),
    AntennaTypeExt("active_loop", "Active Loop", "Active Loop", "RX LF/MF/HF", "RX LF/MF/HF", "Varies", "Varies", "~50Ω", "Amplifier", "No", True),

    # ONTVANGST - BREEDBAND
    AntennaTypeExt("active_whip", "Active Whip", "Active Whip", "RX Broadband", "RX Broadband", "Short", "Short", "~50Ω", "Amplifier", "No", True),
    AntennaTypeExt("miniwhip", "MiniWhip", "MiniWhip", "RX Broadband", "RX Broadband", "Small", "Small", "~50Ω", "Amplifier", "No", True),
    AntennaTypeExt("discone", "Discone", "Discone", "RX Broadband", "RX Broadband", "Wideband", "Wideband", "~50Ω", "Direct", "No", True),
    AntennaTypeExt("bb_dipole", "Broadband Dipole", "Broadband Dipole", "RX Broadband", "RX Broadband", "468/f", "142.65/f", "~50Ω", "1:1", "No", True),

    # PORTABLE / POTA / SOTA
    AntennaTypeExt("linked_dipole", "Linked Dipole", "Linked Dipole", "Portable", "Portable", "468/f", "142.65/f", "~50Ω", "1:1", "No", False),
    AntennaTypeExt("portable_efhw", "Portable EFHW", "Portable EFHW", "Portable", "Portable", "468/f", "142.65/f", "~2400Ω", "49:1", "Optional", False),
    AntennaTypeExt("random_9to1", "Random Wire + 9:1", "Random Wire + 9:1", "Portable", "Portable", "Any", "Any", "High-Z", "9:1", "Required", False),
    AntennaTypeExt("lightweight_vert", "Lightweight Vertical", "Lightweight Vertical", "Portable", "Portable", "234/f", "71.3/f", "~37Ω", "Direct", "Optional", False),
    AntennaTypeExt("telescopic_vert", "Telescopic Vertical", "Telescopic Vertical", "Portable", "Portable", "234/f", "71.3/f", "~37Ω", "Direct", "Optional", False),
    AntennaTypeExt("portable_loop", "Portable Loop", "Portable Loop", "Portable", "Portable", "1005/f", "306.3/f", "~200Ω", "4:1", "Recommended", False),
    AntennaTypeExt("delta_portable", "Delta Loop Portable", "Delta Loop Portable", "Portable", "Portable", "1005/f", "306.3/f", "~100Ω", "4:1", "Optional", False),

    # VHF/UHF - VERTICALS
    AntennaTypeExt("gp_antenna", "Ground Plane", "Ground Plane", "VHF/UHF Vertical", "VHF/UHF Vertical", "234/f", "71.3/f", "~50Ω", "Direct", "No", False),
    AntennaTypeExt("jpole", "J-Pole", "J-Pole", "VHF/UHF Vertical", "VHF/UHF Vertical", "702/f", "213.9/f", "~50Ω", "Stub", "No", False),
    AntennaTypeExt("slim_jim", "Slim Jim", "Slim Jim", "VHF/UHF Vertical", "VHF/UHF Vertical", "702/f", "213.9/f", "~50Ω", "Stub", "No", False),
    AntennaTypeExt("collinear", "Collinear", "Collinear", "VHF/UHF Vertical", "VHF/UHF Vertical", "Varies", "Varies", "~50Ω", "Direct", "No", False),
    AntennaTypeExt("coax_collinear", "Coaxial Collinear", "Coaxial Collinear", "VHF/UHF Vertical", "VHF/UHF Vertical", "Varies", "Varies", "~50Ω", "Direct", "No", False),

    # VHF/UHF - RICHTANTENNES
    AntennaTypeExt("vhf_yagi", "VHF Yagi", "VHF Yagi", "VHF/UHF Beam", "VHF/UHF Beam", "Varies", "Varies", "~50Ω", "Direct", "No", False),
    AntennaTypeExt("uhf_yagi", "UHF Yagi", "UHF Yagi", "VHF/UHF Beam", "VHF/UHF Beam", "Varies", "Varies", "~50Ω", "Direct", "No", False),
    AntennaTypeExt("vhf_lp", "VHF Log Periodic", "VHF Log Periodic", "VHF/UHF Beam", "VHF/UHF Beam", "Varies", "Varies", "~50Ω", "Direct", "No", False),
    AntennaTypeExt("vhf_quad", "VHF Quad", "VHF Quad", "VHF/UHF Beam", "VHF/UHF Beam", "Varies", "Varies", "~50Ω", "4:1", "Optional", False),

    # VHF/UHF - SATELLIET
    AntennaTypeExt("arrow_ant", "Arrow Antenna", "Arrow Antenna", "VHF/UHF Satellite", "VHF/UHF Satellite", "Varies", "Varies", "~50Ω", "Direct", "No", False),
    AntennaTypeExt("eggbeater", "Eggbeater", "Eggbeater", "VHF/UHF Satellite", "VHF/UHF Satellite", "Varies", "Varies", "~50Ω", "Direct", "No", False),
    AntennaTypeExt("turnstile", "Turnstile", "Turnstile", "VHF/UHF Satellite", "VHF/UHF Satellite", "Varies", "Varies", "~50Ω", "Direct", "No", False),
    AntennaTypeExt("helix_sat", "Helix", "Helix", "VHF/UHF Satellite", "VHF/UHF Satellite", "Varies", "Varies", "~50Ω", "Direct", "No", False),

    # SPECIALE ANTENNES
    AntennaTypeExt("rhombic", "Rhombic", "Rhombic", "Special", "Special", "Multiλ", "Multiλ", "~600Ω", "9:1", "No", True),
    AntennaTypeExt("t2fd", "T2FD", "Terminated Folded Dipole", "Special", "Special", "Varies", "Varies", "~600Ω", "9:1", "No", False),
    AntennaTypeExt("lazy_h", "Lazy-H", "Lazy-H", "Special", "Special", "Varies", "Varies", "~50Ω", "Direct", "No", False),
    AntennaTypeExt("bobtail_curtain", "Bobtail Curtain", "Bobtail Curtain", "Special", "Special", "Varies", "Varies", "~50Ω", "Direct", "No", False),
    AntennaTypeExt("sterba_curtain", "Sterba Curtain", "Sterba Curtain", "Special", "Special", "Varies", "Varies", "~50Ω", "Direct", "No", False),
    AntennaTypeExt("hentenna", "Hentenna", "Hentenna", "Special", "Special", "Varies", "Varies", "~50Ω", "Direct", "No", False),
    AntennaTypeExt("cobweb", "Cobweb", "Cobweb", "Special", "Special", "Varies", "Varies", "~50Ω", "Direct", "No", False),
    AntennaTypeExt("cobwebb", "Cobwebb", "Cobwebb", "Special", "Special", "Varies", "Varies", "~50Ω", "Direct", "No", False),
    AntennaTypeExt("folded_mono", "Folded Monopole", "Folded Monopole", "Special", "Special", "Varies", "Varies", "~50Ω", "Direct", "No", False),

    # MOBIELE ANTENNES
    AntennaTypeExt("qwave_mobile", "Quarter Wave Mobile", "Quarter Wave Mobile", "Mobile", "Mobile", "234/f", "71.3/f", "~37Ω", "Direct", "Optional", False),
    AntennaTypeExt("5_8_mobile", "5/8 Wave Mobile", "5/8 Wave Mobile", "Mobile", "Mobile", "585/f", "178.3/f", "~52Ω", "Direct", "Optional", False),
    AntennaTypeExt("helical_mobile", "Helical Mobile", "Helical Mobile", "Mobile", "Mobile", "Short", "Short", "~50Ω", "Direct", "No", False),
    AntennaTypeExt("loaded_whip", "Loaded Mobile Whip", "Loaded Mobile Whip", "Mobile", "Mobile", "Short", "Short", "~50Ω", "Direct", "Optional", False),
    AntennaTypeExt("screwdriver", "Screwdriver Antenna", "Screwdriver Antenna", "Mobile", "Mobile", "Adjustable", "Adjustable", "~50Ω", "Direct", "Optional", False),
    AntennaTypeExt("hamstick", "Hamstick", "Hamstick", "Mobile", "Mobile", "Short", "Short", "~50Ω", "Direct", "Optional", False),
]

def get_antennas_by_category(category_en: str) -> List[AntennaTypeExt]:
    """Get all antennas in a specific category."""
    return [ant for ant in ANTENNA_TYPES_EXTENDED if ant.category_en == category_en]

def get_rx_suitable_antennas() -> List[AntennaTypeExt]:
    """Get antennas marked as suitable for RX-only."""
    return [ant for ant in ANTENNA_TYPES_EXTENDED if ant.suitable_for_rx]

def get_categories() -> List[str]:
    """Get unique categories."""
    return sorted(set(ant.category_en for ant in ANTENNA_TYPES_EXTENDED))
