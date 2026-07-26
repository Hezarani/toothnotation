"""Core tooth model and notation conversion.

Three notation systems are supported:

- **FDI** (ISO 3950, "World Dental Federation"): two-digit code. First digit is the
  quadrant, second digit is the tooth position counting from the midline.
  Permanent quadrants: 1=upper-right, 2=upper-left, 3=lower-left, 4=lower-right.
  Primary quadrants:   5=upper-right, 6=upper-left, 7=lower-left, 8=lower-right.
- **Universal** (American): permanent teeth 1-32, primary teeth A-T.
- **Palmer** (Zsigmondy-Palmer): a quadrant + a position symbol (1-8 permanent,
  A-E primary). The true Palmer form is a graphical bracket; in text we use an
  unambiguous quadrant abbreviation (UR/UL/LL/LR) plus the symbol, e.g. ``UR6``.

FDI is used as the canonical internal representation. Everything parses to an FDI
code and every output is derived from it, so there is exactly one source of truth.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

Dentition = Literal["permanent", "primary"]
Quadrant = Literal["UR", "UL", "LL", "LR"]
Arch = Literal["upper", "lower"]
Side = Literal["right", "left"]
ToothType = Literal[
    "central incisor",
    "lateral incisor",
    "canine",
    "first premolar",
    "second premolar",
    "first molar",
    "second molar",
    "third molar",
    "first primary molar",
    "second primary molar",
]

# FDI first digit -> quadrant code, by dentition.
_FDI_QUADRANT = {
    1: "UR", 2: "UL", 3: "LL", 4: "LR",   # permanent
    5: "UR", 6: "UL", 7: "LL", 8: "LR",   # primary
}
_FDI_DENTITION = {
    1: "permanent", 2: "permanent", 3: "permanent", 4: "permanent",
    5: "primary", 6: "primary", 7: "primary", 8: "primary",
}
_QUADRANT_ARCH = {"UR": "upper", "UL": "upper", "LL": "lower", "LR": "lower"}
_QUADRANT_SIDE = {"UR": "right", "UL": "left", "LL": "left", "LR": "right"}

# Position (1-8 permanent, 1-5 primary) -> tooth type. Position counts from midline.
_PERMANENT_TYPE = {
    1: "central incisor", 2: "lateral incisor", 3: "canine",
    4: "first premolar", 5: "second premolar",
    6: "first molar", 7: "second molar", 8: "third molar",
}
_PRIMARY_TYPE = {
    1: "central incisor", 2: "lateral incisor", 3: "canine",
    4: "first primary molar", 5: "second primary molar",
}


@dataclass(frozen=True)
class Tooth:
    """A single tooth, identified canonically by its FDI code.

    Attributes are derived once at construction so a Tooth can be rendered in any
    notation and also carries useful clinical metadata (arch, side, type, name).
    """

    fdi: int

    def __post_init__(self) -> None:
        if self.fdi not in _ALL_FDI:
            raise ValueError(
                f"{self.fdi!r} is not a valid FDI tooth code. "
                "Expected a two-digit code such as 11-48 (permanent) or 51-85 (primary)."
            )

    # --- canonical components -------------------------------------------------
    @property
    def quadrant_digit(self) -> int:
        return self.fdi // 10

    @property
    def position(self) -> int:
        """Tooth position counting from the midline (1 = central incisor)."""
        return self.fdi % 10

    @property
    def dentition(self) -> Dentition:
        return _FDI_DENTITION[self.quadrant_digit]  # type: ignore[return-value]

    @property
    def quadrant(self) -> Quadrant:
        return _FDI_QUADRANT[self.quadrant_digit]  # type: ignore[return-value]

    @property
    def arch(self) -> Arch:
        return _QUADRANT_ARCH[self.quadrant]  # type: ignore[return-value]

    @property
    def side(self) -> Side:
        return _QUADRANT_SIDE[self.quadrant]  # type: ignore[return-value]

    @property
    def tooth_type(self) -> ToothType:
        table = _PERMANENT_TYPE if self.dentition == "permanent" else _PRIMARY_TYPE
        return table[self.position]  # type: ignore[return-value]

    @property
    def name(self) -> str:
        """Human-readable name, e.g. 'upper right first molar'."""
        return f"{self.arch} {self.side} {self.tooth_type}"

    # --- notation renderings --------------------------------------------------
    @property
    def fdi_str(self) -> str:
        return str(self.fdi)

    @property
    def universal(self) -> str:
        return _fdi_to_universal(self.fdi)

    @property
    def palmer(self) -> "PalmerTooth":
        return _fdi_to_palmer(self.fdi)

    def to(self, system: str) -> str:
        """Render this tooth in ``system`` ('fdi', 'universal', or 'palmer')."""
        s = system.strip().lower()
        if s == "fdi":
            return self.fdi_str
        if s == "universal":
            return self.universal
        if s == "palmer":
            return str(self.palmer)
        raise ValueError(
            f"Unknown notation system {system!r}. Use 'fdi', 'universal', or 'palmer'."
        )

    def __str__(self) -> str:
        return self.fdi_str


@dataclass(frozen=True)
class PalmerTooth:
    """Palmer notation value: a quadrant plus a position symbol.

    ``str()`` yields the text form (e.g. ``UR6`` or ``LL E``). The graphical
    bracket form is rendered by the charting component, not in text.
    """

    quadrant: Quadrant
    symbol: str  # '1'..'8' for permanent, 'A'..'E' for primary

    def __str__(self) -> str:
        return f"{self.quadrant}{self.symbol}"


# --- build the set of valid FDI codes -----------------------------------------
def _build_all_fdi() -> frozenset[int]:
    codes: set[int] = set()
    for q in (1, 2, 3, 4):
        for p in range(1, 9):
            codes.add(q * 10 + p)
    for q in (5, 6, 7, 8):
        for p in range(1, 6):
            codes.add(q * 10 + p)
    return frozenset(codes)


_ALL_FDI = _build_all_fdi()


# --- FDI <-> Universal ---------------------------------------------------------
# Permanent: derived from the quadrant.
#   Q1 (UR): U = 9  - position     (18->1 ... 11->8)
#   Q2 (UL): U = 8  + position     (21->9 ... 28->16)
#   Q3 (LL): U = 25 - position     (38->17 ... 31->24)
#   Q4 (LR): U = 24 + position     (41->25 ... 48->32)
def _fdi_to_universal(fdi: int) -> str:
    q, p = divmod(fdi, 10)
    if q == 1:
        return str(9 - p)
    if q == 2:
        return str(8 + p)
    if q == 3:
        return str(25 - p)
    if q == 4:
        return str(24 + p)
    # Primary: letters A-T. Index from 'A' by quadrant.
    #   Q5 (UR): idx = 5 - p     (51->E ... 55->A)
    #   Q6 (UL): idx = 4 + p     (61->F ... 65->J)
    #   Q7 (LL): idx = 15 - p    (71->O ... 75->K)
    #   Q8 (LR): idx = 14 + p    (81->P ... 85->T)
    idx = {5: 5 - p, 6: 4 + p, 7: 15 - p, 8: 14 + p}[q]
    return chr(ord("A") + idx)


def _universal_to_fdi(value: str) -> int:
    v = value.strip().upper()
    if v.isdigit():
        n = int(v)
        if not 1 <= n <= 32:
            raise ValueError(f"Universal tooth number {n} is out of range (1-32).")
        # Invert the permanent mappings above.
        if 1 <= n <= 8:
            return 10 + (9 - n)      # Q1
        if 9 <= n <= 16:
            return 20 + (n - 8)      # Q2
        if 17 <= n <= 24:
            return 30 + (25 - n)     # Q3
        return 40 + (n - 24)         # Q4 (25-32)
    if len(v) == 1 and "A" <= v <= "T":
        idx = ord(v) - ord("A")      # 0..19
        # Invert the primary mappings above.
        if 0 <= idx <= 4:            # A-E  -> Q5
            return 50 + (5 - idx)
        if 5 <= idx <= 9:            # F-J  -> Q6
            return 60 + (idx - 4)
        if 10 <= idx <= 14:          # K-O  -> Q7
            return 70 + (15 - idx)
        return 80 + (idx - 14)       # P-T  -> Q8
    raise ValueError(
        f"{value!r} is not a valid Universal code. Use 1-32 (permanent) or A-T (primary)."
    )


# --- FDI <-> Palmer ------------------------------------------------------------
# Palmer position number equals the FDI position for permanent teeth. Primary
# teeth use letters A-E by position (A=central ... E=second molar).
def _fdi_to_palmer(fdi: int) -> PalmerTooth:
    q, p = divmod(fdi, 10)
    quadrant = _FDI_QUADRANT[q]
    if _FDI_DENTITION[q] == "permanent":
        symbol = str(p)
    else:
        symbol = chr(ord("A") + (p - 1))
    return PalmerTooth(quadrant=quadrant, symbol=symbol)  # type: ignore[arg-type]


_QUADRANT_TO_FDI_TENS = {
    ("UR", "permanent"): 1, ("UL", "permanent"): 2,
    ("LL", "permanent"): 3, ("LR", "permanent"): 4,
    ("UR", "primary"): 5, ("UL", "primary"): 6,
    ("LL", "primary"): 7, ("LR", "primary"): 8,
}


def _palmer_to_fdi(value: str | PalmerTooth) -> int:
    if isinstance(value, PalmerTooth):
        quadrant, symbol = value.quadrant, value.symbol
    else:
        quadrant, symbol = _parse_palmer_str(value)
    symbol = symbol.strip().upper()
    if symbol.isdigit():
        p = int(symbol)
        if not 1 <= p <= 8:
            raise ValueError(f"Palmer permanent position {p} is out of range (1-8).")
        tens = _QUADRANT_TO_FDI_TENS[(quadrant, "permanent")]
        return tens * 10 + p
    if len(symbol) == 1 and "A" <= symbol <= "E":
        p = ord(symbol) - ord("A") + 1
        tens = _QUADRANT_TO_FDI_TENS[(quadrant, "primary")]
        return tens * 10 + p
    raise ValueError(
        f"{symbol!r} is not a valid Palmer symbol. Use 1-8 (permanent) or A-E (primary)."
    )


def _parse_palmer_str(value: str) -> tuple[str, str]:
    """Parse a text Palmer code like 'UR6', 'UL B', or 'lr8' into (quadrant, symbol)."""
    raw = value.strip().upper().replace(" ", "")
    if len(raw) < 3:
        raise ValueError(
            f"{value!r} is not a valid Palmer code. Expected a quadrant and a symbol, e.g. 'UR6'."
        )
    quadrant, symbol = raw[:2], raw[2:]
    if quadrant not in {"UR", "UL", "LL", "LR"}:
        raise ValueError(
            f"{quadrant!r} is not a valid Palmer quadrant. Use UR, UL, LL, or LR."
        )
    return quadrant, symbol
