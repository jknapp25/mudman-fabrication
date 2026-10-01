#!/usr/bin/env python3
"""Serialize and validate a project-owned manufacturing manifest with Bambu."""

import argparse
import hashlib
import json
import re
import subprocess
import tempfile
import zipfile
from pathlib import Path


INVALID_CONFIG_WARNING = "The 3mf file has invalid config, load geometry data only"
REQUIRED_BAMBU_METADATA = {
    "Metadata/model_settings.config",
    "Metadata/project_settings.config",
}


def digest(path):
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def run(command):
    result = subprocess.run(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
    )
    if result.returncode or INVALID_CONFIG_WARNING in result.stdout:
        raise RuntimeError("Bambu command failed:\n" + result.stdout)
    return result.stdout


def runtime_version(runtime):
    output = run([str(runtime), "--help"])
    match = re.search(r"BambuStudio[- ]([0-9.]+)", output)
    if not match:
        raise RuntimeError("Bambu Studio version was not present in --help output")
    return match.group(1)


def manufacture(manifest_path,runtime):
    manifest_path = manifest_path.resolve()
    base = manifest_path.parent
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    resolve = lambda value: (base / value).resolve()
    geometry = resolve(manifest["geometry_3mf"])
    output = resolve(manifest["output_project_3mf"])
    profiles = manifest["profiles"]
    machine = resolve(profiles["machine"])
    process = resolve(profiles["process"])
    filaments = [resolve(value) for value in profiles["filaments"]]

    inputs = [geometry, machine, process, *filaments]
    missing = [str(path) for path in inputs if not path.is_file()]
    if missing:
        raise RuntimeError("Manufacturing input missing: " + ", ".join(missing))

    version = runtime_version(runtime)
    output.parent.mkdir(parents=True,exist_ok=True)
    export_log = run([
        str(runtime),
        "--load-settings", f"{machine};{process}",
        "--load-filaments", ";".join(map(str, filaments)),
        "--arrange", "0",
        "--export-3mf", str(output),
        str(geometry),
    ])
    with zipfile.ZipFile(output) as archive:
        corrupt = archive.testzip()
        if corrupt:
            raise RuntimeError(f"Corrupt 3MF member: {corrupt}")
        names = sorted(archive.namelist())
        absent = REQUIRED_BAMBU_METADATA.difference(names)
        if absent:
            raise RuntimeError("Bambu project metadata absent: " + ", ".join(sorted(absent)))
        project = json.loads(archive.read("Metadata/project_settings.config"))

    expected = manifest.get("expect", {})
    required = expected.get("project_settings", {})
    for key, value in required.items():
        if project.get(key) != value:
            raise RuntimeError(
                f"{key}: expected {value!r}, got {project.get(key)!r}"
            )

    project_sha = digest(output)
    with tempfile.TemporaryDirectory(prefix="mudman-bambu-") as directory:
        slice_log = run([
            str(runtime),
            "--slice", "0",
            "--outputdir", directory,
            str(output),
        ])
        if digest(output) != project_sha:
            raise RuntimeError("Configured project changed during reopen/slice validation")
        result_path = Path(directory) / "result.json"
        if not result_path.exists():
            raise RuntimeError("Bambu did not emit result.json")
        native = json.loads(result_path.read_text(encoding="utf-8"))
        plates = native.get("sliced_plates") or []
        if (
            native.get("return_code") != 0
            or not plates
            or any(item.get("warning_message", "") for item in plates)
        ):
            raise RuntimeError("Bambu slice was not warning-free")
        if expected.get("require_gcode", True) and not list(Path(directory).glob("*.gcode")):
            raise RuntimeError("Bambu did not emit G-code")

    report = {
        "artifact_class": "VALIDATED_PRINT_READY_BAMBU_3MF",
        "bambu_studio_version": version,
        "geometry_sha256": digest(geometry),
        "project_sha256": project_sha,
        "project_3mf": str(output),
        "package_entries": names,
        "project_settings_verified": required,
        "slice_return_code": native.get("return_code"),
        "slice_plate_count": len(plates),
        "invalid_config_warning": False,
        "export_log_tail": export_log[-2000:],
        "slice_log_tail": slice_log[-2000:],
    }
    report_path = resolve(
        manifest.get("validation_report", "BambuManufacturingValidation.json")
    )
    report_path.write_text(
        json.dumps(report, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return report


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("manifest", type=Path)
    parser.add_argument(
        "--runtime",
        type=Path,
        default=Path(__file__).with_name("run_bambu_studio.sh"),
    )
    args = parser.parse_args()
    print(json.dumps(
        manufacture(args.manifest, args.runtime.resolve()),
        indent=2,
        sort_keys=True,
    ))


if __name__ == "__main__":
    main()
