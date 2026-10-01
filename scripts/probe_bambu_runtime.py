#!/usr/bin/env python3
"""Probe the pinned Bambu runtime and its required manufacturing CLI surface."""

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path


REQUIRED_FLAGS = (
    "--load-settings",
    "--load-filaments",
    "--export-3mf",
    "--slice",
)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--runtime",
        type=Path,
        default=Path(__file__).with_name("run_bambu_studio.sh"),
    )
    args = parser.parse_args()
    result = subprocess.run(
        [str(args.runtime.resolve()), "--help"],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
    )
    match = re.search(r"BambuStudio[- ]([0-9.]+)", result.stdout)
    missing = [flag for flag in REQUIRED_FLAGS if flag not in result.stdout]
    report = {
        "status": "PASS" if result.returncode == 0 and match and not missing else "FAILED",
        "return_code": result.returncode,
        "version": match.group(1) if match else None,
        "required_flags": list(REQUIRED_FLAGS),
        "missing_flags": missing,
        "output_tail": result.stdout[-4000:],
    }
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
