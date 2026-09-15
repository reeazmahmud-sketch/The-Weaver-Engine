# FILE: weaver_gateway_pipeline.py
# CREATED BY: GitHub Copilot CLI (AI Agent)
# DATE: 09-15-2026
# PROJECT: The-Weaver-Engine
# VERSION: 2.0.0-R2026
# ===============================================================================
#
# Description:
#   Universal Gateway Server with JSON-RPC 2.0 ingest, LTM FTS5 queries, and
#   engine-core module loading, language conversion, and secure adaptation.
#
# ===============================================================================

from __future__ import annotations

import importlib
import json
import os
import queue
import sys
import time

from weaver_memory_engine import WeaverMemoryEngine

_engine_core = importlib.import_module(
    "weaver_runtime.1_universal_modules_weaver.engine_core"
)
ModuleAdapter = _engine_core.ModuleAdapter
ModuleLoader = _engine_core.ModuleLoader
MarkdownLanguageConverter = _engine_core.MarkdownLanguageConverter


class UniversalGatewayServer:
    """Convert JSON-RPC frames into LTM queries or module executions."""

    def __init__(self, runtime_root="./weaver_runtime", memory_engine=None):
        self.runtime_root = runtime_root
        self.modules_dir = os.path.join(runtime_root, "1_universal_modules_weaver")
        self.gateway_dir = os.path.join(runtime_root, "3_universal_gateway_server")
        self.memory_engine = memory_engine or WeaverMemoryEngine(runtime_root=runtime_root)
        self.module_loader = ModuleLoader(self.modules_dir)
        self.language_converter = MarkdownLanguageConverter()
        self.adapter = ModuleAdapter(self.modules_dir)
        self.incoming_queue = queue.Queue()

        print("\n============================================================")
        print("   THE WEAVER ENGINE CORE - UNIVERSAL GATEWAY INITIALIZED   ")
        print("============================================================")
        self.bootstrap_gateway_pipes()

    def bootstrap_gateway_pipes(self):
        """Prepare runtime directories and the default native hook."""
        os.makedirs(os.path.join(self.gateway_dir, "stdio_channels"), exist_ok=True)
        for folder in ("skills", "hooks", "mcps"):
            os.makedirs(os.path.join(self.modules_dir, folder), exist_ok=True)

        mock_hook_path = os.path.join(self.modules_dir, "hooks", "crypto_sign.py")
        if not os.path.exists(mock_hook_path):
            with open(mock_hook_path, "w", encoding="utf-8") as f:
                f.write("import sys\nimport json\nimport hashlib\n")
                f.write("if __name__ == '__main__':\n")
                f.write("    input_data = json.loads(sys.argv[1]) if len(sys.argv) > 1 else {}\n")
                f.write("    raw_string = input_data.get('data', '')\n")
                f.write("    hashed = hashlib.md5(raw_string.encode()).hexdigest()\n")
                f.write("    print(json.dumps({'verification_hash': hashed}))\n")

    @staticmethod
    def _validate_json_rpc_request(packet):
        if not isinstance(packet, dict) or packet.get("jsonrpc", "2.0") != "2.0":
            raise ValueError("request must be a JSON-RPC 2.0 object")
        if not isinstance(packet.get("method"), str) or not packet["method"]:
            raise ValueError("request method must be a non-empty string")
        if "params" in packet and not isinstance(packet["params"], dict):
            raise ValueError("request params must be an object")

    def submit_incoming_network_request(self, external_packet_json):
        """Validate and queue one JSON-RPC request frame."""
        try:
            packet = json.loads(external_packet_json)
            self._validate_json_rpc_request(packet)
            print(
                f"\n[Gateway Server] Network packet received! "
                f"ID: {packet.get('id')} | Method: {packet.get('method')}"
            )
            self.incoming_queue.put(packet)
            return packet
        except (TypeError, ValueError, json.JSONDecodeError) as exc:
            print(f"[Gateway Error] Dropping malformed transaction packet frame: {exc}")
            return None

    def query_ltm(self, query, scope=None, limit=10):
        """Query the LTM SQLite FTS5 index through the gateway."""
        return self.memory_engine.search(query=query, scope=scope, limit=limit)

    def process_gateway_pipeline(self):
        """Process queued JSON-RPC requests and persist response frames."""
        if self.incoming_queue.empty():
            print("[Gateway Server] Zero processing queues active in channel buffer.")
            return []

        responses = []
        while not self.incoming_queue.empty():
            packet = self.incoming_queue.get()
            target_method = packet["method"]
            params = packet.get("params", {})
            print("[Gateway Server] Ingesting method payload into Module Adapter...")

            try:
                if target_method == "memory.search":
                    result = self.query_ltm(
                        query=params["query"],
                        scope=params.get("scope"),
                        limit=params.get("limit", 10),
                    )
                else:
                    result = self.adapter.execute(target_method, params)
                response = {
                    "jsonrpc": "2.0",
                    "id": packet.get("id"),
                    "result": result,
                    "execution_result": result,
                }
                self.memory_engine.record_lineage(
                    agent_id="universal_gateway",
                    action_type="execute",
                    target_resource=target_method,
                    payload_summary=json.dumps(
                        {"id": packet.get("id"), "params": params}, default=str
                    )[:500],
                    status="SUCCESS",
                )
            except Exception as exc:
                response = {
                    "jsonrpc": "2.0",
                    "id": packet.get("id"),
                    "error": {"code": -32000, "message": str(exc)},
                }
                self.memory_engine.record_lineage(
                    agent_id="universal_gateway",
                    action_type="execute",
                    target_resource=target_method,
                    payload_summary=str(exc)[:500],
                    status="FAILURE",
                )

            response_file = os.path.join(
                self.gateway_dir,
                "stdio_channels",
                f"response_{packet.get('id')}.json",
            )
            with open(response_file, "w", encoding="utf-8") as f:
                json.dump(response, f, indent=4)
            print(
                "[Gateway Server] Output response transmission packet committed "
                f"to disk: {os.path.basename(response_file)}"
            )
            responses.append(response)
        return responses


if __name__ == "__main__":
    if not os.path.exists("./weaver_runtime"):
        print("[Error] Initialize the main filesystem footprint by running 'weaver_core.py' first!")
        sys.exit(1)

    gateway = UniversalGatewayServer()
    gateway.submit_incoming_network_request(
        json.dumps(
            {
                "jsonrpc": "2.0",
                "id": "tx_9001",
                "method": "data_parser",
                "params": {"text_stream": "Logistics metrics dump string"},
            }
        )
    )
    gateway.submit_incoming_network_request(
        json.dumps(
            {
                "jsonrpc": "2.0",
                "id": "tx_9002",
                "method": "crypto_sign",
                "params": {"data": "Secure-Weaver-Transaction-Payload-Verification-String"},
            }
        )
    )
    time.sleep(1)
    gateway.process_gateway_pipeline()
