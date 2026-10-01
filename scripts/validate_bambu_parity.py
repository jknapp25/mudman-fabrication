#!/usr/bin/env python3
"""Re-export, reopen, and slice an exact known-good Bambu project."""

import argparse
import hashlib
import json
import re
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path


INVALID_CONFIG_WARNING = "The 3mf file has invalid config, load geometry data only"
DEFAULT_SETTING_KEYS = (
    "printer_model",
    "printer_variant",
    "curr_bed_type",
    "filament_settings_id",
    "print_settings_id",
)


def digest(path):
    value = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            value.update(chunk)
    return value.hexdigest()


def run(command):
    result = subprocess.run(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
    )
    if result.returncode or INVALID_CONFIG_WARNING in result.stdout:
        raise RuntimeError(result.stdout)
    return result.stdout


def package(path):
    with zipfile.ZipFile(path) as archive:
        corrupt = archive.testzip()
        if corrupt:
            raise RuntimeError(f"Corrupt 3MF member: {corrupt}")
        names = sorted(archive.namelist())
        project = json.loads(archive.read("Metadata/project_settings.config"))
        model = archive.read("Metadata/model_settings.config")
    return names, project, model


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("golden", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("report", type=Path)
    parser.add_argument(
        "--runtime",
        type=Path,
        default=Path(__file__).with_name("run_bambu_studio.sh"),
    )
    parser.add_argument(
        "--setting-key",
        action="append",
        dest="setting_keys",
        default=[],
    )
    args = parser.parse_args()
    runtime = args.runtime.resolve()
    golden = args.golden.resolve()
    output = args.output.resolve()
    setting_keys = args.setting_keys or list(DEFAULT_SETTING_KEYS)

    help_output = run([str(runtime), "--help"])
    version_match = re.search(r"BambuStudio[- ]([0-9.]+)", help_output)
    if not version_match:
        raise RuntimeError("Bambu Studio version missing from help output")

    golden_names, golden_project, golden_model = package(golden)
    output.parent.mkdir(parents=True, exist_ok=True)
    export_log = run([str(runtime), "--export-3mf", str(output), str(golden)])
    candidate_sha = digest(output)
    candidate_names, candidate_project, candidate_model = package(output)

    mismatches = {
        key: {
            "golden": golden_project.get(key),
            "candidate": candidate_project.get(key),
        }
        for key in setting_keys
        if golden_project.get(key) != candidate_project.get(key)
    }
    required_entries = {
        "Metadata/model_settings.config",
        "Metadata/project_settings.config",
    }
    if not required_entries.issubset(candidate_names):
        raise RuntimeError("Re-export lacks required Bambu project metadata")
    if mismatches:
        raise RuntimeError("Preserved-setting mismatch: " + json.dumps(mismatches))

    with tempfile.TemporaryDirectory(prefix="mudman-bambu-parity-") as directory:
        slice_log = run([
            str(runtime),
            "--slice", "0",
            "--outputdir", directory,
            str(output),
        ])
        if digest(output) != candidate_sha:
            raise RuntimeError("Re-export changed during exact-artifact slice")
        result_path = Path(directory) / "result.json"
        if not result_path.is_file():
            raise RuntimeError("Bambu did not emit result.json")
        native = json.loads(result_path.read_text(encoding="utf-8"))
        plates = native.get("sliced_plates") or []
        if (
            native.get("return_code") != 0
            or not plates
            or any(plate.get("warning_message", "") for plate in plates)
        ):
            raise RuntimeError("Parity slice was not warning-free")

    report = {
        "status": "PASS",
        "bambu_studio_version": version_match.group(1),
        "golden_sha256": digest(golden),
        "candidate_sha256": candidate_sha,
        "invalid_config_warning": False,
        "slice_return_code": native.get("return_code"),
        "slice_plate_count": len(plates),
        "preserved_settings": {
            key: candidate_project.get(key) for key in setting_keys
        },
        "package_entries_added": sorted(set(candidate_names) - set(golden_names)),
        "package_entries_removed": sorted(set(golden_names) - set(candidate_names)),
        "model_settings_bytes_equal": golden_model == candidate_model,
        "export_log_tail": export_log[-2000:],
        "slice_log_tail": slice_log[-2000:],
    }
    args.report.resolve().parent.mkdir(parents=True, exist_ok=True)
    args.report.resolve().write_text(
        json.dumps(report, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
