# ktavik-synth

Synthetic training-data generation for Paleo-Hebrew OCR.

No labelled corpus of Paleo-Hebrew inscriptions exists at the scale supervised
training requires — the entire known corpus is a few thousand items, most of them
a handful of words each. This package builds a corpus instead: it renders
public-domain Hebrew text in ancient scripts, jitters each glyph to imitate a
human hand, and applies a photorealistic degradation pipeline (ceramic, stone and
papyrus substrates, ink fading, erosion, cracks, lighting) so the output resembles
a field photograph of a real inscription rather than a clean render.

Every image is generated from a known string, so labels are exact and free.
Generation is fully seeded and reproducible.