# ToothNotation

**Convert between dental tooth-numbering systems — FDI (ISO 3950), Universal, and Palmer — with one source of truth and 293 verifying tests.**

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.21704141.svg)](https://doi.org/10.5281/zenodo.21704141)
[![PyPI](https://img.shields.io/pypi/v/toothnotation.svg?color=2c8c9c&label=PyPI)](https://pypi.org/project/toothnotation/)
[![License: MIT](https://img.shields.io/badge/License-MIT-informational.svg)](LICENSE)
[![Tests](https://img.shields.io/badge/tests-293%20passing-brightgreen.svg)](tests/)

Tooth numbering is a perennial source of error and re-implementation in dental
software: the US uses the **Universal** system (1–32, A–T), most of the world uses
**FDI / ISO 3950** (two-digit quadrant codes), and clinicians often chart in
**Palmer** notation. Every project that touches teeth ends up rewriting these
conversions, usually with subtle off-by-one and inverted-quadrant bugs.

ToothNotation does it once, correctly, with FDI as the canonical internal key — so
every conversion is derived from a single representation rather than a tangle of
pairwise lookup tables. It ships as a small dependency-free Python package, a CLI,
and an interactive React odontogram you can drop into a teaching site or chart UI.

```python
from toothnotation import convert, parse

convert("36", "fdi", "universal")   # "19"
convert("19", "universal", "fdi")    # "36"
convert("UR6", "palmer", "universal") # "3"

t = parse("36")          # auto-detects the system
t.name                   # "lower left first molar"
t.universal              # "19"
str(t.palmer)            # "LL6"
t.dentition, t.arch      # ("permanent", "lower")
```

## Why trust it

Tooth maps are easy to get wrong, so correctness is the whole point of the library:

- **FDI-canonical design.** Every system parses to an FDI code and every output is
  derived from it. There is exactly one source of truth, not six pairwise maps to
  keep in sync.
- **293 tests**, including **every one of the 52 teeth round-tripped through all
  three systems** (`FDI → system → FDI` must return the original). This catches any
  off-by-one or inverted quadrant across the whole dentition, not just spot checks.
- **Hand-verified anchors** against ISO 3950 and ADA references (e.g. FDI `11` =
  Universal `8` = Palmer `UR1`; FDI `48` = Universal `32`).

```
$ pytest -q
293 passed
```

## Install

```bash
pip install toothnotation
```

No runtime dependencies. Python 3.9+.

## Use it

### Python

```python
from toothnotation import convert, parse, all_teeth, detect_system

detect_system("19")          # "universal"  (not a valid FDI code)
detect_system("36")          # "fdi"
detect_system("UR6")         # "palmer"

[t.universal for t in all_teeth("primary")]   # ['A', 'B', ... 'T']

tooth = parse("65")
tooth.name                   # "upper left second primary molar"
tooth.tooth_type             # "second primary molar"
```

The `Tooth` object exposes `fdi`, `universal`, `palmer`, `name`, `quadrant`,
`arch`, `side`, `dentition`, `tooth_type`, and `position` (counting from the
midline), plus `.to("fdi" | "universal" | "palmer")`.

### Command line

```bash
toothnotation convert 36 fdi universal     # 19
toothnotation info UR6                       # full detail, auto-detected
toothnotation chart --system universal       # print the chart
```

### Interactive chart (React)

`toothchart.jsx` is a self-contained component — an anatomically arranged
odontogram that displays any of the three systems, lets you click a tooth for full
detail, and converts codes live. Palmer brackets are drawn the way they appear on a
paper chart (the quadrant corner is marked with real borders, not an approximated
glyph). The conversion logic is ported from the Python package and verified with
the same round-trip checks.

> Drop it into a teaching site, a charting UI, or a patient-education page.

## The three systems, briefly

| System | Permanent | Primary | Example (lower-left first molar) |
|---|---|---|---|
| **FDI** (ISO 3950) | `11`–`48` (quadrant + position) | `51`–`85` | `36` |
| **Universal** (US) | `1`–`32` | `A`–`T` | `19` |
| **Palmer** | quadrant + `1`–`8` | quadrant + `A`–`E` | `LL6` |

## References & prior work

**Standards and guidance**

- International Organization for Standardization (2016). *ISO 3950:2016 Dentistry — Designation system for teeth and areas of the oral cavity* (4th ed.). Geneva: ISO. <https://www.iso.org/standard/68292.html>
- American Dental Association (2022). *Universal Tooth Designation System — Value Set, Version 1*. Chicago: ADA. <https://www.ada.org/-/media/project/ada-organization/ada/ada-org/files/publications/cdt/ada_utds_value_set_v1_2022_aug.pdf>
- Leatherman, G. (1971). Two-digit system of designating teeth — FDI submission. *Australian Dental Journal* 16(6):394. [doi:10.1111/j.1834-7819.1971.tb03438.x](https://doi.org/10.1111/j.1834-7819.1971.tb03438.x)

**Evidence that motivated it**

- Peck, S. & Peck, L. (1993). A time for change of tooth numbering systems. *Journal of Dental Education* 57(8):643–647. [doi:10.1002/j.0022-0337.1993.57.8.tb02785.x](https://doi.org/10.1002/j.0022-0337.1993.57.8.tb02785.x)
- Türp, J.C. & Alt, K.W. (1995). Designating teeth: the advantages of the FDI's two-digit system. *Quintessence International* 26(7):501–504. [PMID 8935036](https://pubmed.ncbi.nlm.nih.gov/8935036/) (no DOI)
- Ferguson, J.W. (2005). The Palmer notation system and its use with personal computer applications. *British Dental Journal* 198(9):551–553. [doi:10.1038/sj.bdj.4812303](https://doi.org/10.1038/sj.bdj.4812303)

## Contributing

Issues and PRs welcome — especially additional reference anchors, alternative
Palmer text conventions, and bindings in other languages. Every conversion change
must keep the exhaustive round-trip tests green.

## Citing

If this is useful in research or software, please cite it (see `CITATION.cff`). A
short software paper is in `paper.md`.

## License

MIT — see `LICENSE`.
