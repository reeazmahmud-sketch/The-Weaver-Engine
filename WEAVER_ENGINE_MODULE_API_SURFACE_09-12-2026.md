FILE: WEAVER_ENGINE_MODULE_API_SURFACE_09-12-2026.md
CREATED BY: Grok AI Assistant
DATE: 09-12-2026
PROJECT: The-Weaver-Engine
VERSION: 2.0.1-R2026
===============================================================================

Description:
Catalog of classes, functions, and methods for all six top-level Weaver Engine
Python modules (including AutomatedLoggingSuite), with brief params and purpose.
Notes simulation vs production.

===============================================================================

# Weaver Engine — Module API Surface

**System version:** 2.0.0-R2026  
**Doc version:** 2.0.1-R2026  
**Scope:** `weaver_core.py`, `weaver_coordinator.py`, `weaver_gateway_pipeline.py`, `weaver_integration_runner.py`, `weaver_system_extension.py`, `weaver_logging_suite.py`
**Documentation tier:** **As-built implementation/reference**

---

## Simulation vs production (read this first)

| Layer | Current behavior | Production intent |
|-------|------------------|-------------------|
| Ephemeral workers | `time.sleep(1.2)` then canned `SUCCESS` dict; no LLM call | Pass `self.context` to an LLM/client for real subtask work |
| Gateway ingest | In-memory `queue.Queue` + mock JSON strings in `__main__` | Real sockets / HTTP / WebSocket via a network proxy |
| Skill execution | Returns a formatted string acknowledging the payload | Interpret playbook and drive agent steps |
| Language converter | **Mock AST**: string splits / keyword checks, not real `ast` parsing of foreign languages | Real lexer/AST or micro-compile for JS/Bash/Go/etc. |
| Polyglot hooks | Emit a tiny Python stub that prints fixed JSON meta | Execute or bridge to the original foreign runtime |
| Guardian / loom | Poll walk every 0.5s + in-memory content restore | Kernel FS watchers, stronger integrity policy |
| Integration runner | Orchestrated demo challenge with forged `security_scanner` | Continuous service composition |

All six modules are **demo-grade runnable scaffolds** aligned to the master blueprint, not full production services. The logging suite is implemented middleware (stdlib file I/O), not a containerized ops stack.

---

## 1. `weaver_core.py`

### `class TheWeaverEngine`

| Member | Signature / params | Purpose |
|--------|--------------------|---------|
| `__init__` | `(self, root_dir="./weaver_runtime")` | Sets pillar paths, bootstraps dirs, spins loom-state, starts daemon guardian thread. |
| `bootstrap_environment` | `(self)` | Creates modules/skills/mcps/hooks, memory/vector_nodes, gateway/stdio_channels; seeds `data_parser.md` and `blackboard.json` if missing. |
| `calculate_hash` | `(self, file_path)` | SHA-256 hex digest of file bytes; `None` if missing. |
| `spin_loom_state` | `(self)` | Walks `root_dir`, caches relative path → `{hash, content, is_binary}` in `self.loom_state`. |
| `monitor_warp_threads` | `(self)` | Loop while `is_running`: detect hash drift (REPAIR) or missing files (REGENERATE). |
| `trigger_weave_loop` | `(self, relative_path, action)` | Restores file from loom cache (`action` is informational: `"REPAIR"` / `"REGENERATE"`). |
| `run_chaos_test_simulation` | `(self)` | Corrupts skill + deletes blackboard, waits for heal, then sets `is_running = False`. |

**`__main__`:** constructs engine, runs chaos simulation, then process ends (daemon thread stops with process).

---

## 2. `weaver_coordinator.py`

### `class EphemeralWorker`

| Member | Signature / params | Purpose |
|--------|--------------------|---------|
| `__init__` | `(self, id, assigned_skill_path)` | Stores worker id and skill path; loads skill text. |
| `load_skill` | `(self)` | Reads skill file into `self.context`, or default string if missing. |
| `execute_subtask` | `(self, subtask_payload)` | **Simulated** work: sleep 1.2s; return SUCCESS dict with worker_id, processed_payload, timestamp. |

### `class CentralCoordinator`

| Member | Signature / params | Purpose |
|--------|--------------------|---------|
| `__init__` | `(self, runtime_root="./weaver_runtime")` | Resolves modules/memory paths, blackboard + lineage paths. |
| `write_to_blackboard` | `(self, key, value)` | Read-modify-write JSON update of a single key on the blackboard. |
| `log_lineage_evolution` | `(self, task_id, structure_delta)` | Appends mutation record to `lineage_tree.json` (creates file if needed). |
| `process_complex_workflow` | `(self, massive_task, payload_chunks, skill_name)` | Ensures skill `.md` (forges if missing), sets blackboard PROCESSING, ThreadPoolExecutor over chunks, stores `last_swarm_output`, resets status ONLINE. |

**`__main__`:** requires `./weaver_runtime`; runs logistics four-chunk demo with `skill_name="data_parser"`.

---

## 3. `weaver_gateway_pipeline.py`

### `class UniversalModuleAdapter`

