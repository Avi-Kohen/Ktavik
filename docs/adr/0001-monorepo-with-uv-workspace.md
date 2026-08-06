# ADR-0001: Monorepo with a uv workspace

- **Status:** Accepted
- **Date:** 2026-08-06

## Context

Ktavik is built from five components: a synthetic data generator, a training and
evaluation package, an inference API, an active-learning orchestrator, and an Android
application.

Two facts about those components pull in opposite directions.

They are **tightly coupled by a pipeline**. The generator produces the images the
training package consumes; training produces the model the API serves; the API collects
the corrections that feed retraining. A change to the label format or the glyph encoding
touches several of them at once.

Their **dependencies barely overlap**. The generator needs image rendering. Training
needs the deep-learning stack and a GPU. The API needs a web framework and an inference
runtime, and must ship as a container small enough to deploy. Installing the training
stack into the serving image would inflate it by an order of magnitude for no benefit.

The project has a single developer. Any structure whose overhead scales with the number
of components will be paid for entirely by one person, on evenings and weekends, for
roughly ten months.

## Decision

A single repository containing all components under `packages/`, wired together as a
**uv workspace**: one lockfile at the root, one virtual environment, and each member
declaring its own dependencies.

The root project is **virtual** — it has no build backend and is never installed. It
exists only to declare workspace membership and the development dependency group. What
gets installed is always a member, never the root.

## Alternatives considered

### A repository per component

The honest case for it: hard boundaries. Each component gets independent versioning and
release cadence, and it is impossible to accidentally couple two of them, because the
coupling would have to be an explicit published dependency.

Rejected because the coupling here is real and frequent. A change to the label format
would require coordinated pull requests across three repositories, merged in order, with
a version bump between each. That cost is bearable for a team with owners per repository.
For one developer it is the difference between shipping and not.

### A single package containing everything

The honest case for it: the simplest possible structure, no workspace concepts to learn,
one dependency list.

Rejected because it destroys partial installation. The serving container would pull the
training stack; the Android build tooling would pull the image renderer. The separation
this project needs most — deploy the API without the training dependencies — is exactly
the one this structure cannot express.

## Consequences

### What this buys

- A cross-cutting change lands in **one commit**, reviewed as one unit, tested together.
- Every machine and CI resolve to identical versions, because there is a single
  `uv.lock`. Reproducibility across the two development machines is automatic rather
  than remembered.
- Lint, type-check and test configuration lives once at the root and applies to every
  member, including members that do not exist yet.
- The serving image can be built from the API package alone.

### What this costs

- **Dependency resolution is global.** All members are resolved together against one
  lockfile. If the training package and the API ever require incompatible versions of a
  shared library, there is no local workaround — one of them must move. In practice that
  means occasionally pinning a component to an older version than it would have chosen
  on its own.
- Every contributor clones the whole repository, including components they will never
  touch.
- As the repository grows, CI must learn to skip work that a given change cannot affect.
  This is not yet implemented and will be needed before Phase 3.

The first cost is the direct price of the first benefit. Consistency across components
and freedom per component are the same axis, and this decision chooses consistency.
