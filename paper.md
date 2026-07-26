---
title: "ToothNotation: a verified library for converting between dental tooth-numbering systems"
tags:
  - dentistry
  - dental informatics
  - tooth numbering
  - FDI
  - Python
authors:
  - name: Hezarani
    affiliation: 1
affiliations:
  - name: "Independent researcher"
    index: 1
date: 10 June 2026
bibliography: paper.bib
---

# Summary

Teeth are identified by several mutually incompatible numbering systems. The
*Universal Numbering System* (teeth 1–32, primary teeth A–T) predominates in the
United States; the *FDI two-digit notation* (ISO 3950), in which the first digit
encodes the quadrant and the second the position from the midline, is used through
most of the rest of the world; and the *Palmer (Zsigmondy-Palmer) notation*, a
quadrant symbol paired with a position number or letter, remains common in clinical
charting and orthodontics. Any software, dataset, or teaching resource that records
dental findings must translate between these systems, and these translations are a
recurring source of subtle, hard-to-detect errors.

`ToothNotation` is a small, dependency-free library that performs these conversions
using the FDI code as a single canonical representation: every input is parsed to an
FDI code, and every output is derived from it. This avoids the combinatorial set of
pairwise mappings that invites inconsistency, and it makes correctness checkable. The
package additionally exposes per-tooth clinical metadata (quadrant, arch, side,
dentition, and tooth type) and ships with a command-line interface and a
self-contained interactive odontogram component for the web.

# Statement of need

Tooth-numbering conversion is repeatedly re-implemented in dental research code,
practice-management integrations, and educational tools, frequently with off-by-one
errors or inverted quadrants that are easy to introduce and easy to miss. There is
no widely used, openly licensed, and explicitly tested reference implementation that
covers all three major systems for both the permanent and primary dentitions.

`ToothNotation` addresses this gap. Its correctness is established by an exhaustive
property test: each of the 52 teeth (32 permanent, 20 primary) is converted from FDI
to every supported system and back, and the result must equal the original. These
round-trip tests, together with hand-verified landmark anchors drawn from ISO 3950
and American Dental Association references, make the mapping auditable rather than
asserted. The library is intended as reusable infrastructure for dental-informatics
software and for education, and as a dependable conversion layer beneath
higher-level clinical and research tools.

# Functionality

- Conversion among FDI (ISO 3950), Universal, and Palmer notations for permanent and
  primary teeth.
- Automatic detection of the input notation where unambiguous.
- A `Tooth` value object carrying canonical FDI plus derived metadata.
- A command-line interface (`convert`, `info`, `chart`).
- A self-contained, accessible React odontogram for display and live conversion.

# Acknowledgements

The author thanks the maintainers of the open dental-imaging datasets whose
documentation informed the metadata conventions used here.

# References
