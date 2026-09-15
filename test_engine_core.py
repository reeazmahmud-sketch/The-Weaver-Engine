"""Unit tests for the Phase 2 Weaver Engine core."""

from __future__ import annotations

import json
import importlib
import tempfile
import textwrap
import unittest
from pathlib import Path

_engine_core = importlib.import_module(
    "weaver_runtime.1_universal_modules_weaver.engine_core"
)
MarkdownLanguageConverter = _engine_core.MarkdownLanguageConverter
ModuleAdapter = _engine_core.ModuleAdapter
ModuleLoader = _engine_core.ModuleLoader
ModuleSecurityError = importlib.import_module(
    "weaver_runtime.1_universal_modules_weaver.engine_core.module_adapter"
).ModuleSecurityError


class EngineCoreTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.root = Path(self.temp_dir.name) / "modules"
        for folder in ("skills", "hooks", "mcps"):
            (self.root / folder).mkdir(parents=True)
        (self.root / "skills" / "demo.md").write_text(
            "# Demo Skill\n- Parse input text.\n- `text` (string): text to parse\n",
            encoding="utf-8",
        )
        (self.root / "hooks" / "echo.py").write_text(
            textwrap.dedent(
                """
                import json
                import sys
                if __name__ == "__main__":
                    print(json.dumps({"echo": json.loads(sys.argv[1])["value"]}))
                """
            ),
            encoding="utf-8",
        )
        (self.root / "mcps" / "sample.json").write_text(
            json.dumps({"schema_version": "1", "description": "sample", "tools": ["demo"]}),
            encoding="utf-8",
        )

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def test_loader_builds_registry_for_all_module_types(self) -> None:
        registry = ModuleLoader(self.root).scan()
        self.assertEqual({"demo", "echo", "sample"}, set(registry))
        self.assertEqual("skill", registry["demo"]["module_type"])
        self.assertIn("functions", registry["echo"]["signature"])
        self.assertEqual(["demo"], registry["sample"]["signature"]["tools"])

    def test_converter_emits_json_rpc_declaration_and_schema(self) -> None:
        declaration = MarkdownLanguageConverter().convert_file(self.root / "skills" / "demo.md")
        self.assertEqual("demo", declaration["name"])
        self.assertEqual("object", declaration["inputSchema"]["type"])
        self.assertEqual("string", declaration["inputSchema"]["properties"]["text"]["type"])

    def test_adapter_executes_hook_and_declares_skill(self) -> None:
        adapter = ModuleAdapter(self.root)
        hook_result = adapter.execute("echo", {"value": "ok"})
        skill_result = adapter.execute("demo", {"text": "ok"})
        self.assertEqual("SUCCESS", hook_result["status"])
        self.assertEqual({"echo": "ok"}, hook_result["output"])
        self.assertEqual("DECLARED", skill_result["status"])

    def test_adapter_rejects_forbidden_tokens_and_absolute_paths(self) -> None:
        adapter = ModuleAdapter(self.root)
        with self.assertRaises(ModuleSecurityError):
            adapter.execute("echo", {"value": "safe && rm -rf x"})
        with self.assertRaises(ModuleSecurityError):
            adapter.execute("echo", {"value": str(Path("/", "tmp", "not-portable"))})


if __name__ == "__main__":
    unittest.main(verbosity=2)