| Member | Signature / params | Purpose |
|--------|--------------------|---------|
| `__init__` | `(self, modules_dir)` | Stores modules root for skills/hooks resolution. |
| `execute_primitive` | `(self, primitive_name, payload)` | If `hooks/{name}.py` exists → subprocess with JSON argv; elif `skills/{name}.md` → semantic SUCCESS string; else `NOT_FOUND`. |

### `class UniversalGatewayServer`

| Member | Signature / params | Purpose |
|--------|--------------------|---------|
| `__init__` | `(self, runtime_root="./weaver_runtime")` | Builds adapter, inbound queue; calls `bootstrap_gateway_pipes`. |
| `bootstrap_gateway_pipes` | `(self)` | Ensures `hooks/crypto_sign.py` mock plugin exists. |
| `submit_incoming_network_request` | `(self, external_packet_json)` | Parses JSON-RPC-like packet (`id`, `method`, `params`); enqueues or drops malformed. |
| `process_gateway_pipeline` | `(self)` | Drains queue; `execute_primitive(method, params)`; writes `stdio_channels/response_{id}.json`. |

**`__main__`:** submits `tx_9001` (`data_parser`) and `tx_9002` (`crypto_sign`), then processes pipeline.

---

## 4. `weaver_integration_runner.py`

Module-level functions (no classes):

| Function | Signature / params | Purpose |
|----------|--------------------|---------|
| `run_guardian_process` | `(stop_event)` | Child process: constructs `TheWeaverEngine`, loops until `stop_event` is set. |
| `run_live_challenge` | `()` | Starts guardian process; gateway + coordinator; injects `security_scanner` challenge; swarm + crypto_sign pipeline; prints blackboard; stops guardian. |

**`__main__`:** `multiprocessing.freeze_support()` then `run_live_challenge()`.

**Imports:** `TheWeaverEngine`, `CentralCoordinator`, `UniversalGatewayServer`.

---

## 5. `weaver_system_extension.py`

### `class UniversalLanguageConverter`

| Member | Signature / params | Purpose |
|--------|--------------------|---------|
| `__init__` | `(self, modules_dir)` | Target directory for emitted hooks. |
| `cross_compile_to_schema` | `(self, filename, code_content, language="javascript")` | **Mock** language parse → tool schema; writes `hooks/polyglot_wrapper_{func}.py`; returns schema dict (`name`, `language`, `signature`, `parameters`). |

Supported mock branches: `javascript` (function name + fixed params), `bash` (filename stem + `args` array), else `generic_primitive`.

### `class WeaverConsoleTerminal`

| Member | Signature / params | Purpose |
|--------|--------------------|---------|
| `__init__` | `(self, runtime_root="./weaver_runtime")` | Paths + nested `UniversalLanguageConverter`. |
| `query_blackboard` | `(self)` | Loads `blackboard.json` or `{"error": "Blackboard offline"}`. |
| `launch_interactive_shell` | `(self)` | REPL: `status`, `convert` (hardcoded JS `cleanLogs` demo), `exit`; handles `KeyboardInterrupt`. |

**`__main__`:** requires `./weaver_runtime`; launches interactive shell.

---

## 6. `weaver_logging_suite.py`

### `class AutomatedLoggingSuite`

| Member | Signature / params | Purpose |
|--------|--------------------|---------|
| `__init__` | `(self, runtime_root="./weaver_runtime")` | Resolves blackboard + `vector_nodes/` metrics/dashboard paths; `max_history_points = 20`. |
| `harvest_live_telemetry` | `(self)` | Reads blackboard → snapshot `{timestamp, swarm_load, status_code, raw_status}` (zeros/`UNKNOWN` on miss/error). |
| `commit_metrics_snapshot` | `(self, snapshot)` | Appends to `performance_metrics.json`; sliding-window trim; returns history list. |
| `render_ascii_line_chart` | `(self, history_data)` | Builds ASCII swarm-load grid; writes `uptime_dashboard.txt`; returns dashboard string. |
| `run_telemetry_cycle` | `(self)` | harvest → commit → render one pass; returns dashboard text. |

**`__main__`:** requires `./weaver_runtime`; runs **5** cycles with 1s sleep; handles `KeyboardInterrupt`.

**Status codes:** `PROCESSING_SWARM`→3, `ONLINE`→2, other non-empty→1, missing blackboard→0.

Detail + example ASCII: [`WEAVER_ENGINE_AUTOMATED_LOGGING_SUITE_09-12-2026.md`](WEAVER_ENGINE_AUTOMATED_LOGGING_SUITE_09-12-2026.md).

---

## Cross-module dependency sketch

```text
weaver_integration_runner
  ├── weaver_core.TheWeaverEngine
  ├── weaver_coordinator.CentralCoordinator
  └── weaver_gateway_pipeline.UniversalGatewayServer
          └── UniversalModuleAdapter  →  skills/*.md | hooks/*.py

weaver_system_extension
  └── UniversalLanguageConverter  →  writes hooks/polyglot_wrapper_*.py
  └── WeaverConsoleTerminal       →  reads blackboard.json

weaver_logging_suite
  └── AutomatedLoggingSuite       →  reads blackboard.json
                                  →  writes vector_nodes/performance_metrics.json
                                  →  writes vector_nodes/uptime_dashboard.txt
```
