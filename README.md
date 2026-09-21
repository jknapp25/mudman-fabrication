# mudman-fabrication

`mudman-fabrication` is a small, documentation-first toolkit for reproducible AI-assisted digital fabrication projects. It provides shared workflow guidance, project templates, and a conservative fabrication-oriented `.gitignore` without imposing a CAD framework, build system, or Python package.

## Why it exists

Fabrication projects mix several kinds of information: editable design sources, generated exports, validation records, release packages, and physical test results. When those roles are unclear, an old export or a passing digital check can be mistaken for the approved design. This toolkit gives engineers, makers, and AI collaborators a compact vocabulary and a repeatable way to record what is authoritative and what has actually been validated.

The guiding principle is **minimum sufficient scope, context, validation, visualization, and reporting**. Make the smallest coherent change, inspect only the relevant files and direct dependencies, choose the lowest validation tier that credibly proves the change, show the minimum useful view for the next design decision, and report the result without unrelated cleanup or process narration.

## Sources, artifacts, and validation

An **authoritative source** is the file or system that owns a decision and should be edited to change it. A **generated artifact** is normally a derived snapshot, not a source of truth, unless the project explicitly designates it as canonical. See [Artifact Roles](workflow/ARTIFACT_ROLES.md) for the complete vocabulary.

Validation is organized into four reusable tiers:

1. **Small/local:** documentation, syntax, formatting, and focused checks
2. **Geometry/behavior:** shape, interfaces, topology, and functional behavior
3. **Manufacturing/export:** tool configuration, orientation, exports, and warnings
4. **Production checkpoint/release:** exact release artifacts, evidence, and approval state

Escalate only when the requested outcome or its risk requires it. A digital pass demonstrates only what was checked in software; it does not replace physical fit, process, or production evidence. See [Validation Tiers](workflow/VALIDATION_TIERS.md).

## AI-assisted fabrication workflow

Before changing a project, identify its current repository state, authoritative sources, derived outputs, and validation entry points. Repository state takes precedence over stale conversation history. Keep changes narrowly scoped, preserve unrelated work, check Git status, and inspect staged content before committing. Do not fabricate history or push unless explicitly requested.

Visualization is part of the iteration loop. Exploratory proposals receive lightweight conceptual views without unnecessary CAD changes; created or materially revised CAD receives a preview of the current model. Native inline viewing is preferred, with immediately viewable static angles as the fallback. Previous previews become stale after material geometry changes. The canonical contract and its cost boundaries are in [Generic Codex Workflow](workflow/GENERIC_CODEX_WORKFLOW.md).

The full product-agnostic workflow is in [Generic Codex Workflow](workflow/GENERIC_CODEX_WORKFLOW.md).

## Bootstrap a project

1. Copy the files from [`templates/`](templates/) into the new project's repository root. Bracketed fields are intentional prompts to replace with project facts.
2. Fill in project-specific sources of truth, commands, preview entry point, and validation entry points in `AGENTS.md`.
3. Record only the current approved state in `PROJECT_STATE.md`, including its lightweight visualization status. Do not use it as a preview log.
4. Define production assumptions and gates in `PRODUCTION_SPEC.md` without inventing universal thresholds.
5. Adopt [`gitignore/fabrication.gitignore`](gitignore/fabrication.gitignore), then add project-specific rules. Selectively unignore any canonical production artifacts the project intentionally tracks.
6. Use the physical checklist, validation report, and revision history as evidence is created—not as substitutes for testing.

The [minimal project layout](examples/minimal-project-layout.md) shows how these pieces can relate without prescribing tools or product details.

Existing projects can adopt the same behavior by updating their `AGENTS.md` reference or adopted workflow copy and adding the lightweight visualization-state section from `templates/PROJECT_STATE.md` when it helps prevent stale-preview confusion.

## Intentionally not included

This repository does not provide product geometry, dimensions or tolerances, manufacturing settings, CAD abstractions, a Python package, slicer-package generation, or dependencies between projects. It is workflow infrastructure only; projects remain responsible for their own tools, profiles, validation logic, and explicitly canonical outputs.

## License

Licensed under the [MIT License](LICENSE).
