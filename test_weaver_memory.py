# FILE: test_weaver_memory.py
# CREATED BY: GitHub Copilot CLI (AI Agent)
# DATE: 09-15-2026
# PROJECT: The-Weaver-Engine
# ===============================================================================

import os
import sys
import time
import json
import asyncio
import unittest
import tempfile
import shutil

from weaver_memory_engine import WeaverMemoryEngine

class TestWeaverMemoryEngine(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp(prefix="weaver_mem_test_")
        self.engine = WeaverMemoryEngine(runtime_root=self.test_dir)

    def tearDown(self):
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_store_and_recall(self):
        """Verify storing and recalling episodic, procedural, and system memories."""
        mid = self.engine.store(
            key="user_preference_01",
            content="User prefers strict fail-closed security for AppleScript execution.",
            scope="user",
            tags="security,applescript,rules",
            metadata={"priority": "high"},
            source_agent="test_agent"
        )
        self.assertTrue(bool(mid))

        mem = self.engine.recall(key="user_preference_01", scope="user")
        self.assertIsNotNone(mem)
        self.assertEqual(mem["key"], "user_preference_01")
        self.assertEqual(mem["scope"], "user")
        self.assertEqual(mem["metadata"]["priority"], "high")
        self.assertIn("fail-closed", mem["content"])

    def test_fts5_search(self):
        """Verify full-text search index querying across multiple memories."""
        self.engine.store(
            key="doc_gateway",
            content="The Universal Gateway Server runs an asynchronous UNIX socket at /tmp/weaver_gateway.sock",
            scope="semantic",
            tags="gateway,network,socket",
            source_agent="doc_agent"
        )
        self.engine.store(
            key="doc_memory",
            content="The Universal Memory Weaver maintains SQLite FTS5 indexes and blackboard JSON state",
            scope="semantic",
            tags="memory,sqlite,fts5",
            source_agent="doc_agent"
        )

        # Search for "socket"
        results_socket = self.engine.search(query="socket")
        self.assertEqual(len(results_socket), 1)
        self.assertEqual(results_socket[0]["key"], "doc_gateway")

        # Search for "sqlite"
        results_sqlite = self.engine.search(query="sqlite")
        self.assertEqual(len(results_sqlite), 1)
        self.assertEqual(results_sqlite[0]["key"], "doc_memory")

    def test_config_matrix_path_resolution(self):
        """Verify zero-touch path mask registration and resolution."""
        path_001 = self.engine.resolve_path("path_001")
        self.assertIsNotNone(path_001)
        self.assertTrue(path_001.endswith("1_universal_modules_weaver"))

        # Set custom mask
        self.engine.set_path_mask("custom_001", "/tmp/custom_target", resource_type="directory", description="Test Mask")
        res = self.engine.resolve_path("custom_001")
        self.assertEqual(res, os.path.abspath("/tmp/custom_target"))

    def test_lineage_audit_logging(self):
        """Verify audit event creation and cryptographic hash integrity."""
        self.engine.store("k1", "Sample content for lineage tracking", scope="episodic")
        lineage = self.engine.get_lineage(limit=5)
        self.assertGreaterEqual(len(lineage), 1)
        self.assertEqual(lineage[0]["action_type"], "store")
        self.assertEqual(lineage[0]["target_resource"], "episodic:k1")
        self.assertTrue(bool(lineage[0]["hash_signature"]))

    def test_delete_and_index_cleanup(self):
        """Verify deletion removes record from both primary table and FTS index."""
        self.engine.store("to_delete", "UniqueStringToPurgeLater", scope="episodic")
        self.assertEqual(len(self.engine.search("UniqueStringToPurgeLater")), 1)

        deleted = self.engine.delete("to_delete", scope="episodic")
        self.assertTrue(deleted)
        self.assertIsNone(self.engine.recall("to_delete", scope="episodic"))
        self.assertEqual(len(self.engine.search("UniqueStringToPurgeLater")), 0)

if __name__ == "__main__":
    unittest.main()
