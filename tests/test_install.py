"""Installer regression checks for replacement rollouts."""

from __future__ import annotations

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
INSTALLER = ROOT / "scripts" / "install.py"


class InstallTests(unittest.TestCase):
    def test_force_removes_stale_published_files_but_preserves_sessions(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            base = Path(directory)
            runtime = base / "runtime"
            destinations = {
                "--codex-skills-dir": base / "codex",
                "--claude-skills-dir": base / "claude",
                "--cursor-skills-dir": base / "cursor",
                "--shared-skills-dir": base / "shared",
            }
            arguments = [sys.executable, str(INSTALLER), "--agents-dir", str(runtime)]
            for option, destination in destinations.items():
                arguments.extend((option, str(destination)))

            first = subprocess.run(arguments, cwd=ROOT, capture_output=True, text=True, check=False)
            self.assertEqual(first.returncode, 0, first.stderr)

            stale_runtime = runtime / "scripts" / "0xsdlc.py"
            stale_runtime.write_text("stale", encoding="utf-8")
            session_marker = runtime / "sessions" / "existing-task" / "route.json"
            session_marker.parent.mkdir(parents=True)
            session_marker.write_text("{}", encoding="utf-8")
            stale_skill = destinations["--codex-skills-dir"] / "0xsdlc-autopilot" / "stale.txt"
            stale_skill.write_text("stale", encoding="utf-8")

            second = subprocess.run([*arguments, "--force"], cwd=ROOT, capture_output=True, text=True, check=False)
            self.assertEqual(second.returncode, 0, second.stderr)
            installed_script_names = {path.name for path in (runtime / "scripts").iterdir()}
            self.assertIn("0xSDLC.py", installed_script_names)
            self.assertNotIn("0xsdlc.py", installed_script_names)
            self.assertTrue(session_marker.is_file())
            self.assertFalse(stale_skill.exists())


if __name__ == "__main__":
    unittest.main()
