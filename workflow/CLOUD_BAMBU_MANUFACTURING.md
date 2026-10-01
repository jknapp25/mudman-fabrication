# Cloud Bambu Manufacturing

The Linux x86-64 capability converts validated Geometry 3MF plus project-owned print intent into a Bambu-authored project, then reopens and slices that exact artifact before promotion.

`bambu-runtime.json` pins the official Ubuntu 24.04 AppImage by version, URL, and SHA-256. `scripts/bootstrap_bambu_linux.sh` verifies and extracts it without FUSE, provisions missing libraries and Weston into a private cache, and verifies CLI launch through a headless Wayland compositor. No runtime binary is committed.

Projects adopt `templates/MANUFACTURING.json` incrementally and supply validated geometry, full machine/process/filament profiles, concise intent, preserved-setting assertions, and product-specific slice expectations.

```sh
./scripts/bootstrap_bambu_linux.sh
python3 scripts/probe_bambu_runtime.py
python3 scripts/bambu_manufacture.py /path/to/project/MANUFACTURING.json
```

The command asks Bambu Studio to serialize, reopens and slices the exact output, rejects failures and warnings, verifies declared settings, records hashes, and emits `VALIDATED_PRINT_READY_BAMBU_3MF` only after every gate passes.

A newly pinned version is not authoritative merely because it launches. Promotion requires a rigid golden-project re-export, reopen/slice result, preserved-settings audit, hashes, and structural comparison. Without passing parity, configured and validated generation remains local-only.

Run the exact-golden gate with:

```sh
python3 scripts/validate_bambu_parity.py \
  /path/to/known-good-rigid-small.3mf \
  validation/runtime-parity/rigid-small-reexport.3mf \
  validation/runtime-parity/rigid-small-report.json
```

`scripts/rigid_round_parity.py` can regenerate a diagnostic rigid Small
project from its CAD source, but that is not a substitute for the exact-golden
gate.

## Runtime host requirements

The official 2.8.2.61 AppImage bundles a Wayland GLFW backend. A headless host
therefore must permit a Weston compositor to create a Unix-domain Wayland
socket in `XDG_RUNTIME_DIR`; Xvfb alone is not sufficient. The runner fails
before launching Bambu when that capability is unavailable.

## Current promotion status

The provisioner and project interface are reusable, but this runtime version is
**NOT PROMOTED AS AUTHORITATIVE** until `validation/BAMBU_CLOUD_RUNTIME_STATUS.md`
records a passing exact-golden rigid parity run. Projects must not infer cloud
authority from the presence of the scripts.
