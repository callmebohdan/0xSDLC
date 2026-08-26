"""Cross-platform convenience entry point for the 0xSDLC autopilot command."""

from __future__ import annotations

import runpy
import sys
from pathlib import Path


target = Path(__file__).with_name("0xsdlc.py")
sys.argv = [str(target), "autopilot", *sys.argv[1:]]
runpy.run_path(str(target), run_name="__main__")
