# Ktavik

Reading Paleo-Hebrew inscriptions from photographs — an OCR system for the ancient
Hebrew script, and the Android application that puts it in your hand at the dig site.

> **Status:** Phase 0 of 6. The engineering foundation is in place; no recognition model
> exists yet. See [Status](#status) for exactly what runs today.

---

## The problem

Paleo-Hebrew is the script the Hebrew Bible was originally written in — the alphabet of
the Siloam inscription, the Arad ostraca and the Lachish letters, in use until roughly
the sixth century BCE. It is not a different language. It is the same Hebrew in a
different alphabet, and modern readers cannot read it because they cannot read the
letterforms.

Recognising it from a photograph is hard for reasons that have nothing to do with
language:

- Inscriptions survive on broken pottery, worn stone and faded papyrus. Strokes are
  eroded, cracked, or lost entirely.
- Spacing is irregular and glyph boundaries are frequently absent, so the line cannot
  simply be cut into letters and classified one at a time.
- **No labelled dataset exists.** The entire known corpus is a few thousand items, most
  of them a handful of words. Ordinary supervised training is not an option.

## What is actually hard here — and what is not

The pipeline splits into three stages of wildly different difficulty. Being precise
about this matters, because the project is easy to oversell:

| Stage | Difficulty | How it is solved |
|---|---|---|
| **Recognition** — image to glyph sequence | **Very hard** | Computer vision, deep learning |
| Transliteration — Paleo to modern square script | Trivial | A 22-to-22 lookup table |
| Translation — Hebrew to English | Largely solved | Existing NMT / LLM APIs |

Roughly ninety percent of the engineering lives in the first row. Ktavik is a computer
vision project that ends in a translation, not a translation system.

## The approach

Since no labelled corpus exists, **the synthetic data generator is the centre of the
project**, not a preprocessing step. It renders public-domain Hebrew text in ancient
scripts, perturbs every glyph to imitate a human hand, and applies a photorealistic
degradation pipeline — ceramic and stone substrates, ink fading, erosion, cracks,
lighting — so that the output resembles a field photograph rather than a clean render.
Every image is generated from a known string, so labels are exact and free.

The methodological blueprint is
[Deep Aramaic](https://journals.plos.org/plosone/article?id=10.1371%2Fjournal.pone.0299297)
(PLOS One, 2024), which reached 95% on real eighth-century BCE inscriptions using
250k synthetic glyph images. Ktavik extends it in four directions:

- **line-level** end-to-end recognition rather than isolated glyph classification
- **real field photographs** rather than clean white-on-black renders
- **a diverse evaluation set** across multiple inscriptions rather than one
- **on-device deployment with a continuous improvement loop** rather than a model in a lab

That last point is the one that matters most. Accuracy is a number; the system around
the model — data versioning, experiment tracking, an evaluation gate in CI, retraining
driven by user corrections — is the engineering.

## Status

Honest accounting of what exists today.

| | |
|---|---|
| ✅ **Phase 0 — foundations** | Reproducible environment, quality gates, CI, branch protection, first ADRs |
| ⬜ Phase 1 — synthetic data generator | |
| ⬜ Phase 2 — glyph classifier + real evaluation set | |
| ⬜ Phase 2.5 — vertical skeleton, first end-to-end demo | |
| ⬜ Phase 3 — line-level detection and recognition | |
| ⬜ Phase 4 — inference service and MLOps | |
| ⬜ Phase 5 — Android application | |
| ⬜ Phase 6 — active learning loop and release | |

**What runs today:** a uv workspace with one member package, a reproducible environment
pinned by `uv.lock`, ruff and mypy in strict mode, pytest, pre-commit hooks across three
git stages, and a CI workflow that gates every pull request. There is no model yet, and
no accuracy to report.

## Architecture

```
Android app (Kotlin · Compose · CameraX)
  ├── fast path:     on-device LiteRT, detector + small CRNN, works offline
  ├── accurate path: cloud, full model + LLM translation
  └── user correction UI ──┐
                           ▼
Inference service (FastAPI · ONNX Runtime · Docker)
  detection → recognition → transliteration → translation
                           │ corrections + uncertainty samples
                           ▼
Active learning loop
  labeling queue → retrain → eval gate → canary → deploy
                           │
                           ▼
Training pipeline (PyTorch) ← synthetic data generator
  MLflow · DVC · model registry
```

### Repository layout

```
packages/synth/      synthetic data generator
packages/models/     training, evaluation, ONNX export     (Phase 2)
packages/api/        inference service                      (Phase 4)
packages/pipeline/   active-learning orchestration          (Phase 6)
packages/android/    the application                        (Phase 5)
docs/adr/            architecture decision records
```

## Running it

Requires [uv](https://docs.astral.sh/uv/). Python is installed and pinned automatically.

```bash
git clone https://github.com/Avi-Kohen/Ktavik.git
cd Ktavik
uv sync
```

That is the whole setup. To run the checks:

```bash
uv run ruff check .
uv run mypy
uv run pytest
```

To install the git hooks, once per clone:

```bash
uv run pre-commit install
```

## Decisions

Significant decisions are recorded as ADRs — context, decision, alternatives considered,
and consequences including the costs.

- [ADR-0001 — Monorepo with a uv workspace](docs/adr/0001-monorepo-with-uv-workspace.md)
- [ADR-0002 — CRNN + CTC for recognition, before TrOCR](docs/adr/0002-crnn-ctc-before-trocr.md)

## Roadmap

The next milestone is the **synthetic data generator** (Phase 1), followed by a glyph
classifier and a real evaluation set built from published photographs of the Arad
ostraca, the Siloam inscription, the Gezer calendar and the Lachish letters.

Phase 2 also measures the incumbents: Tesseract and Google Vision are run against the
same evaluation set and their error rates recorded. No off-the-shelf Paleo-Hebrew model
exists — available Hebrew models target the modern square script, a different sign
system — and quantifying that gap is what turns this from an exercise into a
demonstrated need.

The first thing you will be able to run end to end is the
[vertical skeleton](#status) at Phase 2.5: photograph a glyph, get a transliteration and
a translation, on a real device.

## References

- [Deep Aramaic — PLOS One, 2024](https://journals.plos.org/plosone/article?id=10.1371%2Fjournal.pone.0299297) · [arXiv](https://arxiv.org/abs/2310.07310)
- [A Review of Computational Approaches to Epigraphy](https://arxiv.org/pdf/2406.06570)
- [InscriptiFact, USC](http://www.inscriptifact.com/aboutus/index.shtml) — image archive
- [Culmus Ancient Semitic fonts](https://culmus.sourceforge.io/ancient/index.html)

## License

Apache 2.0. See [LICENSE](LICENSE).
