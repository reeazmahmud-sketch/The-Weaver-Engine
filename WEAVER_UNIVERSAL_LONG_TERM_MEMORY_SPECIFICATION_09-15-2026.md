# The Weaver Universal Long-Term Memory (LTM) Engine: Master Specification & Integration Guide
**System Version:** 2.0.0-R2026  
**Document Date:** 09-15-2026  
**Classification:** Universal Polyglot Multi-Agent Memory & Zero-Touch Configuration Subsystem  
**Target Environments:** macOS Native Apps (AppleScript/JXA/Swift), Terminal CLI, WebApps, and Multi-Agent Swarms  

---

## 1. Executive Summary & Architectural Overview

The **Weaver Universal Long-Term Memory (LTM) Engine** is the production implementation of Pillar 2 (`2_universal_memory_weaver`) within **The Binary Weaver Engine Archetype v2**.

Traditional agent systems suffer from memory pollution, context-window bloat, and fragile, hardcoded filesystem bindings. The Weaver LTM Engine solves these failure modes by providing:
1. **Multi-Scope Memory Partitioning:** Structured separation across `system`, `procedural`, `semantic`, `episodic`, and `user` scopes.
2. **Lightning-Fast Full-Text Search (FTS5):** Tokenized SQLite FTS5 index enabling sub-millisecond keyword and associative recall without loading entire memory stores into LLM context windows.
3. **Zero-Touch Database-Driven Path Abstraction (`config_matrix`):** Logical mask resolution (`path_001`, `path_002`, `path_003`, etc.) that completely decouples host-specific file paths from agent prompts and execution runtimes.
4. **Cryptographic Lineage Audit Ledger:** Append-only cryptographic trace of all memory operations, agent tool actions, self-healing events, and host mutations.
5. **Multi-Protocol Client Access:** Unified access via native Python SDK, high-speed Terminal CLI, asynchronous UNIX Domain Sockets (`/tmp/weaver_memory.sock`), and JSON-RPC stream channels.

---

## 2. Directory Layout & Storage Artifacts

The LTM subsystem is located under `weaver_runtime/2_universal_memory_weaver/`:

```text
/Users/reeazmahmud/sandbox/reeaz-terminal-projects/The-Weaver-Engine/
├── weaver_memory_engine.py          # Primary Python SDK, CLI & IPC Socket Server
├── test_weaver_memory.py            # Unit & Integration Test Suite
└── weaver_runtime/
    ├── 1_universal_modules_weaver/  # Pillar 1: Skills, MCPs, Hooks
    ├── 2_universal_memory_weaver/   # Pillar 2: Universal Memory Weaver
    │   ├── memory_store.db          # SQLite WAL Database + FTS5 Search Tables
    │   ├── blackboard.json          # Shared real-time state scratchpad
    │   ├── config_matrix.json       # JSON mirror of zero-touch path abstraction masks
    │   ├── lineage_tree.json        # JSON mirror of cryptographic audit events
    │   └── vector_nodes/            # High-dimensional metrics and telemetry nodes
    └── 3_universal_gateway_server/  # Pillar 3: Gateway pipelines & stdio channels
```

---

## 3. Database Schema & Data Models

The core database `memory_store.db` is configured with SQLite Write-Ahead Logging (`WAL`) mode and immediate foreign key constraints.

### 3.1 `memories` (Primary Memory Store)
| Column | Type | Constraints | Description |
| :--- | :--- | :--- | :--- |
| `id` | `TEXT` | `PRIMARY KEY` | Deterministic SHA-256 hash of `scope:key`. |
| `scope` | `TEXT` | `NOT NULL` | One of `system`, `episodic`, `semantic`, `procedural`, `user`. |
| `key` | `TEXT` | `NOT NULL` | Semantic identifier (unique per scope). |
| `content` | `TEXT` | `NOT NULL` | Raw memory payload, instructions, or observation. |
| `tags` | `TEXT` | `NULLABLE` | Comma-separated keyword tags for filtering. |
| `metadata_json`| `TEXT` | `NULLABLE` | Serialized JSON dictionary of custom attributes. |
| `source_agent` | `TEXT` | `NOT NULL` | Identifier of agent or client that recorded the entry. |
| `importance` | `REAL` | `DEFAULT 1.0` | Weight factor for priority ranking and eviction gating. |
| `created_at` | `REAL` | `NOT NULL` | Epoch timestamp of creation. |
| `updated_at` | `REAL` | `NOT NULL` | Epoch timestamp of latest update. |

