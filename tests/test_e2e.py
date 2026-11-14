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
        self.env.pop("0XSDLC_SESSIONS_ROOT", None)
        self.env["0XSDLC_GENERIC_COMMAND"] = (
            f'"{sys.executable}" "{FAKE}" --prompt-file "{{prompt_file}}" --output-dir "{{output_dir}}" '
            '--output-artifact "{output_artifact}" --telemetry-file "{telemetry_file}"'
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
        tasks = list((self.workspace / ".agents" / "0xsdlc" / "sessions").iterdir())
        self.assertTrue(tasks)
        return max(tasks, key=lambda path: path.stat().st_mtime_ns)

    @staticmethod
    def route(task: Path) -> dict:
        return json.loads((task / "route.json").read_text(encoding="utf-8"))

    @staticmethod
    def metrics(task: Path) -> list[dict]:
        return [json.loads(line) for line in (task / "metrics.jsonl").read_text(encoding="utf-8").splitlines()]

    def test_complete_cycle_and_telemetry(self) -> None:
        result = self.run_cli("autopilot", "fix local label", "--kind", "small", "--workspace", str(self.workspace), "--execute", "--full")
        self.assertEqual(result.returncode, 0, result.stderr)
        route = self.route(self.latest_task())
        self.assertEqual(route["status"], "completed")
        self.assertEqual(route["telemetry"]["calls"], 6)
        self.assertGreater(route["telemetry"]["input_tokens"], 0)
        self.assertTrue((self.latest_task() / "project-profile.json").is_file())

    def test_adapter_cannot_complete_unverified_route(self) -> None:
        result = self.run_cli("autopilot", "fix local label", "--kind", "small", "--execute", "--full", mode="unverified")
        self.assertEqual(result.returncode, 3, result.stderr)
        route = self.route(self.latest_task())
        self.assertEqual(route["status"], "blocked")
        self.assertEqual(route["current_phase"], "verify")
        self.assertIn("requires status: verified", route["phase_states"]["verify"]["reason"])

    def test_native_cannot_complete_unverified_route(self) -> None:
        result = self.run_cli("autopilot", "verify this change", "--native", "--phase", "verify")
        self.assertEqual(result.returncode, 0, result.stderr)
        task = self.latest_task()
        result = self.run_cli("native", "open", task.name, "verify")
        self.assertEqual(result.returncode, 0, result.stderr)
        opened = json.loads(result.stdout)
        artifact = Path(opened["artifact"])
        report = f'---\nschema_version: "0.2"\ntask_id: "{task.name}"\nphase: verify\nstatus: '
        close = ("native", "close", task.name, opened["attempt_id"], "--outcome", "succeeded")
        artifact.write_text(report + "ready\n---\n\nNo proof.\n", encoding="utf-8")
        result = self.run_cli(*close)
        self.assertEqual(result.returncode, 2, result.stderr)
        self.assertIn("requires status: verified", result.stderr)
        self.assertEqual(self.route(task)["status"], "running")
        artifact.write_text(report + "verified\n---\n\nProof recorded.\n", encoding="utf-8")
        result = self.run_cli(*close)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(self.route(task)["status"], "completed")

    def test_session_root_precedence_and_contract_lookup(self) -> None:
        contracts = Path(self.env["0XSDLC_AGENTS_HOME"]) / "templates"
        contracts.mkdir(parents=True)
        (contracts / "brief.md").write_text("Custom contract: {{request}}\n", encoding="utf-8")
        env_root, flag_root = self.base / "environment sessions", self.base / "flag sessions"
        self.env["0XSDLC_SESSIONS_ROOT"] = str(env_root)
        for root, flags in ((env_root, ()), (flag_root, ("--sessions-root", str(flag_root)))):
            result = self.run_cli("autopilot", "fix label", "--model", "generic", *flags)
            self.assertEqual(result.returncode, 0, result.stderr)
            task, = root.iterdir()
            self.assertIn("Custom contract: fix label", (task / "brief.md").read_text(encoding="utf-8"))
            self.assertIn(task.name, self.run_cli("status", *flags).stdout)
            result = self.run_cli("resume", task.name, "--full", "--execute", *flags)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(self.route(task)["status"], "completed")
        self.assertFalse((contracts.parent / "sessions").exists())

    def test_project_local_default_and_legacy_task_lookup(self) -> None:
        result = self.run_cli("autopilot", "fix project label", "--model", "generic")
        self.assertEqual(result.returncode, 0, result.stderr)
        task = self.latest_task()
        self.assertEqual(task.parent, self.workspace / ".agents" / "0xsdlc" / "sessions")
        self.assertIn(task.name, self.run_cli("status").stdout)

        legacy_root = Path(self.env["0XSDLC_AGENTS_HOME"]) / "sessions"
        legacy_root.mkdir(parents=True)
        legacy_task = legacy_root / task.name
        task.rename(legacy_task)
        self.assertIn(task.name, self.run_cli("status").stdout)
        result = self.run_cli("resume", task.name)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn(str(legacy_task).casefold(), result.stdout.casefold())

    def test_nested_workspace_uses_repository_root_for_sessions(self) -> None:
        nested = self.workspace / "packages" / "app"
        nested.mkdir(parents=True)
        (self.workspace / ".git").mkdir()
        result = self.run_cli("autopilot", "fix nested label", "--model", "generic", "--workspace", str(nested))
        self.assertEqual(result.returncode, 0, result.stderr)
        task = self.latest_task()
        self.assertEqual(task.parent, self.workspace / ".agents" / "0xsdlc" / "sessions")

    def test_unwritable_session_root_fails_before_adapter(self) -> None:
        blocked = self.base / "file instead of directory"
        blocked.touch()
        result = self.run_cli("autopilot", "fix label", "--sessions-root", str(blocked), "--execute", mode="crash")
        self.assertEqual(result.returncode, 2)
        self.assertIn(str(blocked).casefold(), result.stderr.casefold())
        self.assertIn("0XSDLC_SESSIONS_ROOT", result.stderr)
        self.assertNotIn("Task:", result.stdout)

    def test_unknown_and_measured_zero_usage(self) -> None:
        for mode, output in (("no-usage", None), ("partial-usage", 0)):
            result = self.run_cli("autopilot", f"fix label {mode}", "--execute", mode=mode)
            self.assertEqual(result.returncode, 0, result.stderr)
            task = self.latest_task()
            call, = self.metrics(task)
            summary = self.route(task)["telemetry"]
            for data in (call, summary):
                self.assertIsNone(data["input_tokens"])
                self.assertIsNone(data["cost_usd"])
                self.assertEqual(data["output_tokens"], output)
                self.assertEqual(data["cache_read_tokens"], output)
                self.assertEqual(data["inference_ms"], output)
            self.assertEqual(summary["coverage"]["output_tokens"], int(output is not None))
            self.assertEqual(summary["coverage"]["duration_ms"], 1)

    def test_retry_preserves_attempts_and_rejects_stale_usage(self) -> None:
        result = self.run_cli("autopilot", "fix label", "--execute", "--full", "--parallel-checks", mode="blocked")
        self.assertEqual(result.returncode, 3, result.stderr)
        task = self.latest_task()
        first = next(event for event in self.metrics(task) if event["lane"] == "primary")
        first_logs = {key: (task / first["evidence"][key]).read_bytes() for key in ("prompt", "stdout", "stderr", "artifact")}
        result = self.run_cli("resume", task.name, "--execute", "--full", mode="stale-usage")
        self.assertEqual(result.returncode, 0, result.stderr)
        route = self.route(task)
        attempts = route["phase_states"]["audit"]["attempt_history"]
        calls = {event["call_id"]: event for event in self.metrics(task)}
        self.assertEqual([attempt["outcome"] for attempt in attempts], ["blocked", "succeeded"])
        for attempt in attempts:
            self.assertLessEqual(attempt["started_at"], attempt["finished_at"])
            call = calls[attempt["call_ids"][0]]
            self.assertEqual(call["attempt_id"], attempt["attempt_id"])
            self.assertGreaterEqual(attempt["duration_ms"], call["duration_ms"])
        second = calls[attempts[1]["call_ids"][0]]
        self.assertEqual(len(attempts[1]["call_ids"]), 3)
        self.assertNotEqual(first["call_id"], second["call_id"])
        self.assertIsNone(second["input_tokens"])
        self.assertIn("does not match", second["telemetry_warning"])
        for key, content in first_logs.items():
            self.assertNotEqual(first["evidence"][key], second["evidence"][key])
            self.assertEqual((task / first["evidence"][key]).read_bytes(), content)
        self.assertEqual(route["telemetry"]["input_tokens"], 20)
        self.assertEqual(route["telemetry"]["coverage"]["input_tokens"], 2)
        self.assertEqual(self.run_cli("resume", task.name).returncode, 0)
        self.assertEqual(self.route(task)["telemetry"], route["telemetry"])

    def test_repair_resume_keeps_the_same_repair_budget(self) -> None:
        result = self.run_cli("autopilot", "fix label", "--execute", "--full", mode="repair-crash")
        self.assertEqual(result.returncode, 17, result.stderr)
        task = self.latest_task()
        before = self.route(task)
        self.assertEqual(before["active_repair"]["phase"], "fix")
        result = self.run_cli("resume", task.name, "--execute", "--full")
        self.assertEqual(result.returncode, 0, result.stderr)
        after = self.route(task)
        self.assertEqual(after["status"], "completed")
        self.assertNotIn("active_repair", after)
        self.assertEqual(after["fix_attempts"], 1)
        history = after["phase_states"]["fix"]["attempt_history"]
        self.assertEqual([attempt["outcome"] for attempt in history], ["failed", "succeeded"])
        self.assertNotEqual(history[0]["artifacts"], history[1]["artifacts"])

    def test_native_chat_records_elapsed_and_unknown_interrupted_end(self) -> None:
        result = self.run_cli("autopilot", "audit this change", "--native", "--phase", "audit")
        self.assertEqual(result.returncode, 0, result.stderr)
        task = self.latest_task()
        result = self.run_cli("native", "open", task.name, "audit")
        self.assertEqual(result.returncode, 0, result.stderr)
        first = json.loads(result.stdout)
        result = self.run_cli("native", "interrupt", task.name, first["attempt_id"])
        self.assertEqual(result.returncode, 0, result.stderr)
        result = self.run_cli("native", "open", task.name, "audit")
        self.assertEqual(result.returncode, 0, result.stderr)
        second = json.loads(result.stdout)
        self.assertNotEqual(first["artifact"], second["artifact"])
        Path(second["artifact"]).write_text(
            f'---\nschema_version: "0.2"\ntask_id: "{task.name}"\nphase: audit\nstatus: ready\n---\n\n# Evidence\n',
            encoding="utf-8",
        )
        result = self.run_cli("native", "close", task.name, second["attempt_id"], "--outcome", "succeeded")
        self.assertEqual(result.returncode, 0, result.stderr)
        route = self.route(task)
        interrupted, closed = route["phase_states"]["audit"]["attempt_history"]
        self.assertEqual((interrupted["outcome"], interrupted["provenance"]), ("interrupted", "retrospective"))
        self.assertIsNone(interrupted["finished_at"])
        self.assertIsNone(interrupted["duration_ms"])
        self.assertEqual(route["status"], "completed")
        self.assertGreaterEqual(closed["duration_ms"], 0)
        self.assertLessEqual(closed["started_at"], closed["finished_at"])
        for field in ("inference_ms", "adapter_wall_ms", "cost_usd", "input_tokens", "output_tokens"):
            self.assertIsNone(closed[field])
        self.assertEqual(closed["call_ids"], [])
        self.assertEqual(self.run_cli("resume", task.name, "--execute", "--full").returncode, 2)

    def test_legacy_metrics_are_kept_separate_and_recovery_reports_cannot_resume(self) -> None:
        self.assertEqual(self.run_cli("autopilot", "fix label").returncode, 0)
        task = self.latest_task()
        route = self.route(task)
        old_metrics = {"calls": 2, "duration_ms": 25, "input_tokens": 24, "output_tokens": 16, "cost_usd": 0.02}
        route["telemetry"] = old_metrics
        route_path, metrics_path = task / "route.json", task / "metrics.jsonl"
        route_path.write_text(json.dumps(route), encoding="utf-8")
        original = '{"phase":"audit","duration_ms":25}\n'
        metrics_path.write_text(original, encoding="utf-8")
        result = self.run_cli("resume", task.name)
        self.assertEqual(result.returncode, 0, result.stderr)
        route = self.route(task)
        self.assertEqual(route["legacy_telemetry"], old_metrics)
        self.assertIsNone(route["telemetry"]["input_tokens"])
        self.assertEqual(metrics_path.read_text(encoding="utf-8"), original)
        route["provenance"] = "retrospective"
        route_path.write_text(json.dumps(route), encoding="utf-8")
        result = self.run_cli("resume", task.name, "--execute", "--full")
        self.assertEqual(result.returncode, 2)
        self.assertIn("retrospective", result.stderr)
        self.assertEqual(self.route(task), route)

    def test_assessment_route_never_implements_or_runs_product_tests(self) -> None:
        result = self.run_cli(
            "autopilot", "Assess this harness for missing coverage", "--workspace", str(self.workspace),
            "--execute", "--full",
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        task = self.latest_task()
        route = self.route(task)
        self.assertEqual(route["mode"], "assessment")
        self.assertNotIn("implement", route["phases"])
        self.assertNotIn("test", route["phases"])
        self.assertEqual(route["status"], "completed")
        self.assertEqual(route["telemetry"]["calls"], 5)

    def test_diagnosis_route_is_read_only(self) -> None:
        result = self.run_cli(
            "autopilot", "Why is the report endpoint broken?", "--workspace", str(self.workspace),
            "--execute", "--full",
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        route = self.route(self.latest_task())
        self.assertEqual(route["mode"], "diagnose")
        self.assertNotIn("implement", route["phases"])
        self.assertEqual(route["telemetry"]["calls"], 4)

    def test_diagnosis_failure_is_recorded_without_auto_fix(self) -> None:
        result = self.run_cli(
            "autopilot", "Why is the report endpoint broken?", "--workspace", str(self.workspace),
            "--execute", "--full", mode="test-failure",
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        task = self.latest_task()
        route = self.route(task)
        self.assertEqual(route["status"], "needs-review")
        self.assertNotIn("implement", route["phases"])
        self.assertFalse((task / "fix-report-1.md").exists())

    def test_failed_test_enters_bounded_fix_test_review_loop(self) -> None:
        result = self.run_cli(
            "autopilot", "fix local label", "--kind", "small", "--workspace", str(self.workspace),
            "--execute", "--full", mode="test-failure",
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        task = self.latest_task()
        route = self.route(task)
        self.assertEqual(route["status"], "completed")
        self.assertEqual(route["fix_attempts"], 1)
        self.assertEqual(route["telemetry"]["calls"], 8)
        self.assertTrue(any(event["event"] == "repair-loop-started" and event["source_phase"] == "test" for event in route["events"]))
        for name in ("test-report.md", "fix-report-1.md", "test-report-1.md", "review-1.md"):
            self.assertTrue((task / name).is_file(), name)

    def test_quality_control_is_opt_in_and_runs_after_review(self) -> None:
        result = self.run_cli(
            "autopilot", "fix local label", "--kind", "small", "--workspace", str(self.workspace),
            "--execute", "--full", "--quality-control",
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        task = self.latest_task()
        route = self.route(task)
        self.assertIn("quality-control", route["phases"])
        self.assertEqual(route["telemetry"]["calls"], 7)
        self.assertTrue((task / "quality-report.md").is_file())

    def test_maintainability_review_adds_lane_and_shared_synthesis(self) -> None:
        (self.workspace / "main.cpp").write_text("int main() { return 0; }\n", encoding="utf-8")
        result = self.run_cli(
            "autopilot",
            "refactor reusable parser",
            "--kind",
            "small",
            "--workspace",
            str(self.workspace),
            "--execute",
            "--full",
            "--maintainability-review",
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        task = self.latest_task()
        route = self.route(task)
        self.assertTrue(route["routing"]["maintainability_review"])
        self.assertEqual(route["telemetry"]["calls"], 8)
        self.assertTrue((task / "review-maintainability.md").is_file())
        self.assertTrue((task / "review-synthesis.md").is_file())
        call = next(event for event in self.metrics(task) if event["lane"] == "maintainability")
        prompt = (task / call["evidence"]["prompt"]).read_text(encoding="utf-8")
        self.assertIn("# C++ engineering profile", prompt)
        self.assertIn("# Maintainability review lane", prompt)

    def test_parallel_and_maintainability_reviews_share_one_synthesis(self) -> None:
        result = self.run_cli(
            "autopilot",
            "refactor reusable parser",
            "--kind",
            "small",
            "--workspace",
            str(self.workspace),
            "--execute",
            "--full",
            "--parallel-checks",
            "--maintainability-review",
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        task = self.latest_task()
        route = self.route(task)
        self.assertEqual(route["telemetry"]["calls"], 11)
        synthesis = route["phase_states"]["review"]["lanes"]["synthesis"]
        self.assertEqual(
            synthesis["inputs"],
            ["review.md", "review-secondary.md", "review-maintainability.md"],
        )
        attempt, = route["phase_states"]["review"]["attempt_history"]
        calls = [event for event in self.metrics(task) if event["attempt_id"] == attempt["attempt_id"]]
        self.assertEqual({event["lane"] for event in calls}, {"primary", "secondary", "maintainability", "review"})
        self.assertEqual(set(attempt["call_ids"]), {event["call_id"] for event in calls})
        self.assertGreaterEqual(attempt["duration_ms"], max(event["duration_ms"] for event in calls))
        self.assertTrue(all((task / event["evidence"]["artifact"]).is_file() for event in calls))

    def test_blocked_artifact_stops(self) -> None:
        result = self.run_cli("autopilot", "fix local label", "--kind", "small", "--workspace", str(self.workspace), "--execute", "--full", mode="blocked")
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(self.route(self.latest_task())["status"], "blocked")

    def test_needs_review_artifact_is_not_misreported_as_approval(self) -> None:
        result = self.run_cli("autopilot", "fix local label", "--kind", "small", "--workspace", str(self.workspace), "--execute", "--full", mode="needs-review")
        self.assertEqual(result.returncode, 0, result.stderr)
        route = self.route(self.latest_task())
        self.assertEqual(route["status"], "needs-review")
        self.assertEqual(route["phase_states"]["audit"]["status"], "needs-review")
        self.assertNotEqual(route["status"], "needs-approval")
        task = self.latest_task()
        resumed = self.run_cli("resume", task.name, "--execute", "--full", "--resolve-review", "Reviewed the finding", mode="complete")
        self.assertEqual(resumed.returncode, 0, resumed.stderr)
        self.assertTrue((task / "audit-before-human-resolution.md").is_file())
        self.assertEqual(self.route(task)["status"], "completed")

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
        route = self.route(task)
        self.assertEqual(route["status"], "blocked")
        self.assertEqual(route["phase_states"]["audit"]["status"], "failed")
        call = self.metrics(task)[0]
        self.assertIn("simulated provider process crash", (task / call["evidence"]["stderr"]).read_text(encoding="utf-8"))

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

    def test_needs_review_requires_human_resolution_and_rechecks_phase(self) -> None:
        prepared = self.run_cli(
            "autopilot", "fix local label", "--kind", "small", "--workspace", str(self.workspace),
            "--execute", "--full", mode="review-needs-review",
        )
        self.assertEqual(prepared.returncode, 0, prepared.stderr)
        task = self.latest_task()
        rejected = self.run_cli("resume", task.name, "--execute", "--full")
        self.assertEqual(rejected.returncode, 2)
        resumed = self.run_cli(
            "resume", task.name, "--execute", "--full", "--resolve-review", "Reproduced and addressed the concern",
        )
        self.assertEqual(resumed.returncode, 0, resumed.stderr)
        route = self.route(task)
        self.assertEqual(route["status"], "completed")
        self.assertTrue((task / "review-before-human-resolution.md").is_file())
        self.assertTrue(any(event["event"] == "human-review-resolved" for event in route["events"]))
        self.assertTrue(any(event["event"] == "phase-reopened" for event in route["events"]))

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
