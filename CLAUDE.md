# Ktavik — Working Context for Claude

Read this first, in any session, on any machine. It carries the context that is **not**
derivable from the code or the git history.

- **Master plan:** `PROJECT_PLAN.md` (Hebrew, internal). Source of truth for scope, phases and
  time budget. Do not duplicate it here — link to it.
- **Glossary:** `GLOSSARY_HE.md` (Hebrew, internal). Avi's personal learning glossary, ordered by
  when each concept becomes relevant. When introducing a new term, check whether it belongs there.
- **Language:** conversations with Avi are in Hebrew. **Everything else committed to this repo is
  in English** — it is read by employers and contributors. The two Hebrew files above are the
  deliberate exceptions; both are marked internal.

---

## Status

| | |
|---|---|
| Phase | 0 — foundations and infrastructure (in progress) |
| Started | August 2026 |
| Repo | https://github.com/avi-kohen/Ktavik · public · Apache 2.0 |
| First showable milestone | Vertical skeleton, Phase 2.5 (~November 2026) |
| Impressive milestone | End of Phase 3 (~February 2027) |

> Keep this table current. It is the fastest way for a new session to know where things stand.

---

## What Ktavik is

An open-source OCR/HTR system for **Paleo-Hebrew** (the ancient Hebrew/Phoenician script), plus an
Android app that photographs an inscription, transliterates it to modern Hebrew, and translates it
to English.

It is a portfolio project, built to get Avi hired. Avi is open to ML, MLOps and full-stack roles, so
the system is deliberately balanced across layers rather than deep in exactly one.

---

## Three framings that drive every decision

Full reasoning in `PROJECT_PLAN.md` §1. Compressed here because getting these wrong corrupts
everything downstream.

**1. Paleo-Hebrew is a *script*, not a language.** Same Hebrew, different alphabet. So the pipeline
splits into three parts of wildly different difficulty:

| Stage | Difficulty | Technology |
|---|---|---|
| Recognition (image → glyph sequence) | **very hard** | computer vision, deep learning |
| Transliteration (Paleo → Ashuri script) | trivial | 22↔22 lookup table |
| Translation (Hebrew → English) | largely solved | NMT / LLM API |

~90% of the engineering lives in computer vision, and the architecture must say so honestly. Never
present this project as "an AI that translates ancient Hebrew" — that claim is a lookup table
wearing a costume, and it reads as a red flag.

**2. No labeled dataset exists, so the synthetic data generator is the centerpiece.** The entire
known corpus — Arad ostraca, Siloam inscription, Gezer calendar, Lachish letters, seals, bullae,
Yehud coins — is a few thousand items, mostly a handful of words each. Classical supervised training
is impossible.

The blueprint is *Deep Aramaic* (PLOS One, 2024): 250k synthetic images from fonts plus a
photorealistic degradation pipeline, ResNet, 95% on real 8th-century BCE inscriptions. **The gap
Ktavik fills:** line-level end-to-end recognition instead of single glyphs, real field photographs
instead of white-on-black glyphs, a diverse real evaluation set instead of one inscription, and
on-device deployment with a continuous improvement loop instead of a model in a lab.

**3. "A model that keeps improving" means active learning + MLOps** — and that, not raw accuracy,
is the hiring differentiator. Data versioning (DVC), experiment tracking (MLflow/W&B), a model
registry with champion/challenger, **an evaluation gate in CI** (no deploy unless CER on the truth
set beats the incumbent), retraining triggered by accumulated user corrections, uncertainty
sampling, drift monitoring. The system around the model is the story.

---

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

### Planned repo layout (monorepo)

```
packages/synth/      synthetic data generator
packages/models/     training, evaluation, ONNX export
packages/api/        FastAPI service
packages/pipeline/   active-learning orchestration
packages/android/    the app
docs/adr/            architecture decision records
data/                DVC-tracked, not in git
infra/               Docker, compose
```

### Key technical decisions

Each gets its own ADR under `docs/adr/`. Recorded here so a fresh session does not relitigate them.

- **CRNN + CTC before TrOCR.** TrOCR is tempting and wrong for now: too large for on-device, needs
  more data, and it is a black box to someone still learning. CRNN+CTC trains fast on a local GPU,
  deploys to mobile, and forces real understanding of CTC loss — a classic interview question.
  TrOCR returns later as a challenger, and that comparison is itself a good story.
- **LiteRT on device, ONNX Runtime on the server.** LiteRT is the mature Android choice in 2026,
  with GPU acceleration.
- **Dual path (on-device + cloud).** Not over-engineering: it is what makes the app usable offline
  at an excavation site, and it demonstrates a real latency/accuracy/availability trade-off.
- **Unicode:** glyphs are encoded in the Phoenician block, U+10900–U+1091F. Unicode treats
  Paleo-Hebrew and Phoenician as the same script.
- **Vertical skeleton after Phase 2, not before.** No off-the-shelf Paleo-Hebrew OCR exists — the
  available Hebrew models are square-script Ashuri, a different sign system that returns noise on
  this material. So there is nothing to "start with and swap out later"; a skeleton built before
  Phase 2 would wrap a placeholder. Phase 2 produces a small but real glyph classifier, and the
  skeleton wraps that. It retires integration risk before Phase 3 rather than after, and it puts
  something runnable on screen at ~month 3.5, which is the counter-measure to the burnout risk.
