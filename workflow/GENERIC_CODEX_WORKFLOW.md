# Generic Codex Workflow

Use the minimum sufficient scope, context, validation, and reporting needed to complete the task safely.

## Scope and inspection

- Make the smallest coherent change required by the request. Do not bundle unrelated cleanup, redesign, dependency work, or speculative architecture into a narrow task.
- Inspect the named files and their direct dependencies first. Expand outward only when evidence shows it is necessary; avoid repository-wide audits when targeted inspection can answer the question.
- Treat the current repository state as authoritative over stale conversation history. Confirm assumptions against the files before acting.
- Preserve unrelated user work. Check Git status before editing and again before committing, and work around unrelated changes rather than overwriting them.

## Validation

Choose the lowest tier that credibly proves the requested change, escalating only when the risk or deliverable requires it:

1. **Small/local:** syntax, formatting, focused assertions, file existence, and narrow unit or document checks.
2. **Geometry/behavior:** targeted model generation and checks of the affected geometry, interfaces, or intended behavior.
3. **Manufacturing/export:** regeneration and verification of affected neutral, machine, or slicer artifacts, including configuration and warnings.
4. **Production checkpoint/release:** verification of the exact release package, required physical-test evidence, production approval, and rollback or reference state.

Do not run a higher tier merely because its tooling exists. Do not regenerate unaffected artifacts, and never describe digital validation as physical validation.

## Sources of truth

- Identify authoritative source, derived output, validation evidence, release artifact, and physical validation evidence before editing.
- Change the authoritative source, not a generated symptom.
- Treat generated files and metadata as snapshots unless the project explicitly designates them as canonical. If a snapshot disagrees with current source, do not silently promote it to authority.
- Keep documentation concise and link to authoritative files rather than duplicating configurations that can drift.

## Git and reporting

- Keep commits coherent, reviewable, and limited to the requested outcome. Do not fabricate history or create activity-only commits.
- Do not push unless explicitly requested.
- Before committing, inspect staged changes for secrets, absolute machine-specific paths, private data, accidental artifacts, unexpected binaries, and unexpectedly large files.
- Report the outcome, validation performed, important constraints, and any remaining decision concisely. Avoid narrating routine tool use or unnecessary audits.
