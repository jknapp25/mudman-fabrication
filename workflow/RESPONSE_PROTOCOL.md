# Visual Fabrication Response Protocol

This is a last-mile delivery contract. Generating a preview artifact is not the same as presenting it. For covered tasks, engineering completion and response presentation are both required.

## When this gate applies

Apply this protocol when a task:

- creates CAD;
- materially changes CAD geometry;
- changes a functional physical interface; or
- performs geometry-dependent validation whose result needs visual inspection.

At planning time, identify the final actual-model view and any interface-focused view the response will need. Immediately before sending the final response, run the delivery check below.

Documentation-only work does not require an actual-model preview. Research or concept work without authoritative CAD follows the concept-visualization rules instead.

## Mandatory final-response visual

The final response for a covered task **must display an immediately visible visualization of the actual current geometry**. The task is not complete merely because an STL, PNG, HTML viewer, validation report, or other preview artifact exists.

Use this order:

1. **Inline interactive actual-model preview — preferred.** Use a native inline 3D preview, or a reliably inline WebGL-style preview, when the current surface supports it. It must show the final revision. Do not build elaborate viewer infrastructure solely to satisfy this rule.
2. **Inline static actual-model preview — mandatory fallback.** If interactive display is unavailable or unreliable, embed a robust static image directly in the response so the user can see it without opening, downloading, or navigating elsewhere. Normally show a clear isometric view plus the most relevant orthographic or section view. For an interface-critical change, include the view that exposes that interface.
3. **Attached artifacts — supplemental only.** CAD sources, meshes, PNGs, reports, and HTML viewers may follow, but attachments or file cards alone do not satisfy this contract.

The displayed visual must be derived from the final current CAD, BRep, or mesh. Concept sketches, hand-drawn approximations, stale renders, and earlier revisions cannot substitute for it.

## Final-response delivery check

Immediately before responding, answer:

1. Did the task create or materially change geometry, or validate a geometry-dependent interface?
2. If yes, can the user see the **actual current model directly in the response right now**?
3. Is the displayed geometry from the final revision?
4. Does a visible view expose the feature changed or validated?
5. If inline interactive 3D is unavailable, is an inline static fallback immediately visible?
6. Are attachments supplemental rather than the only visualization?

If any required answer is no, the response is not ready. Fix the presentation before sending it.

An attempted embed that renders as a broken image, empty placeholder, bare filename, or attachment-only card does not count. Use another immediately visible representation before completing the response.

## Preferred response order

For a geometry-changing task:

1. actual current model visualization;
2. concise description of the change;
3. specific validation status and important measurements;
4. unresolved physical validation;
5. commit SHA and supplemental artifact links.

Do not say “complete,” “finished,” “validated,” or “ready for review” for a covered task until the visual-delivery gate is satisfied.

## Cost boundary

Use the cheapest reliable presentation that makes the current geometry immediately inspectable. This protocol does not require photorealistic rendering, custom Three.js development, redundant screenshots, or preview infrastructure for text-only work. The requirement is simply: **show the current thing**.
