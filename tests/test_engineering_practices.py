"""Language detection and selective engineering-practice loading tests."""

from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from sdlc_core.project import project_profile
from sdlc_core.prompts import selected_practice_paths


class EngineeringPracticeTests(unittest.TestCase):
    def test_cpp_profile_uses_source_and_tooling_evidence(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            workspace = Path(directory)
            (workspace / "CMakeLists.txt").write_text("cmake_minimum_required(VERSION 3.25)\n", encoding="utf-8")
            (workspace / ".clang-format").write_text("BasedOnStyle: LLVM\n", encoding="utf-8")
            (workspace / "main.cpp").write_text("int main() { return 0; }\n", encoding="utf-8")
            profile = project_profile(workspace)
            self.assertEqual(profile["languages"]["C++"], 1)
            self.assertIn(".clang-format", profile["style_files"])
            self.assertIn("C++/CMake", profile["ecosystems"])

    def test_language_supplements_are_selected_only_for_relevant_phases(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            task = Path(directory)
            (task / "project-profile.json").write_text(json.dumps({"languages": {"C++": 3}}), encoding="utf-8")
            design = selected_practice_paths(task, "design", "primary")
            audit = selected_practice_paths(task, "audit", "primary")
            self.assertIn("support/engineering-practices/languages/cpp.md", design)
            self.assertNotIn("support/engineering-practices/languages/cpp.md", audit)
            self.assertIn("support/engineering-practices/architecture.md", design)

    def test_c_headers_do_not_trigger_cpp_without_cpp_evidence(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            workspace = Path(directory)
            (workspace / "main.c").write_text("int main(void) { return 0; }\n", encoding="utf-8")
            (workspace / "api.h").write_text("int answer(void);\n", encoding="utf-8")
            profile = project_profile(workspace)
            self.assertEqual(profile["languages"], {"C": 2})


if __name__ == "__main__":
    unittest.main()
