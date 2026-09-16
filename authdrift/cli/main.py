import argparse
import runpy
import sys
from pathlib import Path

from authdrift import run


def main(argv=None):
    parser = argparse.ArgumentParser(prog="authdrift")
    commands = parser.add_subparsers(dest="command", required=True)
    command = commands.add_parser("run", help="execute a trusted local scenario file")
    command.add_argument("scenario", type=Path)
    command.add_argument("--repeats", type=int, default=1)
    command.add_argument("--json", type=Path, default=Path("authdrift-results.json"))
    args = parser.parse_args(argv)
    try:
        namespace = runpy.run_path(str(args.scenario.resolve()))
        source = namespace.get("build_scenario", namespace.get("scenario"))
        if source is None:
            raise ValueError("scenario file must export build_scenario() or scenario")
        report = run(source, repeats=args.repeats, json_path=args.json)
        print(f"Evidence: {args.json}")
        return {"CLOSED": 0, "REVOCATION_ESCAPE": 1,
                "BASELINE_FAILURE": 2, "INVALID_EXPERIMENT": 3}[report["result"]]
    except Exception as exc:
        print(f"authdrift: {exc}", file=sys.stderr)
        return 3


if __name__ == "__main__":
    raise SystemExit(main())
