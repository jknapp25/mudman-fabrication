# Bambu 3MF Artifact Classes and Gates

Use these names exactly. A `.3mf` extension alone says nothing about Bambu
project compatibility.

## 1. Geometry 3MF

A standards-based 3MF containing manufacturing mesh geometry. It may include
ordinary 3MF metadata, but it does not claim to contain a usable Bambu printer,
filament, process, plate, or project configuration.

Required gate:

- archive and 3MF XML parse successfully;
- intended meshes, units, object count, orientation, and tessellation are
  verified;
- the artifact is labeled **GEOMETRY 3MF** in its filename-adjacent report and
  handoff;
- the handoff says that Bambu Studio configuration and slicing remain pending.

A Geometry 3MF must not be described as configured, sliced, print-ready, or a
Bambu project. Opening it as a project may cause Bambu Studio to report
`The 3mf file has invalid config, load geometry data only`; importing its
geometry is not configuration acceptance.

## 2. Configured Bambu Project 3MF

A 3MF containing the intended Bambu project/configuration payload in addition
to geometry. Package inspection can establish that configuration is present,
but cannot establish that Bambu Studio accepts it.

Required gate:

- the project identifies the intended printer, nozzle, plate, filament, process,
  object arrangement, and any deliberate per-object settings;
- configuration originates from a supported project-specific mechanism;
- the artifact is labeled **CONFIGURED BAMBU PROJECT 3MF — UNVALIDATED** until
  the authoritative Bambu checkpoint passes.

Do not fabricate undocumented configuration fields or promote an artifact based
only on ZIP/XML validity. Prefer Bambu Studio's own serializer when available.

## 3. Validated Print-Ready Bambu 3MF

The exact configured artifact has passed the authoritative Bambu Studio
checkpoint and the required slice inspection.

Required gate:

- Bambu Studio opens/loads the configuration without a configuration warning;
- the intended printer, nozzle, plate, filament, process, orientation, and
  per-object settings are confirmed;
- slicing completes successfully;
- required toolpath checks pass;
- the validation record identifies the exact artifact digest, Bambu Studio
  version, and result.

Only then may the artifact be labeled **VALIDATED PRINT-READY BAMBU 3MF**.

## Hard failure rule

The exact Bambu warning

> The 3mf file has invalid config, load geometry data only

automatically fails configured-project and print-ready status. The artifact is
geometry-only for that Bambu run, regardless of internal XML validity or any
earlier label.

Projects should run `scripts/classify_bambu_3mf.py` (or an equivalent stricter
project validator) in their manufacturing checkpoint. The shared checker fails
a configured/print-ready claim when required Bambu metadata is absent, and
fails any configured/print-ready claim when the warning appears in the supplied
Bambu result or log.

## Supported cloud workflow

On Ubuntu 24.04 x86-64, provision the pinned official runtime with:

```sh
MUDMAN_BAMBU_RUNTIME_DIR=/durable/runtime/path scripts/bootstrap_bambu_linux.sh
```

A fabrication project adopts the capability by copying
`templates/MANUFACTURING_INTENT.json`, supplying its geometry plus full machine,
process, and filament profiles, and running:

```sh
MUDMAN_BAMBU_RUNTIME_DIR=/durable/runtime/path \
  python3 path/to/mudman-fabrication/scripts/bambu_manufacture.py \
  path/to/project/MANUFACTURING_INTENT.json \
  --parity-report /durable/runtime/path/parity/parity-report.json
```

The command asks Bambu Studio itself to create the configured project, reopens
that exact artifact, slices every plate, rejects the invalid-config warning,
records the Bambu version and artifact hashes, and emits one classification.
Projects remain responsible for geometry generation, the chosen profiles,
orientation, product-specific toolpath expectations, and physical validation.

Cloud runtime authority is version- and platform-specific. A new Bambu version
must pass a recorded golden-project parity test before replacing the pin. The
parity test must re-export, reopen, and slice the accepted golden project and
compare printer, nozzle, plate, filament, process, orientation, and relevant
project settings. Merely launching the binary is insufficient.
`bambu_manufacture.py` will not promote an artifact to validated print-ready
unless a passing parity report for the exact running Bambu version is supplied.

## Fallback cloud-to-local workflow

When the pinned runtime cannot be provisioned or has not passed the project's
required parity gate:

1. **Cloud:** approve CAD; create and validate the fine manufacturing mesh;
   export a clearly labeled Geometry 3MF; record manufacturing intent.
2. **Local Bambu Studio:** import the Geometry 3MF; select the intended printer,
   nozzle, plate, filament, and process; inspect orientation and toolpaths;
   slice; save a Bambu-generated project 3MF.
3. **Validation:** reopen or CLI-slice that exact saved project with the recorded
   Bambu version; reject all configuration warnings and inspect required paths.
4. **Repository:** retain the canonical Bambu-generated artifact and validation
   evidence only when the project tracking policy calls for them.

Cloud generation may claim a Configured Bambu Project only when a supported
Bambu serializer is actually available and used. Reusing an old project's
private metadata without the authoritative application is not a supported
shortcut.
