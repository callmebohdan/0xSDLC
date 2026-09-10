"""End-to-end route tests using a deterministic local adapter."""

from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CLI = ROOT / "scripts" / "0xSDLC.py"
FAKE = ROOT / "tests" / "fake_adapter.py"


class EndToEndTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.base = Path(self.temp.name)
        self.workspace = self.base / "workspace"
        self.workspace.mkdir()
        (self.workspace / "AGENTS.md").write_text("# Test project\n\nRun deterministic checks.\n", encoding="utf-8")
        self.env = os.environ.copy()
        self.env["0XSDLC_AGENTS_HOME"] = str(self.base / "agents" / "0xsdlc")
        self.env["0XSDLC_GENERIC_COMMAND"] = (
            f"{sys.executable} {FAKE} --prompt-file {{prompt_file}} --output-dir {{output_dir}} "
            "--output-artifact {output_artifact} --telemetry-file {telemetry_file}"
        )

    def tearDown(self) -> None:
        self.temp.cleanup()

    def run_cli(self, *arguments: str, mode: str = "complete") -> subprocess.CompletedProcess[str]:
        env = {**self.env, "0XSDLC_FAKE_MODE": mode}
        return subprocess.run([sys.executable, str(CLI), *arguments], cwd=self.workspace, env=env, capture_output=True, text=True, check=False)

    def test_canonical_entry_point_is_available(self) -> None:
        result = subprocess.run(
            [sys.executable, str(CLI), "--help"],
            cwd=self.workspace,
            env=self.env,
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("usage: 0xSDLC", result.stdout)

    def latest_task(self) -> Path:
        tasks = list((Path(self.env["0XSDLC_AGENTS_HOME"]) / "sessions").iterdir())
        self.assertTrue(tasks)
        return max(tasks, key=lambda path: path.stat().st_mtime_ns)

    @staticmethod
    def route(task: Path) -> dict:
        return json.loads((task / "route.json").read_text(encoding="utf-8"))

    def test_complete_cycle_and_telemetry(self) -> None:
        result = self.run_cli("autopilot", "fix local label", "--kind", "small", "--workspace", str(self.workspace), "--execute", "--full")
        self.assertEqual(result.returncode, 0, result.stderr)
        route = self.route(self.latest_task())
        self.assertEqual(route["status"], "completed")
        self.assertEqual(route["telemetry"]["calls"], 6)
        self.assertGreater(route["telemetry"]["input_tokens"], 0)

    def test_blocked_artifact_stops(self) -> None:
        result = self.run_cli("autopilot", "fix local label", "--kind", "small", "--workspace", str(self.workspace), "--execute", "--full", mode="blocked")
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(self.route(self.latest_task())["status"], "blocked")

    def test_approval_and_resume(self) -> None:
        result = self.run_cli("autopilot", "change authentication", "--kind", "high-risk", "--workspace", str(self.workspace), "--execute", "--full")
        self.assertEqual(result.returncode, 0, result.stderr)
        task = self.latest_task()
        self.assertEqual(self.route(task)["status"], "needs-approval")
        resumed = self.run_cli("resume", task.name, "--approve", "reviewed test scope", "--execute", "--full")
        self.assertEqual(resumed.returncode, 0, resumed.stderr)
        self.assertEqual(self.route(task)["status"], "completed")

    def test_adapter_crash_is_preserved(self) -> None:
        result = self.run_cli("autopilot", "fix local label", "--kind", "small", "--workspace", str(self.workspace), "--execute", "--full", mode="crash")
        self.assertEqual(result.returncode, 17)
        task = self.latest_task()
        self.assertEqual(self.route(task)["status"], "blocked")
        self.assertIn("simulated provider process crash", (task / "adapter-audit.stderr.txt").read_text(encoding="utf-8"))

    def test_invalid_artifact_is_rejected(self) -> None:
        result = self.run_cli("autopilot", "fix local label", "--kind", "small", "--workspace", str(self.workspace), "--execute", "--full", mode="invalid")
        self.assertEqual(result.returncode, 3)
        self.assertIn("invalid required artifact", self.route(self.latest_task())["phase_states"]["audit"]["reason"])

    def test_fix_loop_preserves_numbered_artifacts(self) -> None:
        result = self.run_cli("autopilot", "fix local label", "--kind", "small", "--workspace", str(self.workspace), "--execute", "--full", mode="fix-loop")
        self.assertEqual(result.returncode, 0, result.stderr)
        task, route = self.latest_task(), None
        route = self.route(task)
        self.assertEqual(route["fix_attempts"], 1)
        for name in ("review.md", "fix-report-1.md", "test-report-1.md", "review-1.md"):
            self.assertTrue((task / name).is_file(), name)

    def test_interrupted_phase_recovers_on_resume(self) -> None:
        prepared = self.run_cli("autopilot", "fix local label", "--kind", "small", "--workspace", str(self.workspace))
        self.assertEqual(prepared.returncode, 0, prepared.stderr)
        task = self.latest_task()
        route = self.route(task)
        route.update({"status": "running", "current_phase": "audit"})
        route["phase_states"]["audit"]["status"] = "running"
        (task / "route.json").write_text(json.dumps(route), encoding="utf-8")
        resumed = self.run_cli("resume", task.name, "--execute", "--full")
        self.assertEqual(resumed.returncode, 0, resumed.stderr)
        route = self.route(task)
        self.assertEqual(route["status"], "completed")
        self.assertTrue(any(event["event"] == "run-interrupted" for event in route["events"]))

    def test_audit_can_add_design_and_approval(self) -> None:
        result = self.run_cli("autopilot", "add reporting feature", "--kind", "standard", "--without-design", "--workspace", str(self.workspace), "--execute", "--full", mode="route-upgrade")
        self.assertEqual(result.returncode, 0, result.stderr)
        route = self.route(self.latest_task())
        self.assertIn("design", route["phases"])
        self.assertIn("approval", route["phases"])
        self.assertEqual(route["status"], "needs-approval")
        self.assertTrue(any(event["event"] == "route-changed" and event["reason"] == "audit found cross-boundary impact" for event in route["events"]))

    def test_missing_agents_uses_local_context_and_bootstrap_requires_approval(self) -> None:
        (self.workspace / "AGENTS.md").unlink()
        (self.workspace / "README.md").write_text("# Demo\n\nA small evidence-based project.\n", encoding="utf-8")
        prepared = self.run_cli("autopilot", "add reporting feature", "--kind", "standard", "--workspace", str(self.workspace))
        self.assertEqual(prepared.returncode, 0, prepared.stderr)
        task = self.latest_task()
        self.assertTrue((task / "project-context.md").is_file())
        self.assertTrue(any(event["event"] == "project-instructions-missing" for event in self.route(task)["events"]))
        drafted = self.run_cli("bootstrap", "--workspace", str(self.workspace))
        self.assertEqual(drafted.returncode, 0, drafted.stderr)
        self.assertFalse((self.workspace / "AGENTS.md").exists())
        bootstrap_task = self.latest_task()
        adopted = self.run_cli("bootstrap", "--adopt", bootstrap_task.name, "--approve", "reviewed test draft")
        self.assertEqual(adopted.returncode, 0, adopted.stderr)
        self.assertTrue((self.workspace / "AGENTS.md").is_file())


if __name__ == "__main__":
    unittest.main()