### 3.2 `memory_fts` (Virtual Full-Text Search Table)
```sql
CREATE VIRTUAL TABLE memory_fts USING fts5(
    id UNINDEXED,
    scope,
    key,
    content,
    tags,
    tokenize = 'porter unicode61'
);
```
*Note: SQLite triggers automatically synchronize inserts, updates, and deletions between `memories` and `memory_fts` in real time.*

### 3.3 `config_matrix` (Zero-Touch Path Abstraction)
| Column | Type | Constraints | Description |
| :--- | :--- | :--- | :--- |
| `mask` | `TEXT` | `PRIMARY KEY` | Abstract handle (e.g., `path_001`, `path_002`, `path_003`). |
| `canonical_path`| `TEXT` | `NOT NULL` | Absolute verified filesystem path. |
| `resource_type`| `TEXT` | `NOT NULL` | `directory`, `file`, `socket`, or `endpoint`. |
| `permissions` | `TEXT` | `NOT NULL` | Permission mode: `ro`, `rw`, or `rwx`. |
| `environment` | `TEXT` | `NOT NULL` | `local`, `sandbox`, or `production`. |
| `description` | `TEXT` | `NULLABLE` | Human/agent documentation for the path. |
| `version` | `INTEGER` | `DEFAULT 1` | Version sequence incremented on updates. |
| `updated_at` | `REAL` | `NOT NULL` | Epoch timestamp of latest modification. |

### 3.4 `lineage_events` (Cryptographic Audit Ledger)
| Column | Type | Constraints | Description |
| :--- | :--- | :--- | :--- |
| `id` | `TEXT` | `PRIMARY KEY` | Truncated SHA-256 hash of event metadata. |
| `timestamp` | `REAL` | `NOT NULL` | Epoch timestamp of event occurrence. |
| `agent_id` | `TEXT` | `NOT NULL` | Originating agent or process ID. |
| `action_type` | `TEXT` | `NOT NULL` | `store`, `recall`, `mutate`, `heal`, `execute`. |
| `target_resource`| `TEXT` | `NULLABLE` | Targeted entity (e.g. `episodic:db_patch_01`). |
| `payload_summary`| `TEXT` | `NULLABLE` | Truncated summary of payload. |
| `status` | `TEXT` | `NOT NULL` | `SUCCESS`, `FAILURE`, or `BLOCKED`. |
| `hash_signature` | `TEXT` | `NOT NULL` | SHA-256 integrity signature of complete event. |

---

## 4. Multi-Agent & Cross-Platform Integration Interfaces

The LTM Engine can be queried and updated through multiple interfaces:

### 4.1 Python SDK API (Direct Engine Binding)
```python
from weaver_memory_engine import WeaverMemoryEngine

engine = WeaverMemoryEngine()

# 1. Store memory
engine.store(
    key="security_rule_apple_events",
    content="AppleScript execution must only target verified system applications in allowlist.",
    scope="procedural",
    tags="security,applescript,sandbox",
    source_agent="weaver_security_sentinel"
)

# 2. Recall memory
memory = engine.recall(key="security_rule_apple_events", scope="procedural")

# 3. Full-Text Search across memories
results = engine.search(query="AppleScript security")

# 4. Resolve Zero-Touch Path Mask
modules_path = engine.resolve_path("path_001")
```

### 4.2 Terminal CLI Commands
AI agents, human developers, and CI/CD shell scripts can interact with the engine directly from terminal:

