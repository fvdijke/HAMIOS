"""HAMIOS Antenna Calculator - Complete Antenna Database

All 12 antenna types with comprehensive formulas, matching transformers, and notes.
Industry-standard antenna design calculations.
"""

from dataclasses import dataclass
from typing import List, Tuple, Optional
import math


# ── VELOCITY FACTOR DATABASE ──────────────────────────────────────────────────

@dataclass
class VelocityFactorOption:
    """Velocity factor preset for wire types."""
    label: str                      # Short label (BARE, THIN, etc.)
    name_nl: str                    # Dutch name
    name_en: str                    # English name
    velocity_factor: float
    examples: str                   # Example wire types

    @property
    def name(self) -> str:
        """Get name (Dutch by default)"""
        return self.name_nl


VELOCITY_FACTORS = [
    VelocityFactorOption("KALE_KOPER", "Kale koperdraad", "Bare copper wire", 0.98, "Bare copper · WD-1 · Magnet wire"),
    VelocityFactorOption("VERTINDE_KOPER", "Vertinde koperdraad", "Tinned copper wire", 0.98, "Tinned · Marine · Stranded"),
    VelocityFactorOption("PVC_THIN", "Koperdraad met dunne PVC", "Thin PVC insulation", 0.95, "Thin PVC · Hookup · Automotive"),
    VelocityFactorOption("PVC_THICK", "Koperdraad met dikke PVC", "Heavy PVC jacket", 0.93, "Heavy jacket · Weatherproof · Marine"),
    VelocityFactorOption("VD_1P5", "Installatiedraad VD 1,5 mm²", "Building wire 1.5mm²", 0.95, "Building wire · 1.5mm · Household"),
    VelocityFactorOption("VD_2P5", "Installatiedraad VD 2,5 mm²", "Building wire 2.5mm²", 0.95, "Building wire · 2.5mm · Household"),
    VelocityFactorOption("SPEAKER", "Speakerwire platte luidsprekerkabel", "Speaker cable", 0.94, "Speaker wire · Audio · Zip cord"),
    VelocityFactorOption("DX_PREMIUM", "DX-Wire Premium Antenna", "DX-Wire Premium", 0.97, "Premium antenna · DX-Wire · Professional"),
    VelocityFactorOption("DX_FLEXWEAVE", "DX-Wire Flexweave", "DX-Wire Flexweave", 0.97, "Flexible premium · DX-Wire · Stranded"),
    VelocityFactorOption("SILICONE", "Silicium geïsoleerde draad", "Silicone insulation", 0.96, "Silicone · High-temp · Flex"),
    VelocityFactorOption("PTFE", "PTFE Teflon geïsoleerde", "PTFE Teflon insulation", 0.97, "Teflon · Low-loss · Premium"),
    VelocityFactorOption("RUBBER", "Rubber geïsoleerde draad", "Rubber insulation", 0.94, "Rubber · Flexible · Vintage"),
    VelocityFactorOption("EMAILLE", "Emaille draad magneetdraad", "Enameled magnet wire", 0.98, "Magnet wire · Enameled · Coil"),
    VelocityFactorOption("LITZE", "Litze draad", "Litze stranded wire", 0.96, "Multi-strand · Flexible · Antenna"),
    VelocityFactorOption("ALUMINUM", "Aluminiumdraad", "Aluminum conductor", 0.98, "Aluminum · Tubing · Rod"),
    VelocityFactorOption("COPPERWELD", "Copperweld", "Copper-clad steel", 0.98, "Copper-clad · Hybrid · High-strength"),
    VelocityFactorOption("STAINLESS", "RVS draad", "Stainless steel wire", 0.98, "Stainless · Corrosion-proof · Marine"),
    VelocityFactorOption("ELECTRIC_FENCE", "Elektrisch schrikdraad", "Electric fence wire", 0.98, "Fence wire · Steel · Farm"),
    VelocityFactorOption("WD1A", "WD-1A/TT veldtelefoondraad", "WD-1A field telephone", 0.95, "Military · Field · Durable"),
    VelocityFactorOption("CAT5", "CAT5 ader als antennedraad", "CAT5 network cable", 0.94, "Network cable · Twisted · Salvaged"),
    VelocityFactorOption("CAT6", "CAT6 ader als antennedraad", "CAT6 network cable", 0.94, "Network cable · Twisted · Salvaged"),
    VelocityFactorOption("POLYESTER", "Polyester ommanteld", "Polyester jacket", 0.95, "Weather-resistant · UV-proof · Outdoor"),
    VelocityFactorOption("POLYETHYLENE", "Polyethyleen PE geïsoleerd", "Polyethylene insulation", 0.96, "Flexible · RF cable · Antenna"),
]


