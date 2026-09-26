# Ktavik

An open-source OCR/HTR system for **Paleo-Hebrew** — the alphabet of the Siloam
inscription, the Arad ostraca and the Lachish letters — and the Android application
that reads one from a photograph at the dig site.

This site is the engineering record: the decisions, the alternatives that were
rejected, and the costs each choice carries. The
[README](https://github.com/Avi-Kohen/Ktavik#readme) is the short version.

## What is hard here, and what is not

The pipeline splits into three stages of wildly different difficulty. Being precise
about this matters, because the project is easy to oversell.

| Stage | Difficulty | How it is solved |
|---|---|---|
| **Recognition** — image to glyph sequence | **Very hard** | Computer vision, deep learning |
| Transliteration — Paleo to modern square script | Trivial | A 22-to-22 lookup table |
| Translation — Hebrew to English | Largely solved | Existing NMT / LLM APIs |

Roughly ninety percent of the engineering lives in the first row. Ktavik is a
computer vision project that ends in a translation, not a translation system.

## What exists today

**Phase 0 of 6 — the engineering foundation.** A reproducible `uv` workspace, strict
linting and type checking, tests, pre-commit hooks across three git stages, CI that
gates every pull request, and this documentation site.

There is no recognition model yet, and no accuracy to report.

The next milestone is the **synthetic data generator**. It is the centre of the
project rather than a preprocessing step: no labelled corpus of Paleo-Hebrew exists
at the scale supervised training requires — the entire known corpus is a few thousand
items, most of them a handful of words — so the training data has to be manufactured
and the labels derived from what was rendered.

## Decisions

Every significant choice is recorded as an ADR: context, decision, alternatives
considered, and consequences including what the decision costs.

- [ADR-0001 — Monorepo with a uv workspace](adr/0001-monorepo-with-uv-workspace.md)
- [ADR-0002 — CRNN + CTC for recognition, before TrOCR](adr/0002-crnn-ctc-before-trocr.md)
