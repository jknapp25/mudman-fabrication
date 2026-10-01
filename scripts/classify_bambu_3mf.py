#!/usr/bin/env python3
"""Classify a 3MF and enforce Bambu configured/print-ready claim gates."""

import argparse
import hashlib
import json
import sys
import zipfile
from pathlib import Path


INVALID_CONFIG_WARNING = "The 3mf file has invalid config, load geometry data only"
REQUIRED_BAMBU_METADATA = {
    "Metadata/model_settings.config",
    "Metadata/project_settings.config",
}


def _strings(value):
    if isinstance(value, str):
        yield value
    elif isinstance(value, dict):
        for item in value.values():
            yield from _strings(item)
    elif isinstance(value, list):
        for item in value:
            yield from _strings(item)


def _bambu_evidence(path):
    if path is None:
        return None, ""
    text = path.read_text(encoding="utf-8", errors="replace")
    try:
        data = json.loads(text)
    except json.JSONDecodeError:
        return None, text
    return data, "\n".join(_strings(data))


def classify(artifact, claim, bambu_result=None):
    raw = artifact.read_bytes()
    with zipfile.ZipFile(artifact) as archive:
        names = set(archive.namelist())
        archive.testzip()

    has_bambu_config = REQUIRED_BAMBU_METADATA.issubset(names)
    artifact_class = (
        "CONFIGURED_BAMBU_PROJECT_3MF"
        if has_bambu_config
        else "GEOMETRY_3MF"
    )
    native, evidence_text = _bambu_evidence(bambu_result)
    invalid_warning = INVALID_CONFIG_WARNING in evidence_text

    failures = []
    if claim in {"configured", "validated-print-ready"} and not has_bambu_config:
        failures.append("required Bambu project metadata is absent")
    if claim in {"configured", "validated-print-ready"} and invalid_warning:
        failures.append("Bambu Studio reported invalid configuration")
    if claim == "validated-print-ready":
        if native is None:
            failures.append("authoritative Bambu result JSON is required")
        else:
            if native.get("return_code") != 0:
                failures.append("Bambu result return_code is not zero")
            plates = native.get("sliced_plates") or []
            if not plates:
                failures.append("Bambu result contains no sliced plates")
            elif any(plate.get("warning_message", "") for plate in plates):
                failures.append("Bambu slice contains a warning")

    if claim == "validated-print-ready" and not failures:
        artifact_class = "VALIDATED_PRINT_READY_BAMBU_3MF"

    return {
        "artifact": str(artifact),
        "sha256": hashlib.sha256(raw).hexdigest(),
        "claim": claim,
        "classification": artifact_class,
        "bambu_metadata_present": has_bambu_config,
        "invalid_config_warning_detected": invalid_warning,
        "status": "FAILED" if failures else "PASS",
        "failures": failures,
    }


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("artifact", type=Path)
    parser.add_argument(
        "--claim",
        choices=("geometry", "configured", "validated-print-ready"),
        required=True,
    )
    parser.add_argument("--bambu-result", type=Path)
    args = parser.parse_args(argv)
    result = classify(args.artifact, args.claim, args.bambu_result)
    print(json.dumps(result, indent=2, sort_keys=True))
    return 1 if result["status"] == "FAILED" else 0


if __name__ == "__main__":
    sys.exit(main())