# ── COAX DATABASE ─────────────────────────────────────────────────────────────

@dataclass
class CoaxCable:
    """Coax cable with frequency-dependent loss data."""
    label: str                              # Short name (RG-58, RG-213, etc.)
    category: str                           # Category for grouping
    velocity_factor: float
    loss_db_per_100ft: dict[float, float]  # Frequency MHz -> Loss dB per 100ft
    note: str


COAX_CABLES = [
    CoaxCable(
        label="RG-174",
        category="Thin/HT use",
        velocity_factor=0.66,
        loss_db_per_100ft={
            1.8: 0.9, 3.5: 1.3, 7.0: 1.8, 14.0: 2.6, 21.0: 3.2,
            28.0: 3.7, 50.0: 5.0, 144.0: 8.5, 446.0: 15.0
        },
        note="Very thin, high loss. Good for short HT pigtails only. Avoid for HF runs over 25ft."
    ),
    CoaxCable(
        label="RG-58",
        category="Common/thin",
        velocity_factor=0.66,
        loss_db_per_100ft={
            1.8: 0.4, 3.5: 0.6, 7.0: 0.9, 14.0: 1.3, 21.0: 1.6,
            28.0: 1.9, 50.0: 2.5, 144.0: 4.5, 446.0: 8.0
        },
        note="Most common boneyard find. Acceptable for short HF runs. Gets lossy fast on VHF/UHF."
    ),
    CoaxCable(
        label="RG-8X",
        category="Mini 8 / compromise",
        velocity_factor=0.82,
        loss_db_per_100ft={
            1.8: 0.3, 3.5: 0.4, 7.0: 0.6, 14.0: 0.9, 21.0: 1.1,
            28.0: 1.3, 50.0: 1.8, 144.0: 3.1, 446.0: 5.8
        },
        note="Good compromise – low loss, flexible, smaller than RG-213. Solid boneyard pick."
    ),
    CoaxCable(
        label="RG-213",
        category="Full size / low loss",
        velocity_factor=0.66,
        loss_db_per_100ft={
            1.8: 0.2, 3.5: 0.3, 7.0: 0.4, 14.0: 0.6, 21.0: 0.75,
            28.0: 0.9, 50.0: 1.2, 144.0: 2.1, 446.0: 4.0
        },
        note="Standard station coax. Buy this over RG-58 at any hamfest if runs exceed 50ft."
    ),
    CoaxCable(
        label="LMR-400",
        category="Premium low loss",
        velocity_factor=0.81,
        loss_db_per_100ft={
            1.8: 0.1, 3.5: 0.15, 7.0: 0.2, 14.0: 0.3, 21.0: 0.38,
            28.0: 0.44, 50.0: 0.6, 144.0: 1.0, 446.0: 1.9
        },
        note="Best field find. Grab it regardless of price – worth it for any run over 25ft."
    ),
    CoaxCable(
        label="MYSTERY",
        category="Unknown coax",
        velocity_factor=0.72,
        loss_db_per_100ft={
            1.8: 0.5, 3.5: 0.7, 7.0: 1.1, 14.0: 1.6, 21.0: 2.0,
            28.0: 2.4, 50.0: 3.2, 144.0: 5.5, 446.0: 10.0
        },
        note="Unknown coax – using conservative worst-case estimate. Measure with NanoVNA if possible."
    ),
]


# ── ANTENNA TYPE DEFINITIONS ───────────────────────────────────────────────────