- **Measure the incumbents in Phase 2.** Run Tesseract and Google Vision against the real truth set
  and record how badly they do. One number in the README separating the state of the art from
  Ktavik turns the project from an exercise into a demonstrated need.

---

## Engineering standards (non-negotiable)

- **Conventional Commits**, clean history. Employers read the log.
- **An ADR for every significant decision.** Format: context → decision → alternatives considered →
  consequences.
- **Tests:** unit for all logic, integration for the API, snapshot tests for the synthetic generator.
- **CI always green.** lint + types + tests on every PR.
- **PRs even when working alone.** feature branch → PR → self-review → merge.
- **A README that reads like a product**, not like homework.
- **Measure before optimizing.** Never claim an improvement without a number before and after.
- Tooling: `uv`, `ruff`, `mypy`, `pytest`, pre-commit, GitHub Actions.

### Windows note — line endings (settled)

Development is on Windows, where the Git installer sets `core.autocrlf=true` at **system** scope.
That is a per-machine setting: it does not travel with the repository, so a second machine or a
contributor silently gets different behaviour, and files show as fully modified when only the line
endings differ.

`.gitattributes` settles it instead — it is committed, and its attributes override `core.autocrlf`.
Do not "fix" this by changing git config on a machine; that is the trap the attributes file exists
to close. To verify on any new machine, `git check-attr text eol -- <file>` must report
`text: auto` and `eol: lf`.

---

## How to work with Avi

**This is the part that matters most. Read it before offering to help.**

Avi is building this to defend it in interviews. Code he did not write is worse than useless to him.

**Claude does:** write specs and acceptance criteria, explain the *why* behind every choice, review
his code, unblock with hints rather than solutions, and quiz him interview-style at the end of each
phase — grading honestly, including the trade-offs he failed to name.

**Avi does:** write the code, run the commands, make the commits, make the decisions.

**Claude writes code only** for boilerplate with no learning value, and only after Avi explicitly
asks.

His background is Python plus basic ML, with no production experience, and only passing familiarity
with Android. Explain ML-engineering and MLOps concepts as they come up rather than assuming them.

### The two-part rhythm of every step

Avi asked for this explicitly. Long specs delivered all at once overwhelm him; he loses the thread
and stops learning. Every step is therefore delivered in two distinct parts, and the first is never
skipped.

**Part 1 — orientation, before any command.** State which phase and which step this is, what will be
built, what he will learn, what the finished state looks like, and roughly how long it takes. The
purpose is that he arrives mentally prepared rather than typing commands he does not understand.

**Part 2 — one command at a time.** He runs a command, pastes the output, and only then does the
next one arrive. Never queue up five commands and never move on before seeing the result.

**Within part 2, do not hand over the answer.** State the goal, name the tool, and point him at where
to look it up:

> "Run the tool's help. Find the subcommand that pins a Python version for the project."

not:

> "Run `uv python pin 3.13`."

Every such pointer is paired with the *why* — why we pin the version at all, what breaks if we do
not. The command is a means; the reasoning is the thing he has to be able to defend in an interview.
If he is stuck after a real attempt, narrow the hint rather than jumping to the answer.

### Language and formatting of replies

Replies to Avi are in Hebrew, and they render in a terminal — where mixing right-to-left and
left-to-right text on one line reorders the line and makes it unreadable. So:

- **Never mix Hebrew and Latin script on the same line.** Technical terms, file paths, identifiers,
  commands and library names go on a line of their own, or in a list item — never embedded inside a
  running Hebrew sentence.
- **Prefer blocks, lists and tables to prose** whenever the content is mixed-language. A table with
  a Hebrew column and a Latin column is readable; the same content as a paragraph is not.
- **Never translate a technical term into Hebrew.** Avi asked for this directly: translations like
  "מנוע בנייה" for *build backend* or "קובץ נעילה" for *lockfile* confuse him, because the term he
  will meet in documentation, in error messages and in an interview is the English one. Keep the
  term in English and put the Hebrew explanation around it — on separate lines, per the rule above.
  A glossary table with an English column and a Hebrew column is the ideal shape.

---

## Known risks being actively managed

See `PROJECT_PLAN.md` §6 for the full register. The two that shape day-to-day decisions:

- **sim-to-real gap.** Mitigated by building the real evaluation set in Phase 2, not Phase 3. If the
  gap turns out large, that is a finding, not a failure — Phase 1 gets rebuilt from it.
- **Burnout across ~10 months.** Phase 3 is the danger zone. Public repo plus a monthly demo video
  are the countermeasures.

---

## Key references

- [Deep Aramaic — PLOS One, 2024](https://journals.plos.org/plosone/article?id=10.1371%2Fjournal.pone.0299297)
  ([arXiv](https://arxiv.org/abs/2310.07310)) — the methodological blueprint
- [InscriptiFact, USC](http://www.inscriptifact.com/aboutus/index.shtml) — ~68k images, free
  registration for researchers; the main source of real evaluation photographs
- [Culmus Ancient Semitic fonts](https://culmus.sourceforge.io/ancient/index.html) ·
  [Robo-PaleoHeb](https://github.com/edenberger/Robo-PaleoHeb) — check the license on every font
- [Review of Computational Epigraphy — arXiv](https://arxiv.org/pdf/2406.06570)

Full list in `PROJECT_PLAN.md` §7.
