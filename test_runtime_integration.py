# FILE: test_runtime_integration.py
# CREATED BY: GitHub Copilot CLI (AI Agent)
# DATE: 09-15-2026
# PROJECT: The-Weaver-Engine
# VERSION: 2.0.0-R2026
# ===============================================================================
#
# Description:
#   End-to-end Phase 3 runtime integration test for LTM, coordinator, gateway,
#   module loading, markdown conversion, and secure primitive adaptation.
#
# ===============================================================================

from __future__ import annotations

import json
import shutil
import tempfile
import unittest
from pathlib import Path

from weaver_coordinator import CentralCoordinator
from weaver_gateway_pipeline import UniversalGatewayServer
from weaver_memory_engine import WeaverMemoryEngine


PROJECT_ROOT = Path(__file__).resolve().parent


class RuntimeIntegrationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory(prefix="weaver_runtime_integration_")
        self.runtime_root = Path(self.temp_dir.name) / "runtime"
        modules_root = self.runtime_root / "1_universal_modules_weaver"
        memory_root = self.runtime_root / "2_universal_memory_weaver"
        gateway_root = self.runtime_root / "3_universal_gateway_server"
        for folder in (
            modules_root / "skills",
            modules_root / "hooks",
            modules_root / "mcps",
            memory_root / "vector_nodes",
            gateway_root / "stdio_channels",
        ):
            folder.mkdir(parents=True, exist_ok=True)
        shutil.copy(
            PROJECT_ROOT / "weaver_runtime/1_universal_modules_weaver/skills/data_parser.md",
            modules_root / "skills/data_parser.md",
        )
        shutil.copy(
            PROJECT_ROOT / "weaver_runtime/1_universal_modules_weaver/hooks/crypto_sign.py",
            modules_root / "hooks/crypto_sign.py",
        )
        self.memory = WeaverMemoryEngine(runtime_root=str(self.runtime_root))

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def test_end_to_end_runtime_wiring(self) -> None:
        self.memory.store(
            key="integration_seed",
            content="Phase 3 gateway integration uses SQLite FTS5 runtime memory",
            scope="semantic",
            tags="integration,sqlite,gateway",
            source_agent="integration_test",
        )
        self.assertEqual(
            self.memory.search("SQLite FTS5", scope="semantic")[0]["key"],
            "integration_seed",
        )

        coordinator = CentralCoordinator(
            runtime_root=str(self.runtime_root),
            memory_engine=self.memory,
        )
        results = coordinator.process_complex_workflow(
            massive_task="integration lifecycle verification",
            payload_chunks=["alpha payload", "beta payload"],
            skill_name="data_parser",
        )
        self.assertEqual(len(results), 2)
        with (self.runtime_root / "2_universal_memory_weaver/blackboard.json").open() as handle:
            blackboard = json.load(handle)
        self.assertEqual(blackboard["system_status"], "ONLINE")

        gateway = UniversalGatewayServer(
            runtime_root=str(self.runtime_root),
            memory_engine=self.memory,
        )
        gateway.submit_incoming_network_request(
            json.dumps(
                {
                    "jsonrpc": "2.0",
                    "id": "primitive-1",
                    "method": "crypto_sign",
                    "params": {"data": "phase-3"},
                }
            )
        )
        gateway.submit_incoming_network_request(
            json.dumps(
                {
                    "jsonrpc": "2.0",
                    "id": "search-1",
                    "method": "memory.search",
                    "params": {"query": "gateway integration", "scope": "semantic"},
                }
            )
        )
        responses = gateway.process_gateway_pipeline()
        self.assertEqual(len(responses), 2)
        primitive_response = next(item for item in responses if item["id"] == "primitive-1")
        self.assertEqual(primitive_response["result"]["status"], "SUCCESS")
        search_response = next(item for item in responses if item["id"] == "search-1")
        self.assertEqual(search_response["result"][0]["key"], "integration_seed")

        lifecycle_events = self.memory.search("swarm_start", scope="episodic", limit=10)
        self.assertTrue(lifecycle_events)
        with self.memory._get_connection() as connection:
            lineage = connection.execute(
                """
                SELECT action_type, target_resource
                FROM lineage_events
                WHERE action_type IN ('swarm_start', 'task_dispatch', 'worker_completion', 'execute')
                """
            ).fetchall()
        action_types = {row["action_type"] for row in lineage}
        self.assertTrue(
            {"swarm_start", "task_dispatch", "worker_completion", "execute"} <= action_types
        )


if __name__ == "__main__":
    unittest.main(verbosity=2)
