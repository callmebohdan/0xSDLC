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
            self.assertIn("<project-root>/.agents/0xSDLC/sessions", (runtime / "AGENTS.md").read_text(encoding="utf-8"))
            for skill_root in destinations.values():
                autopilot = (skill_root / "0xsdlc-autopilot" / "SKILL.md").read_text(encoding="utf-8")
                phase_agent = (skill_root / "0xsdlc-agent" / "SKILL.md").read_text(encoding="utf-8")
                bootstrap = (skill_root / "0xsdlc-bootstrap" / "SKILL.md").read_text(encoding="utf-8")
                self.assertIn("<project-root>/.agents/0xSDLC/sessions", autopilot)
                self.assertIn("nearest nested `AGENTS.md`", autopilot)
                self.assertIn("<project-root>/.agents/0xSDLC/sessions", phase_agent)
                self.assertIn("nearest nested instruction files", phase_agent)
                self.assertIn("init --check", bootstrap)
                self.assertIn("<project-root>/.agents/0xSDLC/sessions", bootstrap)

            stale_runtime = runtime / "scripts" / "0xsdlc.py"
            stale_runtime.write_text("stale", encoding="utf-8")
            custom_runtime_file = runtime / "user-note.txt"
            custom_runtime_file.write_text("keep", encoding="utf-8")
            session_marker = runtime / "sessions" / "existing-task" / "route.json"
            session_marker.parent.mkdir(parents=True)
            session_marker.write_text("{}", encoding="utf-8")
            project_session = base / "repo" / ".agents" / "0xSDLC" / "sessions" / "task" / "route.json"
            project_session.parent.mkdir(parents=True)
            project_session.write_text("{}", encoding="utf-8")
            stale_skill = destinations["--codex-skills-dir"] / "0xsdlc-autopilot" / "stale.txt"
            stale_skill.write_text("stale", encoding="utf-8")
            sibling_skill = destinations["--codex-skills-dir"] / "my-other-skill" / "SKILL.md"
            sibling_skill.parent.mkdir(parents=True)
            sibling_skill.write_text("keep", encoding="utf-8")

            second = subprocess.run([*arguments, "--force"], cwd=ROOT, capture_output=True, text=True, check=False)
            self.assertEqual(second.returncode, 0, second.stderr)
            installed_script_names = {path.name for path in (runtime / "scripts").iterdir()}
            self.assertIn("0xSDLC.py", installed_script_names)
            self.assertNotIn("0xsdlc.py", installed_script_names)
            self.assertTrue(session_marker.is_file())
            self.assertTrue(custom_runtime_file.is_file())
            self.assertTrue(project_session.is_file())
            self.assertTrue(sibling_skill.is_file())
            self.assertFalse(stale_skill.exists())

    def test_provider_conflict_is_found_before_runtime_changes(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            base = Path(directory)
            runtime = base / "runtime"
            codex = base / "codex"
            (codex / "0xsdlc-agent").mkdir(parents=True)
            arguments = [
                sys.executable, str(INSTALLER), "--agents-dir", str(runtime),
                "--codex-skills-dir", str(codex), "--claude-skills-dir", str(base / "claude"),
                "--cursor-skills-dir", str(base / "cursor"), "--portable-skills-dir", str(base / "shared"),
            ]
            result = subprocess.run(arguments, cwd=ROOT, capture_output=True, text=True, check=False)
            self.assertEqual(result.returncode, 2)
            self.assertFalse(runtime.exists())
            self.assertIn("already exist", result.stderr)
            upgraded = subprocess.run([*arguments, "--upgrade"], cwd=ROOT, capture_output=True, text=True, check=False)
            self.assertEqual(upgraded.returncode, 0, upgraded.stderr)
            self.assertTrue((runtime / "scripts" / "0xSDLC.py").is_file())


if __name__ == "__main__":
    unittest.main()
