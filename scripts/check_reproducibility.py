#!/usr/bin/env python3
"""Validate the repository's reproducibility contract."""

from __future__ import annotations

import argparse
import csv
import json
import platform
import shutil
import sys
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Any

import yaml


REPO_ROOT = Path(__file__).resolve().parent.parent


@dataclass
class CheckResult:
    level: str
    stage: str
    path: str
    message: str


def load_manifest(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(f"Manifest not found: {path}")
    with path.open("r", encoding="utf-8") as handle:
        manifest = yaml.safe_load(handle)
    if not isinstance(manifest, dict):
        raise ValueError("Manifest must be a YAML mapping")
    if "stages" not in manifest or not isinstance(manifest["stages"], dict):
        raise ValueError("Manifest must contain a 'stages' mapping")
    return manifest


def resolve_path(base_path: Path, raw_path: str) -> Path:
    candidate = Path(raw_path)
    if candidate.is_absolute():
        return candidate
    return base_path / candidate


def csv_columns(path: Path) -> list[str]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.reader(handle)
        try:
            return next(reader)
        except StopIteration:
            return []


def validate_entry(base_path: Path, stage: str, entry: dict[str, Any], section: str) -> list[CheckResult]:
    results: list[CheckResult] = []
    raw_path = entry.get("path")
    if not raw_path:
        return [CheckResult("error", stage, "", f"{section} entry is missing a path")]

    path = resolve_path(base_path, str(raw_path))
    expected_format = entry.get("format", "file")
    required = bool(entry.get("required", False))

    if not path.exists():
        level = "missing" if required else "warning"
        results.append(CheckResult(level, stage, str(raw_path), "missing"))
        return results

    if expected_format == "directory" and not path.is_dir():
        results.append(CheckResult("error", stage, str(raw_path), "expected directory"))
    elif expected_format != "directory" and not path.is_file():
        results.append(CheckResult("error", stage, str(raw_path), "expected file"))

    expected_columns = entry.get("columns") or []
    if expected_columns and path.is_file() and path.suffix.lower() == ".csv":
        actual = csv_columns(path)
        missing = [column for column in expected_columns if column not in actual]
        if missing:
            results.append(
                CheckResult("error", stage, str(raw_path), f"missing columns: {', '.join(missing)}")
            )

    return results


def validate_manifest(manifest: dict[str, Any], base_path: Path) -> list[CheckResult]:
    results: list[CheckResult] = []
    for stage, spec in manifest["stages"].items():
        for section in ("inputs", "outputs"):
            entries = spec.get(section, []) or []
            if not isinstance(entries, list):
                results.append(CheckResult("error", stage, section, "section must be a list"))
                continue
            for entry in entries:
                if not isinstance(entry, dict):
                    results.append(CheckResult("error", stage, section, "entry must be a mapping"))
                    continue
                results.extend(validate_entry(base_path, stage, entry, section))
    return results


def check_python_version() -> CheckResult:
    version = sys.version_info
    if version < (3, 10):
        return CheckResult("error", "environment", "python", "Python 3.10+ is required")
    return CheckResult("ok", "environment", "python", platform.python_version())


def check_optional_tools(manifest: dict[str, Any]) -> list[CheckResult]:
    results: list[CheckResult] = []
    for tool in manifest.get("optional_tools", []) or []:
        command = tool.get("command")
        name = tool.get("name", command)
        if not command:
            continue
        found = shutil.which(command)
        level = "ok" if found else "warning"
        message = found or "not found on PATH"
        results.append(CheckResult(level, "environment", str(name), message))
    return results


def print_text(results: list[CheckResult]) -> None:
    for result in results:
        prefix = result.level.upper()
        print(f"{prefix}: [{result.stage}] {result.path}: {result.message}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Check BTC-premia reproducibility inputs")
    parser.add_argument("--manifest", type=Path, default=REPO_ROOT / "config" / "data_manifest.yaml")
    parser.add_argument("--base-path", type=Path, default=REPO_ROOT)
    parser.add_argument("--strict", action="store_true", help="Fail when required files are missing")
    parser.add_argument("--json", action="store_true", help="Emit machine-readable JSON")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    base_path = args.base_path.expanduser().resolve()
    manifest = load_manifest(args.manifest.expanduser().resolve())

    results = [check_python_version()]
    results.extend(check_optional_tools(manifest))
    results.extend(validate_manifest(manifest, base_path))

    if args.json:
        print(json.dumps([asdict(result) for result in results], indent=2))
    else:
        print_text(results)

    hard_fail = any(result.level in {"error", "missing"} for result in results)
    if hard_fail and args.strict:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
