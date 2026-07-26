"""toothnotation -- convert between dental tooth-numbering systems.

Quick start::

    from toothnotation import convert, parse

    convert("14", "fdi", "universal")   # -> "5"
    convert("19", "universal", "fdi")    # -> "36"
    convert("UR6", "palmer", "fdi")      # -> "16"

    t = parse("36")                      # auto-detects the system
    t.name                               # -> "lower left first molar"
    t.universal                          # -> "19"
    str(t.palmer)                        # -> "LL6"
"""

from __future__ import annotations

from .core import (
    PalmerTooth,
    Tooth,
    _fdi_to_palmer,
    _fdi_to_universal,
    _palmer_to_fdi,
    _parse_palmer_str,
    _universal_to_fdi,
    _ALL_FDI,
)

__all__ = [
    "Tooth",
    "PalmerTooth",
    "parse",
    "convert",
    "detect_system",
    "all_teeth",
    "SYSTEMS",
]

__version__ = "0.1.0"

SYSTEMS = ("fdi", "universal", "palmer")


def detect_system(value: str) -> str:
    """Best-effort detection of which notation ``value`` is written in.

    Detection is unambiguous except where systems share a glyph: a bare letter
    'A'-'E' is valid as both Universal (primary) and... no other system, so it is
    reported as 'universal'. A two-letter quadrant prefix means Palmer. A bare
    1-8 / 1-32 number or two-digit FDI code is resolved by range.

    Raises ``ValueError`` if nothing matches.
    """
    v = value.strip().upper().replace(" ", "")
    if not v:
        raise ValueError("Cannot detect the notation of an empty string.")

    # Palmer: starts with a quadrant code.
    if v[:2] in {"UR", "UL", "LL", "LR"}:
        return "palmer"

    # Single letter A-T -> Universal primary.
    if len(v) == 1 and "A" <= v <= "T":
        return "universal"

    if v.isdigit():
        n = int(v)
        # Two-digit values whose first digit is a valid FDI quadrant (1-8) and
        # second digit a valid position are FDI codes.
        if int(v) in _ALL_FDI and len(v) == 2:
            return "fdi"
        # Otherwise a 1-32 value is Universal.
        if 1 <= n <= 32:
            return "universal"

    raise ValueError(
        f"Could not detect the notation system of {value!r}. "
        "Pass the system explicitly to convert()."
    )


def _to_fdi(value: str, system: str) -> int:
    s = system.strip().lower()
    if s == "fdi":
        v = value.strip()
        if not v.isdigit() or int(v) not in _ALL_FDI:
            raise ValueError(
                f"{value!r} is not a valid FDI code (expected 11-48 or 51-85)."
            )
        return int(v)
    if s == "universal":
        return _universal_to_fdi(value)
    if s == "palmer":
        return _palmer_to_fdi(value)
    raise ValueError(f"Unknown notation system {system!r}. Use one of {SYSTEMS}.")


def parse(value: str, system: str | None = None) -> Tooth:
    """Parse ``value`` into a :class:`Tooth`.

    If ``system`` is omitted it is auto-detected with :func:`detect_system`.
    """
    if system is None:
        system = detect_system(value)
    return Tooth(_to_fdi(value, system))


def convert(value: str, from_system: str, to_system: str) -> str:
    """Convert ``value`` from ``from_system`` to ``to_system``.

    Both systems are one of 'fdi', 'universal', 'palmer'. Returns the rendered
    string in the target system.
    """
    tooth = Tooth(_to_fdi(value, from_system))
    return tooth.to(to_system)


def all_teeth(dentition: str | None = None) -> list[Tooth]:
    """Return every valid tooth.

    ``dentition`` filters to 'permanent' (32 teeth) or 'primary' (20 teeth);
    omit it to get all 52.
    """
    teeth = [Tooth(code) for code in sorted(_ALL_FDI)]
    if dentition is None:
        return teeth
    d = dentition.strip().lower()
    if d not in {"permanent", "primary"}:
        raise ValueError("dentition must be 'permanent', 'primary', or None.")
    return [t for t in teeth if t.dentition == d]
