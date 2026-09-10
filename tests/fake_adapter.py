"""Deterministic adapter used only by 0xSDLC end-to-end tests."""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--prompt-file", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--output-artifact", required=True)
    parser.add_argument("--telemetry-file", type=Path, required=True)
    args = parser.parse_args()
    prompt = args.prompt_file.read_text(encoding="utf-8")
    task_id = re.search(r"Task ID: `([^`]+)`", prompt).group(1)
    phase = re.search(r"Phase: `([^`]+)`", prompt).group(1)
    mode = os.environ.get("0XSDLC_FAKE_MODE", "complete")
    if mode == "crash" and phase == "audit":
        print("simulated provider process crash", file=sys.stderr)
        return 17
    output = args.output_dir / args.output_artifact
    if mode == "invalid" and phase == "audit":
        output.write_text("invalid artifact without front matter\n", encoding="utf-8")
        return 0
    status = "verified" if phase == "verify" else "ready"
    if mode == "blocked" and phase == "audit":
        status = "blocked"
    metadata = ["---", 'schema_version: "0.2"', f'task_id: "{task_id}"', f'phase: "{phase}"', f'status: "{status}"']
    if phase == "review":
        first_review = args.output_artifact == "review.md"
        decision = "fix" if mode == "fix-loop" and first_review else "approve"
        metadata.extend([f'decision: "{decision}"', 'blocking_findings: ["F-001"]' if decision == "fix" else "blocking_findings: []"])
    if phase == "synthesis" and "review" in args.prompt_file.name:
        metadata.extend(['decision: "approve"', "blocking_findings: []"])
    if mode == "route-upgrade" and phase == "audit":
        metadata.extend(["route_add: [\"design\", \"approval\"]", 'route_reason: "audit found cross-boundary impact"'])
    metadata.extend(["---", "", f"# Fake {phase} artifact", "", "Deterministic evidence for harness testing."])
    output.write_text("\n".join(metadata) + "\n", encoding="utf-8")
    args.telemetry_file.write_text(json.dumps({"input_tokens": 10, "output_tokens": 5, "cost_usd": 0.001}), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
