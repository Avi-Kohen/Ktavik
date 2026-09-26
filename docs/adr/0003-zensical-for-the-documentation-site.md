# ADR-0003: Zensical for the documentation site

- **Status:** Accepted
- **Date:** 2026-09-26

## Context

Phase 0 requires a documentation site. Today it would carry the two existing ADRs. Later it
carries the model card, the dataset card and evaluation results with graphs — material that
belongs beside the code but would bloat a README whose job is to convince a reader in thirty
seconds.

Three facts shape the choice.

**The content is prose.** ADRs, cards, write-ups. There is no public API to document, and by the
reasoning recorded below there will not be one for the foreseeable future.

**There is one developer, working evenings and weekends across roughly ten months.** Anything
whose maintenance cost scales is paid for entirely by one person.

**The repository is public and the site is part of what a reader judges.** This is not internal
documentation.

One complication arrived after the fact. A first choice — Material for MkDocs — was made in August
2026 and never recorded as an ADR. Six weeks later a build warning surfaced that the MkDocs
ecosystem had fractured:

- MkDocs 1.x has had no release since August 2024
- MkDocs 2.0 is a pre-release that removes the plugin system entirely, rewrites theming, moves
  configuration from YAML to TOML, offers no migration path, and carries no declared licence
- Material for MkDocs pins `mkdocs<2` to keep working, and is **end-of-life on 5 May 2027**
- The Material team has redirected its effort into a new generator, Zensical

That is the situation this ADR resolves.

## Decision

Use **Zensical**, pinned through `uv.lock` and installed as a dedicated `docs` dependency group so
that neither the development environment nor the CI check job carries it.

Zensical auto-discovers `docs/`, so the site has no navigation configuration to maintain as ADRs
accumulate.

The criteria applied, in order of weight: low maintenance cost, a modern interface with working
search and navigation, and a simple writing experience. Longevity of the underlying project was
weighed and deliberately given less weight than it first appeared to deserve — see
[Reversibility](#reversibility).

## Alternatives considered

### Material for MkDocs — the incumbent

The honest case for it: mature, an enormous plugin ecosystem, the best-looking defaults of any
option here, and it was already configured and building locally. Its switching cost was the
highest of all the alternatives precisely because it was the only one already working.

Rejected because it has a dated end of life — 5 May 2027 — and its foundation is unmaintained.
Choosing it means knowingly adopting a stack whose expiry falls inside this project's own
lifetime.

### Sphinx

The honest case for it, and it is strong: maintained since 2008, actively developed, and the
standard across scientific Python — NumPy, SciPy, Pandas and PyTorch all use it. Its `autodoc`
extension generates API reference directly from docstrings and type hints, which would turn the
strict type annotations this project already requires into documentation at no additional cost.
With MyST-Parser it reads Markdown, so the existing ADRs would need no conversion. And it carries
none of the ecosystem risk that eliminated Material.

Rejected because its decisive advantage does not apply here. `autodoc` is what distinguishes
Sphinx, and there is no intention to publish a generated API reference for `packages/models` or
`packages/api`. The documents that carry weight for this project are prose: a reader evaluating it
opens the ADRs and the model card, not a generated reference. Measured on the criteria that do
apply — maintenance cost, interface quality, search and navigation, writing experience — Sphinx is
the weaker option out of the box, and `conf.py` is a Python module rather than a declarative file,
which is more surface area to get wrong for no benefit being collected.

Sphinx was in fact selected briefly during this decision and then reversed. The reversal is
recorded rather than tidied away, because the two choices were made on different questions. The
first applied a general principle: prefer the stable foundation. The second asked whether that
principle's benefit actually applied to *this* component. The second is the better question, and
the answer is in Reversibility below.

### MkDocs 2.0

The honest case for it: it is the upstream project's own direction, so in the long run it may be
where the ecosystem settles.

Rejected on three counts, any one of which would be sufficient. The plugin system has been
removed. There is no migration path from 1.x. And no licence is declared — a dependency with no
licence does not belong in an Apache-2.0 repository, whatever its technical merits.

### No documentation site at all

The honest case for it: zero work and zero maintenance. GitHub renders Markdown already, so the
ADRs are readable today without any of this.

Rejected because Phase 0 names a documentation site as a deliverable. Dropping it is a legitimate
choice, but it requires amending the plan in writing rather than quietly not doing it. The site's
value also grows through Phases 1 to 6, as evaluation results and cards arrive.

## Consequences

### What this buys

- **The configuration survived the change of tool.** Zensical reads MkDocs-shaped input, so the
  work done under the previous decision was not wasted — only the file format changed.
- **A much smaller dependency surface:** eight packages against Material's thirty-odd, and no
  MkDocs anywhere in the tree. Zensical is a standalone generator, not a theme or a plugin.
- **No navigation to maintain.** Pages are discovered from the filesystem, so adding ADR-0004 is
  one new file and no configuration edit.
- **MIT licensed,** and built by the team behind Material — who have the strongest available
  understanding of what this kind of site needs.
- **Low friction to write.** Content stays plain Markdown, with no directives to learn.

### What this costs

- **This is alpha software.** `0.0.65` at the time of writing. `0.1.0` is scheduled for
  5 November 2026, and the project states explicitly that breaking changes will occur and that
  users should not wait for 1.0.
- **A small community.** Fewer examples, fewer answers, and a real chance of being the first
  person to hit a given bug. For a developer learning ML engineering, hours spent debugging
  documentation tooling are hours not spent on the synthetic data generator.
- **Upgrade discipline is now required.** `uv.lock` pins the exact version and CI runs
  `uv sync --locked`, so builds stay reproducible. The hazard is `uv lock --upgrade`: this is the
  dependency most likely to break as collateral damage from upgrading something unrelated. It has
  to be upgraded deliberately, not incidentally.
- **No generated API reference.** If that need arises, this decision has to be reopened.

### Open question

Zensical's build cache contains `mkdocstrings.json` and `objects.inv`, which suggests some
API-reference generation capability exists. Its completeness was not verified before deciding,
because the decision did not depend on it. If the need arises, testing this is the first step —
before assuming a migration is required.

### Reversibility

High, and that is what carried the decision.

The argument that nearly selected Sphinx was foundation stability. It was given less weight than
it first appeared to deserve, for one reason: **a documentation site has the smallest blast radius
of anything in this system.** If it breaks, no model breaks, no service breaks, no application
breaks. What is lost is a website that can be rebuilt in an afternoon from Markdown files that are
themselves tool-independent.

The content in `docs/` ports to every alternative considered here. What a migration would actually
discard is `zensical.toml` — three lines — and one deploy workflow.

This decision is revisited on either of two triggers:

1. **A generated API reference is needed** for `packages/models` or `packages/api`. The open
   question above gets tested first; only if the answer is inadequate does the tool change.
2. **A Zensical upgrade breaks the documentation build twice.** At that point the cost of riding
   an alpha release has exceeded its benefit, and the choice should be reopened regardless of
   anything else.
