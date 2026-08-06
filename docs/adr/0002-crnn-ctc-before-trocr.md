# ADR-0002: CRNN + CTC for recognition, before TrOCR

- **Status:** Accepted
- **Date:** 2026-08-06

## Context

The recognition stage takes a photograph of a line of Paleo-Hebrew script and returns
the sequence of glyphs it contains. This is where roughly ninety percent of the
engineering in Ktavik lives; transliteration and translation are comparatively trivial.

The hard part is not classifying a single glyph. It is that **glyph boundaries are
unknown**. On a broken ostracon with eroded strokes and irregular spacing, there is no
reliable way to segment the line first and classify second — and segmentation errors
poison everything downstream. The architecture therefore has to read the line as a
sequence, without being told where each glyph begins.

Three constraints shape the choice:

- **No labelled corpus exists.** The entire known body of Paleo-Hebrew inscriptions is a
  few thousand items, most of them a handful of words. Training data will be synthetic.
- **The model must run on a phone.** The Android application has an offline path
  intended to work at an excavation site with no connectivity.
- **The developer must be able to explain every stage of it.** This is a portfolio
  project. A component that cannot be defended in detail is worth less here than a
  weaker component that can.

## Decision

Use a **CRNN trained with CTC loss**: a convolutional stack that extracts visual
features, sliced into vertical frames, read by a recurrent layer, and trained with
Connectionist Temporal Classification so that no frame-to-glyph alignment has to be
supplied.

TrOCR is deferred, not rejected. It returns in Phase 3 as a challenger model, evaluated
against the same held-out truth set.

## Alternatives considered

### Segment-then-classify

The honest case for it: conceptually simple, easy to debug, and each stage can be
inspected on its own. It is also what the closest prior work — Deep Aramaic — does,
successfully, at the single-glyph level.

Rejected because segmentation is the failure mode, not the solution. On degraded
inscriptions the boundaries are exactly what is missing, and an error in the first stage
is unrecoverable in the second. Deep Aramaic works because it evaluates on pre-cut
glyphs; Ktavik's stated gap over it is line-level end-to-end recognition.

### TrOCR

The honest case for it: a transformer encoder paired with a text decoder, pretrained on
enormous volumes of text and images. That pretraining is precisely the mechanism that
compensates for a scarce target corpus, which is Ktavik's central difficulty. It
processes a whole line in parallel rather than sequentially, and it carries linguistic
priors that can recover a glyph too eroded to read from pixels alone.

Rejected for now on three grounds:

1. **Size.** Hundreds of millions of parameters. It does not fit the on-device path, and
   fine-tuning it is not practical on a single consumer GPU.
2. **Opacity.** Its behaviour cannot be explained stage by stage by someone still
   learning the field, which defeats one of the project's stated purposes.
3. **Unclear transfer.** Its linguistic prior is modern script and modern language. On
   eighth-century BCE inscriptions that prior may help, or it may actively harm — the
   decoder may complete a familiar word instead of reading what is written. That is an
   empirical question, and Phase 3 is where it gets answered rather than assumed.

## Consequences

### What this buys

- Trains in hours on a single local GPU, which makes iteration on the synthetic
  generator possible at all.
- Small enough to export and run on device, which is what makes the offline path real.
- Forces a working understanding of CTC — the alignment-free loss, the blank symbol,
  the collapse rule, the dynamic-programming sum over valid alignments. This is standard
  interview material and cannot be acquired by calling a pretrained model.
- Keeps the pipeline inspectable: feature maps, per-frame distributions and decoded
  output can each be examined separately when accuracy is poor.

### What this costs

- **No linguistic prior.** The network sees shapes, not words. A glyph eroded past
  legibility is lost, where a language-aware decoder might have recovered it. Phase 3
  partially compensates with beam search over an n-gram model of Biblical Hebrew, but
  that is a decoding-time patch, not a learned prior.
- **Sequential processing.** The recurrent layer reads frame by frame and cannot be
  parallelised across the line. Long lines are slower, and long-range context degrades
  toward the end of the sequence.
- **The project is now fully staked on the synthetic data generator.** Pretraining is
  the standard answer to a scarce corpus, and declining it means there is no fallback if
  the sim-to-real gap turns out to be large. This is risk #1 in the project register,
  and this decision is what sharpens it. The mitigation is to build the real evaluation
  set in Phase 2 rather than Phase 3, so the gap is measured early enough to act on.

### Reversibility

Low cost to revisit. The recognition stage sits behind a fixed interface — image in,
glyph sequence out — so swapping the model does not disturb the rest of the pipeline.
Running TrOCR as a challenger in Phase 3 and publishing the comparison is a better
outcome than having chosen it blindly now, whichever model wins.
