"""Regression checks for the dependency-free 0xSDLC route engine."""

from __future__ import annotations

import importlib.util
import json
import os
import socket
import subprocess
import sys
import tempfile
import time
import unittest
from pathlib import Path
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("orchestrator", ROOT / "scripts" / "0xSDLC.py")
assert SPEC and SPEC.loader
ORCHESTRATOR = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(ORCHESTRATOR)
from sdlc_core.runner import start_attempt
from sdlc_core.storage import recover_interrupted
from sdlc_core.telemetry import prepare_call, record, start_call, sync_metrics
INSTALL_SPEC = importlib.util.spec_from_file_location("install", ROOT / "scripts" / "install.py")
assert INSTALL_SPEC and INSTALL_SPEC.loader
INSTALLER = importlib.util.module_from_spec(INSTALL_SPEC)
INSTALL_SPEC.loader.exec_module(INSTALLER)


class RouteTests(unittest.TestCase):
    def test_call_replay_and_interrupted_parallel_recovery(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            task = Path(directory)
            route = ORCHESTRATOR.route_payload(task.name, "fix label", "small", "generic", False, False, directory)
            attempt = start_attempt(task, task, route, "audit")
            completed = prepare_call(task, attempt, "audit", "primary", "generic", "audit.md")
            started = prepare_call(task, attempt, "audit", "secondary", "generic", "audit-secondary.md")
            pending = prepare_call(task, attempt, "audit", "third", "generic", "audit-third.md")
            lanes = route["phase_states"]["audit"]["lanes"]
            for call in (completed, started, pending):
                lanes[call["lane"]] = {"status": "running", "call_id": call["call_id"]}
            for call in (completed, started):
                start_call(task, call, "generic")
            sidecar = task / completed["telemetry_sidecar"]
            sidecar.parent.mkdir(parents=True)
            sidecar.write_text(json.dumps({"call_id": completed["call_id"], "input_tokens": 12, "output_tokens": 8, "cost_usd": 0.01}), encoding="utf-8")
            completed.update(outcome="succeeded", finished_at="2026-11-09T00:00:00+00:00", duration_ms=25, exit_code=0)
            record(task, route, completed)
            record(task, route, {**completed, "duration_ms": 50})
            self.assertTrue(recover_interrupted(route))
            self.assertTrue(sync_metrics(task, route, recover=True))
            self.assertFalse(sync_metrics(task, route, recover=True))
            summary = route["telemetry"]
            self.assertEqual((summary["calls"], summary["duration_ms"], summary["input_tokens"], summary["output_tokens"], summary["cost_usd"]), (2, 25, 12, 8, 0.01))
            metrics = {event["call_id"]: event for event in map(json.loads, (task / "metrics.jsonl").read_text(encoding="utf-8").splitlines())}
            self.assertEqual(metrics[pending["call_id"]]["outcome"], "not-started")
            self.assertEqual(lanes["primary"]["status"], "succeeded")
            self.assertEqual(lanes["third"]["status"], "not-started")
            interrupted = metrics[started["call_id"]]
            self.assertEqual((interrupted["outcome"], interrupted["provenance"]), ("interrupted", "retrospective"))
            self.assertIsNone(interrupted["finished_at"])
            self.assertIsNone(interrupted["duration_ms"])
            self.assertEqual(attempt["outcome"], "interrupted")
            self.assertIsNone(attempt["finished_at"])

    def test_standard_route_skips_design_until_needed(self) -> None:
        self.assertEqual(
            ORCHESTRATOR.route_for("standard", False, False),
            ["specify", "audit", "plan", "implement", "test", "review", "verify"],
        )
        self.assertIn("design", ORCHESTRATOR.route_for("standard", True, False))

    def test_high_risk_route_has_design_and_approval(self) -> None:
        route = ORCHESTRATOR.route_for("high-risk", True, True)
        self.assertLess(route.index("design"), route.index("plan"))
        self.assertLess(route.index("approval"), route.index("implement"))

    def test_read_only_modes_never_route_to_implementation(self) -> None:
        self.assertEqual(ORCHESTRATOR.route_for("standard", False, False, "diagnose"), ["audit", "test", "review", "verify"])
        self.assertEqual(ORCHESTRATOR.route_for("standard", False, False, "assessment"), ["specify", "audit", "plan", "review", "verify"])
        self.assertEqual(ORCHESTRATOR.infer_mode("Why is login broken?"), "diagnose")
        self.assertEqual(ORCHESTRATOR.infer_mode("Assess this harness for gaps"), "assessment")
        route = ORCHESTRATOR.route_payload("2026-10-11_task_1234abcd", "diagnose", "standard", "generic", False, False, ".", mode="diagnose")
        route["phases"].append("implement")
        route["phase_states"]["implement"] = {"status": "pending", "attempts": 0, "lanes": {"primary": {"status": "pending"}}}
        with self.assertRaises(ValueError):
            ORCHESTRATOR.validate_route(route)

    def test_quality_control_is_opt_in_after_review(self) -> None:
        route = ORCHESTRATOR.route_for("standard", False, False, quality_control=True)
        self.assertEqual(route[route.index("review") + 1], "quality-control")

    def test_artifact_requires_task_phase_and_status(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "review.md"
            path.write_text("---\ntask_id: task-1\nphase: review\nstatus: ready\ndecision: approve\n---\n", encoding="utf-8")
            metadata = ORCHESTRATOR.validate_artifact(path, "task-1", "review")
            self.assertEqual(metadata["decision"], "approve")
            path.write_text("---\ntask_id: task-1\nphase: review\nstatus: ready\n---\n", encoding="utf-8")
            with self.assertRaises(ValueError):
                ORCHESTRATOR.validate_artifact(path, "task-1", "review")

    def test_review_decision_uses_stable_finding_ids(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            task_dir = Path(directory) / "task-1"
            task_dir.mkdir()
            (task_dir / "review.md").write_text("---\ntask_id: task-1\nphase: review\nstatus: ready\ndecision: fix\nblocking_findings: [\"F-001\", \"F-002\"]\n---\n", encoding="utf-8")
            route = {"phase_states": {"review": {"last_artifact": "review.md"}}}
            self.assertEqual(ORCHESTRATOR.review_decision(task_dir, route), ("fix", ["F-001", "F-002"]))

    def test_route_migration_is_explicit_and_backward_compatible(self) -> None:
        for source in ("0.2", "0.3"):
            with self.subTest(source=source):
                route = {"schema_version": source, "phases": ["audit"], "events": []}
                migrated, changes = ORCHESTRATOR.migrate_route(route)
                self.assertEqual(migrated["schema_version"], "0.5")
                self.assertTrue(changes)
                self.assertEqual(migrated["events"][-1]["event"], "route-migrated")
                self.assertFalse(migrated["routing"]["maintainability_review"])
                self.assertEqual(migrated["mode"], "change")

    def test_route_0_4_migrates_additive_fields(self) -> None:
        route = {
            "schema_version": "0.4", "phases": ["audit"], "events": [],
            "routing": {"design": False, "approval": False, "maintainability_review": False},
        }
        migrated, _ = ORCHESTRATOR.migrate_route(route)
        self.assertEqual(migrated["schema_version"], "0.5")
        self.assertEqual(migrated["mode"], "change")
        self.assertFalse(migrated["routing"]["quality_control"])

    def test_task_lock_rejects_concurrent_owner(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            task = Path(directory)
            with ORCHESTRATOR.TaskLock(task) as owner:
                past = time.time() - 3600
                os.utime(owner.path, (past, past))
                with self.assertRaisesRegex(RuntimeError, "locked by another run"):
                    with ORCHESTRATOR.TaskLock(task, stale_seconds=0):
                        pass

    def test_task_lock_rejects_live_legacy_owner(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            lock = ORCHESTRATOR.TaskLock(Path(directory), stale_seconds=0)
            lock.path.write_text(json.dumps({"pid": os.getpid(), "host": socket.gethostname()}), encoding="utf-8")
            past = time.time() - 3600
            os.utime(lock.path, (past, past))
            with self.assertRaisesRegex(RuntimeError, "legacy task lock"):
                with lock:
                    pass

    def test_task_lock_recovers_exited_owner(self) -> None:
        owner_script = """
import os
import socket
import sys
from pathlib import Path
sys.path.insert(0, 'scripts')
from sdlc_core.storage import TaskLock, write_json
lock = TaskLock(Path(sys.argv[1]))
if sys.argv[2] == 'guarded':
    lock.__enter__()
else:
    write_json(lock.path, {'pid': os.getpid(), 'host': socket.gethostname()})
os._exit(0)
"""
        for mode, stale_seconds in (("guarded", 3600), ("legacy", 0)):
            with self.subTest(mode=mode), tempfile.TemporaryDirectory() as directory:
                result = subprocess.run([sys.executable, "-c", owner_script, directory, mode], cwd=ROOT, capture_output=True, text=True, timeout=15)
                self.assertEqual(result.returncode, 0, result.stderr)
                lock = ORCHESTRATOR.TaskLock(Path(directory), stale_seconds=stale_seconds)
                self.assertTrue(lock.path.is_file())
                with lock:
                    self.assertEqual(json.loads(lock.path.read_text(encoding="utf-8"))["pid"], os.getpid())
                self.assertFalse(lock.path.exists())

    def test_current_route_is_normalized_when_optional_routing_field_is_missing(self) -> None:
        route = {
            "schema_version": "0.4",
            "routing": {"design": False, "approval": False},
            "events": [],
        }
        normalized, changes = ORCHESTRATOR.migrate_route(route)
        self.assertTrue(changes)
        self.assertFalse(normalized["routing"]["maintainability_review"])
        self.assertFalse(normalized["routing"]["quality_control"])
        self.assertEqual(normalized["events"][-1]["event"], "route-migrated")

    def test_provider_profiles_have_structural_conformance(self) -> None:
        self.assertEqual(ORCHESTRATOR.validate_profiles(), [])

    def test_claude_config_dir_is_honored_by_installer_default(self) -> None:
        with patch.dict(os.environ, {"CLAUDE_CONFIG_DIR": "C:/custom/claude"}):
            self.assertEqual(INSTALLER.default_claude_skills(), Path("C:/custom/claude/skills"))


if __name__ == "__main__":
    unittest.main()
