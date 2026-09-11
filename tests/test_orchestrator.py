"""Regression checks for the dependency-free 0xSDLC route engine."""

from __future__ import annotations

import importlib.util
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("orchestrator", ROOT / "scripts" / "0xSDLC.py")
assert SPEC and SPEC.loader
ORCHESTRATOR = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(ORCHESTRATOR)


class RouteTests(unittest.TestCase):
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
        route = {
            "schema_version": "0.3", "phases": ["audit"], "events": [],
        }
        migrated, changes = ORCHESTRATOR.migrate_route(route)
        self.assertEqual(migrated["schema_version"], "0.4")
        self.assertTrue(changes)
        self.assertEqual(migrated["events"][-1]["event"], "route-migrated")
        self.assertFalse(migrated["routing"]["maintainability_review"])

    def test_task_lock_rejects_concurrent_owner(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            task = Path(directory)
            with ORCHESTRATOR.TaskLock(task):
                with self.assertRaises(RuntimeError):
                    with ORCHESTRATOR.TaskLock(task):
                        pass

    def test_current_route_is_normalized_when_optional_routing_field_is_missing(self) -> None:
        route = {
            "schema_version": "0.4",
            "routing": {"design": False, "approval": False},
            "events": [],
        }
        normalized, changes = ORCHESTRATOR.migrate_route(route)
        self.assertTrue(changes)
        self.assertFalse(normalized["routing"]["maintainability_review"])
        self.assertEqual(normalized["events"][-1]["event"], "route-normalized")

    def test_provider_profiles_have_structural_conformance(self) -> None:
        self.assertEqual(ORCHESTRATOR.validate_profiles(), [])


if __name__ == "__main__":
    unittest.main()
