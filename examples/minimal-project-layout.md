# Minimal Project Layout

This fictional `LumenTag` project illustrates relationships, not required names, tools, settings, or acceptance thresholds.

```text
lumen-tag/
├── AGENTS.md
├── PROJECT_STATE.md
├── PRODUCTION_SPEC.md
├── src/
│   └── tag-model.cad
├── tests/
│   └── check-model-interface.example
├── profiles/
│   └── README.md
├── outputs/
│   └── README.md
├── PHYSICAL_VALIDATION_CHECKLIST.md
├── VALIDATION_REPORT.md
└── REVISION_HISTORY.md
```

- `AGENTS.md` points collaborators to the shared generic workflow, identifies project commands, and records project-specific rules.
- `PROJECT_STATE.md` indexes the currently approved revision, authoritative files, validation status, and unresolved decisions. It changes only when approved state changes.
- `src/tag-model.cad` is the fictional authoritative design source.
- `tests/` contains focused digital checks tied to stated properties, not claims of physical validation.
- `profiles/` contains project-owned tooling or process profiles and explains which file, if any, is authoritative.
- `outputs/` contains derived exports. Its policy states whether any exact release artifact is intentionally canonical; other generated outputs can remain ignored and reproducible.
- The physical checklist records a specimen, conditions, project-defined acceptance criteria, observations, and result.
- The validation report ties evidence to a revision and tier, while revision history records approved changes and artifact identifiers.

A typical flow changes `src/tag-model.cad`, runs the lowest credible checks from `tests/`, generates only affected outputs, and records physical evidence only after a real specimen is tested. Approval then updates `PROJECT_STATE.md` and, when applicable, identifies the exact release artifact.
