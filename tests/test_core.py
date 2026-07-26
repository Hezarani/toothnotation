"""Tests for toothnotation.

Two kinds of checks:

1. **Landmark anchors** -- a handful of teeth whose code in each system is
   independently known (verified against ISO 3950 and ADA references). If the
   mapping logic is wrong, these break.
2. **Exhaustive round-trips** -- for every one of the 52 teeth, converting
   FDI -> system -> FDI must return the original. This catches any off-by-one or
   inverted-quadrant error across the whole dentition, not just the anchors.
"""

import pytest

from toothnotation import (
    Tooth,
    all_teeth,
    convert,
    detect_system,
    parse,
)


# --- counts -------------------------------------------------------------------
def test_tooth_counts():
    assert len(all_teeth("permanent")) == 32
    assert len(all_teeth("primary")) == 20
    assert len(all_teeth()) == 52


# --- landmark anchors: FDI <-> Universal (permanent) --------------------------
# (FDI, Universal) pairs, each verified by hand.
PERMANENT_FDI_UNIVERSAL = [
    ("18", "1"),    # upper right third molar
    ("11", "8"),    # upper right central incisor
    ("21", "9"),    # upper left central incisor
    ("28", "16"),   # upper left third molar
    ("38", "17"),   # lower left third molar
    ("31", "24"),   # lower left central incisor
    ("41", "25"),   # lower right central incisor
    ("48", "32"),   # lower right third molar
    ("14", "5"),    # upper right first premolar
    ("36", "19"),   # lower left first molar
    ("46", "30"),   # lower right first molar
]


@pytest.mark.parametrize("fdi,uni", PERMANENT_FDI_UNIVERSAL)
def test_permanent_fdi_to_universal(fdi, uni):
    assert convert(fdi, "fdi", "universal") == uni


@pytest.mark.parametrize("fdi,uni", PERMANENT_FDI_UNIVERSAL)
def test_permanent_universal_to_fdi(fdi, uni):
    assert convert(uni, "universal", "fdi") == fdi


# --- landmark anchors: FDI <-> Universal (primary) ----------------------------
PRIMARY_FDI_UNIVERSAL = [
    ("55", "A"),    # upper right second primary molar
    ("51", "E"),    # upper right primary central incisor
    ("61", "F"),    # upper left primary central incisor
    ("65", "J"),    # upper left second primary molar
    ("75", "K"),    # lower left second primary molar
    ("71", "O"),    # lower left primary central incisor
    ("81", "P"),    # lower right primary central incisor
    ("85", "T"),    # lower right second primary molar
]


@pytest.mark.parametrize("fdi,uni", PRIMARY_FDI_UNIVERSAL)
def test_primary_fdi_to_universal(fdi, uni):
    assert convert(fdi, "fdi", "universal") == uni


@pytest.mark.parametrize("fdi,uni", PRIMARY_FDI_UNIVERSAL)
def test_primary_universal_to_fdi(fdi, uni):
    assert convert(uni, "universal", "fdi") == fdi


# --- landmark anchors: FDI <-> Palmer -----------------------------------------
PALMER_PAIRS = [
    ("18", "UR8"),
    ("11", "UR1"),
    ("21", "UL1"),
    ("38", "LL8"),
    ("41", "LR1"),
    ("36", "LL6"),
    ("55", "URE"),   # primary: position 5 -> letter E
    ("51", "URA"),   # primary: position 1 -> letter A
    ("85", "LRE"),
]


@pytest.mark.parametrize("fdi,palmer", PALMER_PAIRS)
def test_fdi_to_palmer(fdi, palmer):
    assert convert(fdi, "fdi", "palmer") == palmer


@pytest.mark.parametrize("fdi,palmer", PALMER_PAIRS)
def test_palmer_to_fdi(fdi, palmer):
    assert convert(palmer, "palmer", "fdi") == fdi


# --- exhaustive round-trips ---------------------------------------------------
@pytest.mark.parametrize("tooth", all_teeth())
@pytest.mark.parametrize("system", ["universal", "palmer", "fdi"])
def test_roundtrip_fdi_through_every_system(tooth, system):
    rendered = tooth.to(system)
    back = convert(rendered, system, "fdi")
    assert back == tooth.fdi_str, (
        f"{tooth.fdi} -> {system} ({rendered}) -> {back} did not round-trip"
    )


@pytest.mark.parametrize("tooth", all_teeth())
def test_universal_codes_are_unique_and_complete(tooth):
    # Every tooth produces a distinct Universal code; collected separately below.
    assert tooth.universal


def test_universal_permanent_codes_are_1_to_32():
    codes = {int(t.universal) for t in all_teeth("permanent")}
    assert codes == set(range(1, 33))


def test_universal_primary_codes_are_A_to_T():
    codes = {t.universal for t in all_teeth("primary")}
    assert codes == {chr(c) for c in range(ord("A"), ord("T") + 1)}


# --- metadata -----------------------------------------------------------------
def test_metadata_lower_left_first_molar():
    t = parse("36")
    assert t.name == "lower left first molar"
    assert t.arch == "lower"
    assert t.side == "left"
    assert t.quadrant == "LL"
    assert t.tooth_type == "first molar"
    assert t.dentition == "permanent"
    assert t.position == 6


def test_metadata_upper_right_central_incisor():
    t = parse("11")
    assert t.name == "upper right central incisor"
    assert t.arch == "upper"
    assert t.side == "right"
    assert t.dentition == "permanent"


def test_metadata_primary_tooth():
    t = parse("75")
    assert t.dentition == "primary"
    assert t.tooth_type == "second primary molar"
    assert t.name == "lower left second primary molar"


# --- auto-detection -----------------------------------------------------------
def test_detect_system():
    assert detect_system("36") == "fdi"     # valid two-digit FDI
    assert detect_system("19") == "universal"  # not a valid FDI code -> Universal
    assert detect_system("UR6") == "palmer"
    assert detect_system("A") == "universal"
    assert detect_system("ul b") == "palmer"


def test_parse_auto_detect_matches_explicit():
    assert parse("36").fdi == parse("36", "fdi").fdi
    assert parse("UR6").fdi == 16
    assert parse("19").fdi == 36  # Universal 19 == FDI 36


# --- cross-system convenience -------------------------------------------------
def test_universal_to_palmer_directly():
    # Universal 19 is the lower-left first molar -> Palmer LL6.
    assert convert("19", "universal", "palmer") == "LL6"


def test_palmer_to_universal_directly():
    assert convert("LL6", "palmer", "universal") == "19"


# --- error handling -----------------------------------------------------------
@pytest.mark.parametrize("bad", ["19", "00", "49", "56", "99", "9"])
def test_invalid_fdi_rejected(bad):
    # None of these are valid FDI codes (19=no tooth 9; 49/56 bad quadrant/pos).
    with pytest.raises(ValueError):
        convert(bad, "fdi", "universal")


@pytest.mark.parametrize("bad", ["0", "33", "99", "Z", "AA"])
def test_invalid_universal_rejected(bad):
    with pytest.raises(ValueError):
        convert(bad, "universal", "fdi")


@pytest.mark.parametrize("bad", ["XR6", "UR9", "URZ", "UR", "6"])
def test_invalid_palmer_rejected(bad):
    with pytest.raises(ValueError):
        convert(bad, "palmer", "fdi")


def test_invalid_system_name_rejected():
    with pytest.raises(ValueError):
        convert("11", "fdi", "notasystem")


def test_tooth_constructor_validates():
    with pytest.raises(ValueError):
        Tooth(99)


def test_detect_empty_string_raises():
    with pytest.raises(ValueError):
        detect_system("   ")
