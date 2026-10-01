#!/usr/bin/env python3
"""Re-export/reopen/slice an accepted Bambu project and record parity evidence."""

import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import zipfile

INVALID_CONFIG = "The 3mf file has invalid config, load geometry data only"
REQUIRED = {"Metadata/model_settings.config", "Metadata/project_settings.config"}
PROJECT_KEYS = (
    "printer_model", "printer_variant", "nozzle_diameter", "curr_bed_type",
    "filament_settings_id", "print_settings_id", "printer_settings_id",
)


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def project_settings(path):
    with zipfile.ZipFile(path) as archive:
        names = set(archive.namelist())
        archive.testzip()
        data = json.loads(archive.read("Metadata/project_settings.config")) if "Metadata/project_settings.config" in names else {}
    return {key: data.get(key) for key in PROJECT_KEYS}, REQUIRED.issubset(names)


def run(command, log):
    result = subprocess.run(command, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    log.write_text(result.stdout, encoding="utf-8")
    return result


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("golden", type=Path)
    parser.add_argument("output_dir", type=Path)
    parser.add_argument("--runner", type=Path, default=Path(__file__).with_name("run_bambu_studio.sh"))
    args = parser.parse_args(argv)
    golden = args.golden.resolve()
    output = args.output_dir.resolve()
    output.mkdir(parents=True, exist_ok=True)
    reexported = output / "golden-reexported.3mf"
    sliced = output / "golden-reopened-and-sliced.3mf"
    version = run([str(args.runner), "--help"], output / "version.log")
    export = run([str(args.runner), "--debug", "2", "--export-3mf", str(reexported), str(golden)], output / "export.log")
    slice_result = run([str(args.runner), "--debug", "2", "--slice", "0", "--export-3mf", str(sliced), str(reexported)], output / "slice.log") if reexported.is_file() else None
    golden_settings, golden_metadata = project_settings(golden)
    reexport_settings, reexport_metadata = project_settings(reexported) if reexported.is_file() else ({}, False)
    evidence = export.stdout + (slice_result.stdout if slice_result else "")
    settings_preserved = golden_settings == reexport_settings
    passed = bool(
        export.returncode == 0 and slice_result and slice_result.returncode == 0
        and golden_metadata and reexport_metadata and settings_preserved
        and INVALID_CONFIG not in evidence and sliced.is_file()
    )
    report = {
        "status": "PASS" if passed else "FAILED",
        "bambu_version_line": next((line for line in version.stdout.splitlines() if line.startswith("BambuStudio-")), None),
        "golden_sha256": sha256(golden),
        "reexported_sha256": sha256(reexported) if reexported.is_file() else None,
        "sliced_sha256": sha256(sliced) if sliced.is_file() else None,
        "required_metadata_preserved": golden_metadata and reexport_metadata,
        "project_settings_preserved": settings_preserved,
        "golden_project_settings": golden_settings,
        "reexported_project_settings": reexport_settings,
        "invalid_config_warning": INVALID_CONFIG in evidence,
        "export_return_code": export.returncode,
        "slice_return_code": slice_result.returncode if slice_result else None,
    }
    (output / "parity-report.json").write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if passed else 1


if __name__ == "__main__":
    sys.exit(main())
