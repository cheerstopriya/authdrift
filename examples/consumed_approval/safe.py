"""Corrected synchronous version of the consumed-approval fixture."""
from pathlib import Path
import runpy

_build = runpy.run_path(str(Path(__file__).with_name("scenario.py")))["build_scenario"]


def build_scenario():
    return _build(safe=True)