```bash
# Store a memory
python3 weaver_memory_engine.py store \
  --key "dark_mode_toggle" \
  --content "tell application \"System Events\" to tell appearance preferences to set dark mode to not dark mode" \
  --scope "procedural" \
  --tags "macos,applescript,ui" \
  --agent "copilot_cli"

# Full-text search
python3 weaver_memory_engine.py search "appearance preferences"

# Recall an exact key
python3 weaver_memory_engine.py recall --key "dark_mode_toggle" --scope "procedural"

# Resolve an abstract path mask
python3 weaver_memory_engine.py resolve path_001

# View configured masks
python3 weaver_memory_engine.py masks

# View cryptographic lineage audit trail
python3 weaver_memory_engine.py lineage --limit 10
```

### 4.3 macOS Native Applications & AppleScript Integration
macOS native applications, automation scripts, and background daemons communicate with the memory engine using standard POSIX stream pipes (`nc` or UNIX domain sockets) at `/tmp/weaver_memory.sock`:

#### Starting the IPC Daemon:
```bash
python3 weaver_memory_engine.py serve --socket /tmp/weaver_memory.sock
```

#### AppleScript Query via Socket:
```applescript
set jsonPayload to "{\"action\": \"search\", \"params\": {\"query\": \"dark mode\"}}"
set cmd to "echo '" & jsonPayload & "' | nc -U /tmp/weaver_memory.sock"
set resultJson to do shell script cmd
```

#### Bash / Shell Pipe:
```bash
echo '{"action": "resolve", "params": {"mask": "path_001"}}' | nc -U /tmp/weaver_memory.sock
```

### 4.4 Web Application & Microservice Integration (JSON-RPC Protocol)
All socket and stream interactions follow a deterministic JSON-RPC contract:

**Request:**
```json
{
  "action": "store",
  "params": {
    "key": "user_session_token",
    "content": "Authenticated session for user reeazmahmud",
    "scope": "episodic",
    "tags": "auth,session",
    "source_agent": "web_gateway",
    "importance": 1.5
  }
}
```

**Response:**
```json
{
  "status": "SUCCESS",
  "id": "e83f99b244d01ac8"
}
```

---

## 5. Memory Scopes & Governance Protocols

| Scope | Ingestion Rules | Retention Policy | Typical Payloads |
| :--- | :--- | :--- | :--- |
| `system` | Read-only to workers; updated only by Orchestrator | Permanent | System rules, architectural blueprints, engine invariant limits. |
| `procedural` | Ingested from verified Skills & Runbooks | Long-Term | Step-by-step AppleScript templates, migration recipes, recovery runbooks. |
| `semantic` | Synthesized knowledge extracted by Weaver AST converters | Long-Term | Code AST summaries, tool schemas, external API documentation. |
| `episodic` | Session events, task completions, run metrics | Windowed / 30 Days | Execution outcomes, temporary session artifacts, error traces. |
| `user` | Explicit user preferences & workflow directives | Permanent | Stated coding style, safety boundaries, authorization grants. |

---

## 6. Verification & Test Evidence

The memory engine was validated with a dedicated automated test suite (`test_weaver_memory.py`):

```text
Ran 5 tests in 0.074s
- test_store_and_recall: PASSED (Verified exact key/scope retrieval and metadata deserialization)
- test_fts5_search: PASSED (Verified Porter-stemmed full-text search indexing across multiple records)
- test_config_matrix_path_resolution: PASSED (Verified zero-touch path mask lookup and updates)
- test_lineage_audit_logging: PASSED (Verified SHA-256 event signature generation and ledger entry)
- test_delete_and_index_cleanup: PASSED (Verified atomic cascade deletion from both store and FTS index)

Result: 100% OK
```

---

## 7. Next Steps & Evolutionary Upgrades (Phase 2 & 3 Roadmap)

1. **High-Dimensional Embeddings Integration:** Add local ONNX vector embeddings for dense semantic similarity ranking alongside BM25/FTS5 text search.
2. **Dynamic Swarm Federation:** Enable memory synchronization across distributed hosts using encrypted peer-to-peer raft gossip protocols.
3. **Automated Memory Distillation & Eviction:** Background self-pruning daemon to compress stale episodic logs while protecting high-importance procedural and user directives.
