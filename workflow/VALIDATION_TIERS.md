# Validation Tiers

Use the lowest tier that credibly demonstrates the requested outcome. Escalation is justified when a change crosses a boundary that the current tier cannot evaluate, when risk increases, or when the deliverable itself is a manufacturing or release artifact.

## 1. Small/local

Use for documentation, configuration, or narrowly scoped code changes. Checks may include syntax, formatting, file existence, link resolution, focused assertions, and small unit tests.

## 2. Geometry/behavior

Use when shape, fit logic, topology, interfaces, object composition, or functional behavior changes. Generate or exercise only the affected model or behavior and check the properties relevant to the request.

## 3. Manufacturing/export

Use when manufacturability, export correctness, machine configuration, orientation, packaging, or slicer/tool interpretation is part of the outcome. Regenerate only affected outputs and inspect settings, contents, and warnings.

## 4. Production checkpoint/release

Use when approving or publishing an exact production package. Verify the release artifact, its traceability to source, required digital and physical evidence, approval status, and rollback or reference state.

Higher tiers cost more time and may create unrelated outputs. Running them without need adds noise rather than confidence. Conversely, lower-tier success must not be presented as evidence for properties it did not test, especially physical performance.