@dataclass
class AntennaTypeSpec:
    """Complete specification for an antenna type."""
    id: str                         # Unique ID
    name: str                       # Display name
    formula_ft: str                 # Formula for feet
    formula_m: str                  # Formula for meters
    match_type: str                 # Matching transformer type
    match_ratio: str                # Transformer ratio
    match_impedance: str            # Impedance at feedpoint
    atu_needed: str                 # "No", "Optional", "Recommended", "REQUIRED"
    match_note: str                 # Technical note on matching
    field_notes: str                # Extended deployment notes
    dimensions_formula: callable    # Function to calculate dimensions (freq_mhz) -> [(label, value_ft, sub), ...]


def create_antenna_specs() -> List[AntennaTypeSpec]:
    """Create all 12 antenna type specifications."""

    # DIPOLE
    def dipole_dims(f):
        half_len = 234 / f  # 468 / 2 / f
        return [
            ("TOTAL LENGTH", 468 / f, "each leg = " + f"{half_len:.2f}"),
            ("EACH LEG", half_len, "feed at center"),
        ]

    dipole = AntennaTypeSpec(
        id="dipole",
        name="Dipole\n½λ",
        formula_ft="468 / f(MHz)",
        formula_m="142.65 / f(MHz)",
        match_type="1:1 Current Balun",
        match_ratio="1:1",
        match_impedance="~50Ω balanced",
        atu_needed="Optional",
        match_note="1:1 current balun at feedpoint prevents feedline from radiating. Eliminates pattern distortion and RFI into shack.",
        field_notes="""Half-Wave Dipole – Workhorse field antenna. Center-feed with coax. Each leg = total/2.
Hang horizontal between two trees, as high as possible.
NVIS: Hang ≤0.1λ high (≤45ft on 40m) for regional 0–300 mi coverage.
DX: Hang as high as possible for low-angle radiation skip.
Usable on harmonic frequencies.""",
        dimensions_formula=dipole_dims
    )

    # INVERTED-V
    def invv_dims(f):
        total = 462 / f
        leg = total / 2
        return [
            ("TOTAL LENGTH", total, "apex at top"),
            ("EACH LEG", leg, "~45° droop angle"),
        ]

    invv = AntennaTypeSpec(
        id="invv",
        name="Inverted\nV",
        formula_ft="462 / f(MHz)",
        formula_m="140.8 / f(MHz)",
        match_type="1:1 Current Balun",
        match_ratio="1:1",
        match_impedance="~50–75Ω (leg angle)",
        atu_needed="Optional",
        match_note="1:1 current balun at apex feedpoint. Drooping legs shift impedance slightly but 50Ω coax works fine.",
        field_notes="""Inverted-V Dipole – One support needed. Same wire as flat dipole.
45° from vertical = DX – low-angle radiation, 1000+ mi skip.
60° from vertical = Regional – compromise, 300–800 mi range.
>60° approaching flat = NVIS – use flat dipole formula instead.""",
        dimensions_formula=invv_dims
    )

    # QUARTER WAVE VERTICAL
    def qwave_dims(f):
        elem = 234 / f
        return [
            ("VERT ELEMENT", elem, "run vertical"),
            ("EACH RADIAL", elem, "2–4 radials needed"),
        ]

    qwave = AntennaTypeSpec(
        id="qwave",
        name="¼λ\nVertical",
        formula_ft="234 / f(MHz)",
        formula_m="71.3 / f(MHz)",
        match_type="Direct Feed – No Balun",
        match_ratio="N/A",
        match_impedance="~36Ω with radials",
        atu_needed="Optional",
        match_note="Direct 50Ω coax feed at base. No balun needed with a good radial system. 4 radials minimum.",
        field_notes="""Quarter-Wave Vertical – Vertical element + ground radials.
Deploy 2–4 radials same length as vertical element.
DX: Low-angle omnidirectional radiation – excellent for skip contacts.
Stake base or use tripod, run element vertically up pole or tree.
Elevated radials outperform on-ground radials significantly.""",
        dimensions_formula=qwave_dims
    )

    # JUNGLE GP / 292
    def jungle_gp_dims(f):
        elem = 234 / f
        stick = elem * math.sin(math.radians(45))
        return [
            ("ELEMENT", elem, "vertical – goes up"),
            ("EACH RADIAL", elem, "3 needed – droop down"),
            ("SPACING STICK", stick, "3 sticks · 120° apart"),
        ]

    jungle_gp = AntennaTypeSpec(
        id="jungleGP",
        name="Jungle GP\n/ 292",
        formula_ft="234 / f(MHz)",
        formula_m="71.3 / f(MHz)",
        match_type="Direct Feed – No Balun",
        match_ratio="N/A",
        match_impedance="~50Ω elevated 45°",
        atu_needed="Optional",
        match_note="Direct 50Ω coax feed at feedpoint. No balun needed. Radials drooping at 45° naturally match ~50Ω.",
        field_notes="""Jungle GP / 292 / Elevated Ground Plane
Same math as ¼λ Vertical – just deployed differently.
Hoist feedpoint into tree. Element goes UP, 3 radials droop DOWN forming pyramid.
3 spacing sticks (field sticks from forest floor) hold radials 120° apart.
Impedance by droop angle: Horizontal ~50Ω · 45° droop ~50Ω · Steep droop ~35Ω.
Elevated always outperforms ground mount – less ground loss, better radiation angle.""",
        dimensions_formula=jungle_gp_dims
    )

    # FULL-WAVE LOOP
    def loop_dims(f):
        perimeter = 1005 / f
        side = perimeter / 4
        return [
            ("PERIMETER", perimeter, "any shape"),
            ("EACH SIDE (SQ)", side, "4 equal sides"),
        ]

    loop = AntennaTypeSpec(
        id="loop",
        name="Full-Wave\nLoop",
        formula_ft="1005 / f(MHz)",
        formula_m="306.3 / f(MHz)",
        match_type="4:1 Current Balun",
        match_ratio="4:1",
        match_impedance="~100–300Ω balanced",
        atu_needed="Recommended",
        match_note="4:1 current balun brings loop impedance (~200–300Ω) closer to 50Ω coax. ATU recommended.",
        field_notes="""Full-Wave Loop – String in any shape: square, delta, circle.
DX: Feed at corner – low-angle radiation.
NVIS: Feed at midpoint of top wire – high-angle, regional.
1–1.5 dB gain over dipole. Quieter receive than dipole on noise.""",
        dimensions_formula=loop_dims
    )

    # DELTA LOOP
    def delta_dims(f):
        perimeter = 1005 / f
        side = perimeter / 3
        height = side * math.sin(math.radians(60))
        return [
            ("EACH SIDE", side, "3 equal sides"),
            ("APEX HEIGHT", height, "min height for equilateral"),
            ("BASE WIDTH", side, "bottom corner to corner"),
        ]

    delta = AntennaTypeSpec(
        id="delta",
        name="Delta\nLoop",
        formula_ft="1005 / f(MHz) ÷ 3 per side",
        formula_m="306.3 / f(MHz) ÷ 3 per side",
        match_type="4:1 Current Balun",
        match_ratio="4:1",
        match_impedance="~100Ω balanced",
        atu_needed="Optional",
        match_note="Feed at bottom corner for low-angle DX radiation. Feed at midpoint of bottom side for NVIS/regional.",
        field_notes="""Delta Loop – Equilateral triangle. Only ONE support needed at apex.
Advantage over square loop: Single apex support (tree/mast) – two bottom corners staked out.
DX: Feed at bottom corner – low-angle radiation, similar to vertical.
NVIS: Feed at center of bottom wire – high-angle regional coverage.
1–1.5 dB gain over dipole. Broadband – lower SWR swing than dipole.""",
        dimensions_formula=delta_dims
    )

    # EFHW (END-FED HALF WAVE)
    def efhw_dims(f):
        total = 468 / f
        cp = total * 0.05
        return [
            ("WIRE LENGTH", total, "feed at one end"),
            ("COUNTERPOISE", cp, "~5% of total"),
        ]

    efhw = AntennaTypeSpec(
        id="efhw",
        name="EFHW\nEnd-Fed",
        formula_ft="468 / f(MHz)",
        formula_m="142.65 / f(MHz)",
        match_type="49:1 UnUn",
        match_ratio="49:1",
        match_impedance="~2400Ω → 50Ω",
        atu_needed="Optional",
        match_note="49:1 or 64:1 UnUn required at feedpoint. High impedance end (~2400Ω) must step down to match 50Ω coax.",
        field_notes="""End-Fed Half-Wave (EFHW) – Single wire, one-end feed via 49:1 UnUn.
Same length as dipole but fed from one end – easy tree deploy.
Sloper config: High end in tree, low end tied off – portable DX.
Inverted-L config: Vertical then horizontal – NVIS + some DX.
Multiband capable with ATU on harmonic frequencies.""",
        dimensions_formula=efhw_dims
    )

    # RANDOM WIRE
    def random_dims(f):
        good_lengths = [29, 35, 41, 58, 71, 84, 107, 119, 130]
        hw = 468 / f
        suggested = next((l for l in good_lengths if l > hw * 0.8), 130)
        return [
            ("SUGGESTED LENGTH", suggested, "non-resonant wire"),
            ("COUNTERPOISE", 24, "16–33 ft at feedpoint"),
        ]

    random = AntennaTypeSpec(
        id="random",
        name="Random\nWire",
        formula_ft="Any length",
        formula_m="Any length",
        match_type="9:1 UnUn + ATU",
        match_ratio="9:1",
        match_impedance="High-Z random → ~50Ω",
        atu_needed="REQUIRED",
        match_note="9:1 UnUn steps random high impedance to a range the ATU can handle. ATU is NOT optional.",
        field_notes="""Random Wire / Inverted-L – Any wire length, 9:1 UnUn + ATU required.
Inverted-L: Wire vertical as high as possible, then horizontal – NVIS + regional mix.
Sloper: Wire slopes high to low – DX emphasis.
Good wire lengths (non-resonant): 29, 35, 41, 58, 71, 84, 107, 119, 130 ft.
AVOID half-wave multiples of target freq – e.g. on 40m avoid ~66ft, ~132ft, ~198ft.""",
        dimensions_formula=random_dims
    )

    # SLOPER
    def sloper_dims(f):
        total = 468 / f
        horiz = total * math.cos(math.radians(35))
        return [
            ("WIRE LENGTH", total, "full half-wave"),
            ("HORIZ SPAN (35° from horiz)", horiz, "apex to ground anchor"),
        ]

    sloper = AntennaTypeSpec(
        id="sloper",
        name="Sloper\nHalf-W",
        formula_ft="468 / f(MHz)",
        formula_m="142.65 / f(MHz)",
        match_type="1:1 Balun or Direct",
        match_ratio="1:1",
        match_impedance="~50Ω (varies w/ angle)",
        atu_needed="Recommended",
        match_note="Direct 50Ω coax often works. 1:1 current balun at the high feedpoint improves results.",
        field_notes="""Half-Wave Sloper – Wire slopes from high anchor to low stake.
High end at apex (tree/mast), low end tied off near ground.
DX emphasis: Low-angle radiation toward direction wire slopes away from.
Typically 30–45° slope from horizontal for best results.
Quick POTA/SOTA deploy – one high tie, one stake. Fast and effective.""",
        dimensions_formula=sloper_dims
    )

    # FAN DIPOLE
    def fan_dims(f):
        bands = [
            ("80m", 3.700),
            ("40m", 7.074),
            ("20m", 14.225),
            ("15m", 21.300),
            ("10m", 28.400),
        ]
        return [
            (f"{name} LEG", 234 / freq, "each side · trim 2-4%")
            for name, freq in bands
        ]

    fan = AntennaTypeSpec(
        id="fan",
        name="Fan\nDipole",
        formula_ft="468 / f(MHz) per band",
        formula_m="142.65 / f(MHz) per band",
        match_type="1:1 Current Balun",
        match_ratio="1:1",
        match_impedance="~50Ω at resonance",
        atu_needed="Optional",
        match_note="Single 1:1 current balun feeds all legs from one feedpoint. Each leg pair resonates on its own band.",
        field_notes="""Fan Dipole – Multiple dipoles from one feedpoint. Multiband, no ATU.
Each band gets its own pair of legs, all sharing one balun and feedline.
REQUIRES FIELD TUNING – wire coupling between legs shifts resonance.
Start 2–4% longer than calculated, trim to resonance with NanoVNA.
Spread legs minimum 45° apart to reduce inter-element coupling.""",
        dimensions_formula=fan_dims
    )

    # OCFD (OFF-CENTER FED DIPOLE)
    def ocfd_dims(f):
        total = 468 / f
        long_leg = total * (2/3)
        short_leg = total * (1/3)
        return [
            ("LONG LEG (2/3)", long_leg, "2/3 of total"),
            ("SHORT LEG (1/3)", short_leg, "feed between these"),
        ]

    ocfd = AntennaTypeSpec(
        id="ocfd",
        name="OCFD\nOff-Ctr",
        formula_ft="468 / f(MHz)",
        formula_m="142.65 / f(MHz)",
        match_type="4:1 or 6:1 Current Balun",
        match_ratio="4:1 / 6:1",
        match_impedance="~200Ω at 1/3 point",
        atu_needed="Optional",
        match_note="Feed at ~1/3 point raises feedpoint impedance to ~200Ω. 4:1 balun brings it to ~50Ω.",
        field_notes="""Off-Center Fed Dipole (OCFD / Windom) – Multiband powerhouse.
Same total length as dipole but fed at ~1/3 point instead of center.
Multiband without ATU on fundamental + harmonic frequencies.
Example: 40m OCFD works on 40m, 20m, 15m, 10m – 4 bands, one wire!
Excellent POTA/SOTA antenna – one wire, multiple bands, low complexity.""",
        dimensions_formula=ocfd_dims
    )

    # DOUBLE BAZOOKA (COAXIAL DIPOLE)
    def bazooka_dims(f):
        total = 468 / f
        half = total / 2
        coax_vf = 0.66  # RG-58/RG-8X typical VF
        coax_sec = half * coax_vf
        wire_ext = half - coax_sec
        return [
            ("COAX SECTION (EACH)", coax_sec, "RG-58 per leg (VF 0.66)"),
            ("WIRE EXT (EACH)", wire_ext, "wire tip per leg"),
        ]

    bazooka = AntennaTypeSpec(
        id="bazooka",
        name="Dbl\nBazooka",
        formula_ft="468 / f(MHz)",
        formula_m="142.65 / f(MHz)",
        match_type="Direct Feed – No Balun",
        match_ratio="N/A",
        match_impedance="~50Ω broadband",
        atu_needed="No",
        match_note="The coax shield forms the center section – acts as its own choke/balun. Direct 50Ω feed at center.",
        field_notes="""Double Bazooka (Coaxial Dipole) – Broad bandwidth dipole.
Center section = coax (RG-58/RG-8X, VF–0.66). Wire extensions on each end.
No balun needed – coax shield acts as its own choke.
Wider SWR bandwidth than standard dipole – stays under 2:1 across full band.
Great for SSB phone use – less retuning when moving across band.""",
        dimensions_formula=bazooka_dims
    )

    # J-POLE / ZEPP
    def jpole_dims(f):
        half = 468 / f
        qtr = 234 / f
        return [
            ("RADIATOR (½λ)", half, "upper element"),
            ("MATCH STUB (¼λ)", qtr, "lower stub – bare copper"),
        ]

    jpole = AntennaTypeSpec(
        id="zepp",
        name="Doublet\nJ-Pole",
        formula_ft="468 / f(MHz) + 234 / f(MHz)",
        formula_m="142.65 / f(MHz) + 71.3 / f(MHz)",
        match_type="Stub Match – No Transformer",
        match_ratio="N/A",
        match_impedance="50Ω via ¼λ stub",
        atu_needed="No",
        match_note="J-Pole is self-matching via the quarter-wave stub – no balun or transformer needed.",
        field_notes="""J-Pole / Zepp – ½λ radiator + ¼λ matching stub. No radials needed.
Total wire: ¾λ. Feed with 50Ω coax at stub tap junction.
Excellent for VHF/UHF field deploy – 2m and 70cm.
Can be made from 300Ω twin-lead or ladder line for 2m.
Hang vertically from top – omnidirectional vertical pattern.""",
        dimensions_formula=jpole_dims
    )

    return [dipole, invv, qwave, jungle_gp, loop, delta, efhw, random, sloper, fan, ocfd, bazooka, jpole]


ANTENNA_TYPES = create_antenna_specs()

# Helper to find antenna by ID
def get_antenna_by_id(antenna_id: str) -> Optional[AntennaTypeSpec]:
    """Get antenna spec by ID."""
    for ant in ANTENNA_TYPES:
        if ant.id == antenna_id:
            return ant
    return None
