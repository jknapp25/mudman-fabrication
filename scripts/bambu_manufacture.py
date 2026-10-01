#!/usr/bin/env python3
"""Create and authoritatively validate a Bambu project from project intent."""

import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import zipfile

INVALID_CONFIG = "The 3mf file has invalid config, load geometry data only"
REQUIRED_METADATA = {"Metadata/model_settings.config", "Metadata/project_settings.config"}


def digest(path):
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def resolve(base, value):
    path = Path(value)
    return path if path.is_absolute() else (base / path).resolve()


def run(command, log_path, cwd=None):
    completed = subprocess.run(command, cwd=cwd, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    log_path.write_text(completed.stdout, encoding="utf-8")
    return completed


def resolve_profile(profile, profile_root, destination):
    index = {}
    for candidate in profile_root.rglob("*.json"):
        try:
            data = json.loads(candidate.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        name = data.get("name")
        if name and (candidate == profile or candidate.parts[-3] == profile.parts[-3]):
            index[name] = candidate

    seen = set()
    def expand(path):
        data = json.loads(path.read_text(encoding="utf-8"))
        parent_name = data.get("inherits")
        if not parent_name:
            return data
        if parent_name in seen:
            raise ValueError(f"Profile inheritance cycle at {parent_name}")
        parent = index.get(parent_name)
        if parent is None:
            raise ValueError(f"Cannot resolve inherited profile {parent_name!r} for {path}")
        seen.add(parent_name)
        merged = expand(parent)
        merged.update(data)
        merged.pop("inherits", None)
        return merged

    resolved = expand(profile)
    destination.write_text(json.dumps(resolved, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return destination


def inspect_project(path):
    with zipfile.ZipFile(path) as archive:
        names = set(archive.namelist())
        bad_member = archive.testzip()
    return {"required_metadata_present": REQUIRED_METADATA.issubset(names), "bad_zip_member": bad_member}


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("manifest", type=Path)
    parser.add_argument("--runner", type=Path, default=Path(__file__).with_name("run_bambu_studio.sh"))
    parser.add_argument("--parity-report", type=Path)
    args = parser.parse_args(argv)
    manifest_path = args.manifest.resolve()
    base = manifest_path.parent
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    geometry = resolve(base, manifest["geometry_3mf"])
    configured = resolve(base, manifest["configured_3mf"])
    validation_dir = resolve(base, manifest["validation_dir"])
    machine = resolve(base, manifest["machine_profile"])
    process = resolve(base, manifest["process_profile"])
    filaments = [resolve(base, item) for item in manifest["filament_profiles"]]
    validation_dir.mkdir(parents=True, exist_ok=True)
    configured.parent.mkdir(parents=True, exist_ok=True)
    slice_output = validation_dir / "reopened-and-sliced.3mf"
    native_result_path = validation_dir / "result.json"
    for stale in (configured, slice_output, native_result_path):
        stale.unlink(missing_ok=True)

    missing = [str(p) for p in [geometry, machine, process, *filaments] if not p.is_file()]
    if missing:
        raise SystemExit("Missing manufacturing inputs: " + ", ".join(missing))

    profile_root_value = manifest.get("profile_root")
    if profile_root_value:
        profile_root = resolve(base, profile_root_value)
        resolved_dir = validation_dir / "resolved-profiles"
        resolved_dir.mkdir(parents=True, exist_ok=True)
        machine = resolve_profile(machine, profile_root, resolved_dir / "machine.json")
        process = resolve_profile(process, profile_root, resolved_dir / "process.json")
        filaments = [resolve_profile(item, profile_root, resolved_dir / f"filament-{index}.json") for index, item in enumerate(filaments, 1)]

    version_log = validation_dir / "bambu-version.log"
    version = run([str(args.runner), "--help"], version_log, validation_dir)
    generate_log = validation_dir / "generate.log"
    generate_command = [
        str(args.runner), "--debug", "2", "--load-settings", f"{machine};{process}",
        "--load-filaments", ";".join(map(str, filaments)),
    ]
    if manifest.get("build_plate"):
        generate_command.append(f"--curr-bed-type={manifest['build_plate']}")
    for key, value in (manifest.get("bambu_overrides") or {}).items():
        if not key.replace("_", "").replace("-", "").isalnum():
            raise SystemExit(f"Invalid Bambu override key: {key}")
        generate_command.append(f"--{key.replace('_', '-')}={value}")
    generate_command.extend(["--export-3mf", str(configured), str(geometry)])
    generated = run(generate_command, generate_log, validation_dir)
    generated_text = generated.stdout
    generated_ok = generated.returncode == 0 and configured.is_file() and INVALID_CONFIG not in generated_text
    package = inspect_project(configured) if configured.is_file() else {"required_metadata_present": False, "bad_zip_member": None}

    slice_log = validation_dir / "slice.log"
    sliced = run([
        str(args.runner), "--debug", "2", "--slice", "0", "--export-3mf", str(slice_output), str(configured)
    ], slice_log, validation_dir) if generated_ok and package["required_metadata_present"] else None
    slice_text = sliced.stdout if sliced else ""
    diagnostics = [line for line in (generated_text + "\n" + slice_text).splitlines() if "[warning]" in line.lower() or "[error]" in line.lower()]
    try:
        native_result = json.loads(native_result_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        native_result = None
    plates = native_result.get("sliced_plates", []) if native_result else []
    native_ok = bool(
        native_result and native_result.get("return_code") == 0 and plates
        and all(not plate.get("warning_message") for plate in plates)
    )
    slice_ok = bool(sliced and sliced.returncode == 0 and slice_output.is_file() and INVALID_CONFIG not in slice_text and native_ok)
    parity = None
    if args.parity_report:
        try:
            parity = json.loads(args.parity_report.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            parity = None
    parity_ok = bool(parity and parity.get("status") == "PASS" and parity.get("bambu_version_line") == next((line for line in version.stdout.splitlines() if line.startswith("BambuStudio-")), None))
    status = "PASS" if generated_ok and package["required_metadata_present"] and not package["bad_zip_member"] and slice_ok and parity_ok else "FAILED"
    report = {
        "status": status,
        "classification": "VALIDATED_PRINT_READY_BAMBU_3MF" if status == "PASS" else "CONFIGURED_BAMBU_PROJECT_3MF_UNVALIDATED",
        "bambu_version_line": next((line for line in version.stdout.splitlines() if line.startswith("BambuStudio-")), None),
        "geometry_sha256": digest(geometry),
        "configured_sha256": digest(configured) if configured.is_file() else None,
        "slice_output_sha256": digest(slice_output) if slice_output.is_file() else None,
        "generate_return_code": generated.returncode,
        "slice_return_code": sliced.returncode if sliced else None,
        "native_slice_result": native_result,
        "invalid_config_warning": INVALID_CONFIG in (generated_text + slice_text),
        "runtime_parity_passed": parity_ok,
        "log_diagnostics": diagnostics,
        "package": package,
        "intent": {key: manifest.get(key) for key in ("printer", "nozzle_mm", "build_plate", "orientation", "supports", "brim")},
        "bambu_overrides": manifest.get("bambu_overrides") or {},
        "logs": {"version": str(version_log), "generate": str(generate_log), "slice": str(slice_log)},
    }
    report_path = validation_dir / "manufacturing-validation.json"
    report_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if status == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
