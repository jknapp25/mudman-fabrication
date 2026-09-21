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

### Geometric validity is not functional validity

A valid solid, BRep, mesh, or export proves only the geometric properties actually checked. It does not by itself prove hardware fit, mating, clearance, access, insertion, removal, retention, material thickness, or mechanism motion. Never use an unqualified “validated”; name the validated property and the remaining unknowns.

When the design relies on a physical interaction, follow [Interface and Functional Validation](INTERFACE_VALIDATION.md). Use representative hardware, mating-part, tool-access, inserted-object, or motion envelopes and the minimum quantitative or intersection checks needed for the current risk. Physical performance remains unvalidated until an identified specimen is tested.

## Sources of truth

- Identify authoritative source, derived output, validation evidence, release artifact, and physical validation evidence before editing.
- Change the authoritative source, not a generated symptom.
- Treat generated files and metadata as snapshots unless the project explicitly designates them as canonical. If a snapshot disagrees with current source, do not silently promote it to authority.
- Keep documentation concise and link to authoritative files rather than duplicating configurations that can drift.

## Visualization-first iteration

Visualization is a feedback checkpoint, not merely a final deliverable. Decide automatically between these modes based on the maturity of the work, and use the minimum sufficient effort needed for the next design decision.

### Mode A — concept visualization

Use concept visualization while deciding what geometry should become: the idea is exploratory, production CAD is not yet authoritative or approved for change, alternatives are being compared, or rebuilding the model would be premature.

- Do not modify production CAD merely to make the idea visible.
- Create the smallest useful engineering-style view: one sketch when one is enough; otherwise the necessary front, side, top, section, dimensioned, or motion-state views.
- Prefer clear schematic geometry over polished rendering. These drawings communicate intent and are not manufacturing artifacts or validation evidence.
- Show enough angles or states for the user to understand the proposal and request revisions before further speculative design work.

### Mode B — actual model preview

Use an actual model preview whenever CAD is first created or materially changed in shape, fit, dimensions, interfaces, mechanism motion, or appearance. A completion that changes geometry should normally include the updated visualization.

- Regenerate or open the current geometry, run only the minimum credible validation, and present the current model before continuing into additional speculative design work.
- Prefer the best native inline 3D preview available in ChatGPT Work or the current environment, especially when it supports orbit, pan, zoom, and useful isometric/front/side/top views.
- For assemblies or mechanisms, include important positions or states when inexpensive and materially useful for review.
- Do not substitute a conceptual sketch when revised actual CAD exists and can reasonably be previewed.

### Interface-focused views

When an interface or functional feature matters, make the preview expose it. Prefer the minimum useful section, assembled view, envelope overlay, or critical motion state—for example, a section through a screw and neighboring pocket, both mating parts assembled, a seated object in a snap feature, or sampled mechanism positions.

Visual inspection helps reveal obstruction and spatial mistakes, but it does not replace obvious measurable checks such as clearance, interference, engagement, minimum material thickness, or envelope intersection.

### Freshness, fallback, and cost boundary

- A visualization presented as the **current model** must correspond to the current geometry. After a material geometry change, previous previews are stale until regenerated; never present them as current.
- If interactive inline display is unavailable, do not silently omit visualization. Use the best immediately viewable fallback, normally static renders or screenshots from enough useful angles, and state which preferred capability was unavailable.
- Lack of interactive preview must not block ordinary CAD progress. Do not install large dependencies or build custom viewers unless the project specifically requires them.
- Visualization alone does not trigger manufacturing validation, slicing, printer packaging, exhaustive testing, production exports, or high-quality rendering. Escalate those only when the task or existing project rules require them.

The expected design loop is **propose → visualize → review → revise → visualize → review**, followed by manufacturing validation only when appropriate. Give special priority to visual review for mechanisms, mating interfaces, clearances, proportions, ergonomics, mounting, moving parts, spatial relationships, and form decisions.

## Git and reporting

- Keep commits coherent, reviewable, and limited to the requested outcome. Do not fabricate history or create activity-only commits.
- Do not push unless explicitly requested.
- Before committing, inspect staged changes for secrets, absolute machine-specific paths, private data, accidental artifacts, unexpected binaries, and unexpectedly large files.
- Report the outcome, the specific validation claims established, important constraints, and any remaining functional or physical unknowns concisely. Avoid narrating routine tool use or unnecessary audits.
