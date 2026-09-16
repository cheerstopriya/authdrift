"""Run from the repository root: python benchmarks/run.py."""
import json
import platform
from pathlib import Path
import runpy
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from authdrift import run

reports = {}
for domain in ("refund", "delegation", "session"):
    for variant in ("scenario", "safe"):
        factory = runpy.run_path(str(ROOT / "examples" / domain / f"{variant}.py"))["build_scenario"]
        reports[f"{domain}/{variant}"] = run(factory, repeats=20, quiet=True)
output = ROOT / "benchmarks" / "results.json"
output.write_text(json.dumps({"python": platform.python_version(),
                             "platform": platform.platform(), "reports": reports}, indent=2) + "\n")
for name, report in reports.items():
    print(f"{name}: {report['escapes']}/{report['valid_trials']} escapes")
print(output)
