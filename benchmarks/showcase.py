"""Reproduce the six trusted, synthetic fixtures and retain reviewable evidence.

Run from a checkout: python benchmarks/showcase.py --output results/showcase
This runs repository-owned Python, not arbitrary downloaded scenarios.
"""
import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import platform
import runpy
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from authdrift import run


def validate_report(report, expected, repeats):
    """Do not mistake skipped/invalid trials or broken controls for success."""
    expected_escapes = repeats if expected == "REVOCATION_ESCAPE" else 0
    if (report.get("result") != expected or report.get("repeats") != repeats
            or report.get("valid_trials") != repeats
            or report.get("escapes") != expected_escapes
            or len(report.get("trials", [])) != repeats):
        return False
    for trial in report["trials"]:
        experiments = trial.get("experiments", [])
        if trial.get("result") != expected or len(experiments) != 3:
            return False
        if [e.get("experiment") for e in experiments] != ["positive", "negative", "mid_flight"]:
            return False
        if [e.get("result") for e in experiments] != ["PASS", "PASS", expected]:
            return False
        if [e.get("committed") for e in experiments] != [True, False, expected == "REVOCATION_ESCAPE"]:
            return False
    return True


def git_value(*args):
    result = subprocess.run(["git", "-C", str(ROOT), *args], capture_output=True, text=True)
    return result.stdout.strip() if result.returncode == 0 else "unavailable"


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=ROOT / "results" / "showcase")
    parser.add_argument("--repeats", type=int, default=20)
    args = parser.parse_args(argv)
    if args.repeats < 1:
        parser.error("--repeats must be positive")
    args.output.mkdir(parents=True, exist_ok=True)
    # Refuse to silently replace a previously recorded evidence bundle.
    if any(args.output.iterdir()):
        parser.error("output must be an empty directory; choose a new run directory")
    sources = sorted((ROOT / "authdrift").rglob("*.py"))
    sources += sorted((ROOT / "examples").rglob("*.py")) + [Path(__file__).resolve()]
    manifest = {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "source_commit": git_value("rev-parse", "HEAD"),
        "working_tree_dirty": bool(git_value("status", "--porcelain")),
        "python": platform.python_version(),
        "platform": platform.platform(),
        "scope": "Synthetic in-memory fixtures; not production or independent vulnerability findings",
        "source_sha256": {p.relative_to(ROOT).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest() for p in sources},
        "results": [],
    }
    for family in ("refund", "delegation", "session"):
        for variant, expected in (("scenario", "REVOCATION_ESCAPE"), ("safe", "CLOSED")):
            factory = runpy.run_path(str(ROOT / "examples" / family / (variant + ".py")))["build_scenario"]
            filename = f"{family}-{variant}.json"
            report = run(factory, repeats=args.repeats, quiet=True, json_path=args.output / filename)
            manifest["results"].append({
                "fixture": f"{family}/{variant}", "expected": expected,
                "observed": report["result"], "valid_trials": report["valid_trials"],
                "escapes": report["escapes"], "repeats": args.repeats,
                "verified": validate_report(report, expected, args.repeats), "evidence": filename,
            })
    manifest["all_verified"] = all(row["verified"] for row in manifest["results"])
    (args.output / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    lines = ["# AuthDrift fixture reproduction", "", manifest["scope"], "",
             f"Python {manifest['python']}; source commit `{manifest['source_commit']}`.",
             "Source hashes and working-tree state are recorded in manifest.json.", "",
             "| Fixture | Outcome | Escapes / valid trials | Verified controls |",
             "| --- | --- | --- | --- |"]
    for row in manifest["results"]:
        lines.append(f"| {row['fixture']} | {row['observed']} | {row['escapes']}/{row['valid_trials']} | {row['verified']} |")
    (args.output / "SUMMARY.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines))
    return 0 if manifest["all_verified"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
