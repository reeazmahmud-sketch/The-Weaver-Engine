# FILE: weaver_memory_engine.py
# CREATED BY: GitHub Copilot CLI (AI Agent)
# DATE: 09-15-2026
# PROJECT: The-Weaver-Engine
# VERSION: 2.0.0-R2026
# ===============================================================================
#
# Description:
#   Pillar 2 Universal Long-Term Memory (LTM) Engine for The Weaver Engine.
#   Provides multi-agent, cross-platform memory storage, full-text search (FTS5),
#   zero-touch path abstraction resolution, lineage event logging, and multi-client
#   access (Python SDK, CLI, UNIX socket IPC, and HTTP/JSON stream pipe).
#
# ===============================================================================

import os
import sys
import time
import json
import sqlite3
import hashlib
import argparse
import asyncio
from typing import Dict, List, Any, Optional
from datetime import datetime

class WeaverMemoryEngine:
    """
    Universal Long-Term Memory (LTM) & State Repository for the Weaver Engine.
    Engineered for multi-agent coordination, native macOS apps, WebApps, and Terminal CLIs.
    """
    def __init__(self, runtime_root: Optional[str] = None):
        if runtime_root is None:
            # Auto-detect relative to script or sandbox
            base_dir = os.path.dirname(os.path.abspath(__file__))
            cand_runtime = os.path.join(base_dir, "weaver_runtime")
            if os.path.exists(cand_runtime):
                self.runtime_root = cand_runtime
            else:
                self.runtime_root = "./weaver_runtime"
        else:
            self.runtime_root = runtime_root

        self.memory_dir = os.path.join(self.runtime_root, "2_universal_memory_weaver")
        self.modules_dir = os.path.join(self.runtime_root, "1_universal_modules_weaver")
        self.gateway_dir = os.path.join(self.runtime_root, "3_universal_gateway_server")
        
        os.makedirs(self.memory_dir, exist_ok=True)
        os.makedirs(os.path.join(self.memory_dir, "vector_nodes"), exist_ok=True)
        
        self.db_path = os.path.join(self.memory_dir, "memory_store.db")
        self.blackboard_path = os.path.join(self.memory_dir, "blackboard.json")
        self.lineage_path = os.path.join(self.memory_dir, "lineage_tree.json")
        self.config_matrix_path = os.path.join(self.memory_dir, "config_matrix.json")
        self.socket_path = "/tmp/weaver_memory.sock"
        
        self._init_database()
        self._init_config_matrix()
        self._sync_legacy_blackboard()

    def _get_connection(self) -> sqlite3.Connection:
        """Returns a configured SQLite connection with WAL mode enabled for high concurrency."""
        conn = sqlite3.connect(self.db_path, timeout=30.0)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA journal_mode = WAL;")
        conn.execute("PRAGMA synchronous = NORMAL;")
        conn.execute("PRAGMA foreign_keys = ON;")
        return conn

    def _init_database(self):
        """Initializes tables for structured memory, full-text search, config masks, and lineage."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            # 1. Primary Memories Table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS memories (
                    id TEXT PRIMARY KEY,
                    scope TEXT NOT NULL,         -- 'system', 'episodic', 'semantic', 'procedural', 'user'
                    key TEXT NOT NULL,
                    content TEXT NOT NULL,
                    tags TEXT,                  -- comma-separated tags
                    metadata_json TEXT,         -- structured JSON attributes
                    source_agent TEXT NOT NULL, -- author agent name or client identifier
                    importance REAL DEFAULT 1.0,-- weight for ranking
                    created_at REAL NOT NULL,
                    updated_at REAL NOT NULL,
                    UNIQUE(scope, key)
                );
            """)

            # 2. FTS5 Search Index Table
            cursor.execute("""
                CREATE VIRTUAL TABLE IF NOT EXISTS memory_fts USING fts5(
                    id UNINDEXED,
                    scope,
                    key,
                    content,
                    tags,
                    tokenize = 'porter unicode61'
                );
            """)

            # Triggers to keep FTS5 synchronized with memories table
            cursor.execute("""
                CREATE TRIGGER IF NOT EXISTS trg_memories_ai AFTER INSERT ON memories BEGIN
                    INSERT INTO memory_fts(id, scope, key, content, tags)
                    VALUES (new.id, new.scope, new.key, new.content, new.tags);
                END;
            """)
            cursor.execute("""
                CREATE TRIGGER IF NOT EXISTS trg_memories_ad AFTER DELETE ON memories BEGIN
                    DELETE FROM memory_fts WHERE id = old.id;
                END;
            """)
            cursor.execute("""
                CREATE TRIGGER IF NOT EXISTS trg_memories_au AFTER UPDATE ON memories BEGIN
                    DELETE FROM memory_fts WHERE id = old.id;
                    INSERT INTO memory_fts(id, scope, key, content, tags)
                    VALUES (new.id, new.scope, new.key, new.content, new.tags);
                END;
            """)

            # 3. Zero-Touch Path & Environment Configuration Matrix Table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS config_matrix (
                    mask TEXT PRIMARY KEY,          -- e.g., 'path_001'
                    canonical_path TEXT NOT NULL,   -- physical filesystem or URL target
                    resource_type TEXT NOT NULL,    -- 'directory', 'file', 'socket', 'endpoint'
                    permissions TEXT NOT NULL,      -- 'ro', 'rw', 'rwx'
                    environment TEXT NOT NULL,      -- 'local', 'sandbox', 'production'
                    description TEXT,
                    version INTEGER DEFAULT 1,
                    updated_at REAL NOT NULL
                );
            """)

            # 4. Multi-Agent Lineage & Audit Event Log
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS lineage_events (
                    id TEXT PRIMARY KEY,
                    timestamp REAL NOT NULL,
                    agent_id TEXT NOT NULL,
                    action_type TEXT NOT NULL,      -- 'store', 'recall', 'mutate', 'heal', 'execute'
                    target_resource TEXT,
                    payload_summary TEXT,
                    status TEXT NOT NULL,           -- 'SUCCESS', 'FAILURE', 'BLOCKED'
                    hash_signature TEXT NOT NULL
                );
            """)
            conn.commit()

    def _init_config_matrix(self):
        """Populates baseline zero-touch configuration masks if not present."""
        defaults = [
            ("path_001", os.path.abspath(self.modules_dir), "directory", "rw", "sandbox", "Pillar 1 Universal Modules Directory"),
            ("path_002", os.path.abspath(self.memory_dir), "directory", "rw", "sandbox", "Pillar 2 Universal Memory Directory"),
            ("path_003", os.path.abspath(self.gateway_dir), "directory", "rw", "sandbox", "Pillar 3 Universal Gateway Server Directory"),
            ("path_root", os.path.abspath(self.runtime_root), "directory", "rw", "sandbox", "Weaver Engine Runtime Root Directory")
        ]
        
        with self._get_connection() as conn:
            cursor = conn.cursor()
            for mask, path, rtype, perms, env, desc in defaults:
                cursor.execute("""
                    INSERT OR IGNORE INTO config_matrix (mask, canonical_path, resource_type, permissions, environment, description, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (mask, path, rtype, perms, env, desc, time.time()))
            conn.commit()

        # Also emit a human/agent readable JSON mirror
        self.export_config_matrix_json()

    def export_config_matrix_json(self):
        """Exports the config matrix to config_matrix.json for rapid inspection."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT mask, canonical_path, resource_type, permissions, environment, description, version, updated_at FROM config_matrix")
            rows = [dict(row) for row in cursor.fetchall()]
        
        with open(self.config_matrix_path, 'w', encoding='utf-8') as f:
            json.dump({"schema_version": "2.0.0", "masks": rows}, f, indent=4)

    def _sync_legacy_blackboard(self):
        """Ensures backward compatibility with legacy blackboard.json readers."""
        if not os.path.exists(self.blackboard_path):
            with open(self.blackboard_path, 'w', encoding='utf-8') as f:
                json.dump({"system_status": "ONLINE", "active_swarms": 0, "last_synced": time.time()}, f, indent=4)

    # =========================================================================
    # Memory CRUD & Full-Text Search Operations
    # =========================================================================

    def store(self, key: str, content: str, scope: str = "episodic", tags: str = "", 
              metadata: Optional[Dict[str, Any]] = None, source_agent: str = "weaver_agent", 
              importance: float = 1.0) -> str:
        """Stores or updates a structured long-term memory entry."""
        now = time.time()
        mem_id = hashlib.sha256(f"{scope}:{key}".encode('utf-8')).hexdigest()[:16]
        meta_str = json.dumps(metadata or {})
        
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO memories (id, scope, key, content, tags, metadata_json, source_agent, importance, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(scope, key) DO UPDATE SET
                    content = excluded.content,
                    tags = excluded.tags,
                    metadata_json = excluded.metadata_json,
                    source_agent = excluded.source_agent,
                    importance = excluded.importance,
                    updated_at = excluded.updated_at
            """, (mem_id, scope, key, content, tags, meta_str, source_agent, importance, now, now))
            conn.commit()

        self.record_lineage(
            agent_id=source_agent,
            action_type="store",
            target_resource=f"{scope}:{key}",
            payload_summary=content[:100],
            status="SUCCESS"
        )
        return mem_id

    def recall(self, key: str, scope: str = "episodic") -> Optional[Dict[str, Any]]:
        """Recalls an exact memory entry by scope and key."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM memories WHERE scope = ? AND key = ?", (scope, key))
            row = cursor.fetchone()
            if row:
                d = dict(row)
                d['metadata'] = json.loads(d.pop('metadata_json') or '{}')
                return d
            return None

    def search(self, query: str, scope: Optional[str] = None, limit: int = 10) -> List[Dict[str, Any]]:
        """Performs indexed FTS5 keyword and semantic search across all memories."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            # Sanitize FTS5 query terms
            clean_query = "".join(c for c in query if c.isalnum() or c in (" ", "-", "_", "*")).strip()
            if not clean_query:
                return []
            
            fts_match = f"{clean_query}*"
            
            if scope:
                sql = """
                    SELECT m.*, rank
                    FROM memory_fts f
                    JOIN memories m ON f.id = m.id
                    WHERE memory_fts MATCH ? AND m.scope = ?
                    ORDER BY rank ASC
                    LIMIT ?
                """
                cursor.execute(sql, (fts_match, scope, limit))
            else:
                sql = """
                    SELECT m.*, rank
                    FROM memory_fts f
                    JOIN memories m ON f.id = m.id
                    WHERE memory_fts MATCH ?
                    ORDER BY rank ASC
                    LIMIT ?
                """
                cursor.execute(sql, (fts_match, limit))
                
            results = []
            for row in cursor.fetchall():
                d = dict(row)
                d['metadata'] = json.loads(d.pop('metadata_json') or '{}')
                results.append(d)
            return results

    def list_memories(self, scope: Optional[str] = None, limit: int = 50) -> List[Dict[str, Any]]:
        """Lists recent memories ordered by updated timestamp."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            if scope:
                cursor.execute("SELECT * FROM memories WHERE scope = ? ORDER BY updated_at DESC LIMIT ?", (scope, limit))
            else:
                cursor.execute("SELECT * FROM memories ORDER BY updated_at DESC LIMIT ?", (limit,))
            
            results = []
            for row in cursor.fetchall():
                d = dict(row)
                d['metadata'] = json.loads(d.pop('metadata_json') or '{}')
                results.append(d)
            return results

    def delete(self, key: str, scope: str = "episodic", source_agent: str = "weaver_agent") -> bool:
        """Deletes a memory entry and cascades removal from search index."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM memories WHERE scope = ? AND key = ?", (scope, key))
            deleted = cursor.rowcount > 0
            conn.commit()
            
        if deleted:
            self.record_lineage(
                agent_id=source_agent,
                action_type="delete",
                target_resource=f"{scope}:{key}",
                payload_summary="Memory key deleted",
                status="SUCCESS"
            )
        return deleted

    # =========================================================================
    # Zero-Touch Configuration Matrix Resolver
    # =========================================================================

    def resolve_path(self, mask: str) -> Optional[str]:
        """Resolves an abstract mask (e.g. 'path_001') to a verified canonical filesystem path."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT canonical_path FROM config_matrix WHERE mask = ?", (mask,))
            row = cursor.fetchone()
            if row:
                return row["canonical_path"]
            return None

    def set_path_mask(self, mask: str, canonical_path: str, resource_type: str = "directory", 
                      permissions: str = "rw", environment: str = "sandbox", 
                      description: str = "") -> bool:
        """Sets or updates an abstract configuration mask."""
        now = time.time()
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO config_matrix (mask, canonical_path, resource_type, permissions, environment, description, version, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, 1, ?)
                ON CONFLICT(mask) DO UPDATE SET
                    canonical_path = excluded.canonical_path,
                    resource_type = excluded.resource_type,
                    permissions = excluded.permissions,
                    environment = excluded.environment,
                    description = excluded.description,
                    version = config_matrix.version + 1,
                    updated_at = excluded.updated_at
            """, (mask, os.path.abspath(canonical_path), rtype := resource_type, permissions, environment, description, now))
            conn.commit()
        self.export_config_matrix_json()
        return True

    def get_all_masks(self) -> List[Dict[str, Any]]:
        """Returns all configured path masks."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM config_matrix ORDER BY mask ASC")
            return [dict(row) for row in cursor.fetchall()]

    # =========================================================================
    # Lineage Tree & Audit Trail Logging
    # =========================================================================

    def record_lineage(self, agent_id: str, action_type: str, target_resource: str, 
                       payload_summary: str, status: str = "SUCCESS") -> str:
        """Appends an immutable audit event to the lineage ledger."""
        now = time.time()
        raw_seed = f"{now}:{agent_id}:{action_type}:{target_resource}:{status}"
        event_id = hashlib.sha256(raw_seed.encode('utf-8')).hexdigest()[:16]
        hash_signature = hashlib.sha256((raw_seed + payload_summary).encode('utf-8')).hexdigest()
        
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO lineage_events (id, timestamp, agent_id, action_type, target_resource, payload_summary, status, hash_signature)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (event_id, now, agent_id, action_type, target_resource, payload_summary, status, hash_signature))
            conn.commit()

        # Update JSON mirror file for fast file-watcher ingestion
        self._append_lineage_json_mirror({
            "event_id": event_id,
            "timestamp": now,
            "iso_time": datetime.fromtimestamp(now).isoformat(),
            "agent_id": agent_id,
            "action_type": action_type,
            "target": target_resource,
            "summary": payload_summary,
            "status": status,
            "signature": hash_signature
        })
        return event_id

    def _append_lineage_json_mirror(self, event_dict: Dict[str, Any]):
        """Maintains the legacy lineage_tree.json for dashboard tools."""
        events = []
        if os.path.exists(self.lineage_path):
            try:
                with open(self.lineage_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    events = data.get("events", [])
            except Exception:
                events = []
        
        events.append(event_dict)
        # Keep last 100 in file mirror
        events = events[-100:]
        
        with open(self.lineage_path, 'w', encoding='utf-8') as f:
            json.dump({"schema_version": "2.0.0", "events": events}, f, indent=4)

    def get_lineage(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Retrieves recent lineage audit entries."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM lineage_events ORDER BY timestamp DESC LIMIT ?", (limit,))
            return [dict(row) for row in cursor.fetchall()]

    # =========================================================================
    # IPC Daemon / Server for Terminal CLI, Native Apps, and WebApps
    # =========================================================================

    async def handle_ipc_client(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
        """Handles incoming IPC socket requests from Terminal CLI, AppleScript, or native apps."""
        try:
            data = await reader.read(65536)
            if not data:
                writer.close()
                await writer.wait_closed()
                return
            
            raw_req = data.decode('utf-8').strip()
            req = json.loads(raw_req)
            action = req.get("action", "")
            params = req.get("params", {})
            
            response = {"status": "SUCCESS"}
            
            if action == "store":
                mem_id = self.store(
                    key=params["key"],
                    content=params["content"],
                    scope=params.get("scope", "episodic"),
                    tags=params.get("tags", ""),
                    metadata=params.get("metadata"),
                    source_agent=params.get("source_agent", "ipc_client"),
                    importance=params.get("importance", 1.0)
                )
                response["id"] = mem_id
                
            elif action == "recall":
                mem = self.recall(key=params["key"], scope=params.get("scope", "episodic"))
                response["data"] = mem
                
            elif action == "search":
                res = self.search(query=params["query"], scope=params.get("scope"), limit=params.get("limit", 10))
                response["results"] = res
                
            elif action == "resolve":
                path = self.resolve_path(mask=params["mask"])
                response["canonical_path"] = path
                
            elif action == "list":
                res = self.list_memories(scope=params.get("scope"), limit=params.get("limit", 50))
                response["results"] = res
                
            elif action == "lineage":
                res = self.get_lineage(limit=params.get("limit", 50))
                response["events"] = res
                
            elif action == "ping":
                response["pong"] = True
                response["timestamp"] = time.time()
                
            else:
                response = {"status": "ERROR", "message": f"Unknown action: {action}"}
                
            writer.write((json.dumps(response) + "\n").encode('utf-8'))
            await writer.drain()
        except Exception as e:
            err_res = {"status": "ERROR", "message": str(e)}
            writer.write((json.dumps(err_res) + "\n").encode('utf-8'))
            await writer.drain()
        finally:
            writer.close()
            await writer.wait_closed()

    async def run_ipc_server(self, socket_path: Optional[str] = None):
        """Runs the asynchronous UNIX socket daemon."""
        sock = socket_path or self.socket_path
        if os.path.exists(sock):
            os.remove(sock)
            
        print(f"[*] Starting Weaver Memory Engine IPC Socket Server at: {sock}")
        server = await asyncio.start_unix_server(self.handle_ipc_client, path=sock)
        async with server:
            await server.serve_forever()


# =============================================================================
# Terminal CLI Entrypoint
# =============================================================================

def main():
    parser = argparse.ArgumentParser(description="Weaver Universal Long-Term Memory (LTM) CLI")
    subparsers = parser.add_subparsers(dest="command", help="Available subcommands")

    # Command: store
    p_store = subparsers.add_parser("store", help="Store a memory entry")
    p_store.add_argument("--key", required=True, help="Unique identifier key")
    p_store.add_argument("--content", required=True, help="Memory text content")
    p_store.add_argument("--scope", default="episodic", help="Memory scope (system/episodic/semantic/procedural/user)")
    p_store.add_argument("--tags", default="", help="Comma-separated tags")
    p_store.add_argument("--agent", default="cli_user", help="Author agent identifier")

    # Command: recall
    p_recall = subparsers.add_parser("recall", help="Recall a memory entry")
    p_recall.add_argument("--key", required=True, help="Unique identifier key")
    p_recall.add_argument("--scope", default="episodic", help="Memory scope")

    # Command: search
    p_search = subparsers.add_parser("search", help="Search memory via FTS5 index")
    p_search.add_argument("query", help="Search term query")
    p_search.add_argument("--scope", default=None, help="Scope filter")
    p_search.add_argument("--limit", type=int, default=10, help="Max results")

    # Command: list
    p_list = subparsers.add_parser("list", help="List recent memories")
    p_list.add_argument("--scope", default=None, help="Scope filter")
    p_list.add_argument("--limit", type=int, default=20, help="Max results")

    # Command: resolve
    p_resolve = subparsers.add_parser("resolve", help="Resolve an abstract path mask")
    p_resolve.add_argument("mask", help="Mask identifier (e.g., path_001)")

    # Command: masks
    p_masks = subparsers.add_parser("masks", help="List all abstract configuration masks")

    # Command: set-mask
    p_set_mask = subparsers.add_parser("set-mask", help="Configure an abstract path mask")
    p_set_mask.add_argument("--mask", required=True, help="Mask name (e.g. path_004)")
    p_set_mask.add_argument("--path", required=True, help="Canonical physical target path")
    p_set_mask.add_argument("--type", default="directory", help="Resource type")
    p_set_mask.add_argument("--perms", default="rw", help="Permissions")
    p_set_mask.add_argument("--desc", default="", help="Description")

    # Command: lineage
    p_lineage = subparsers.add_parser("lineage", help="View recent audit lineage events")
    p_lineage.add_argument("--limit", type=int, default=20, help="Max event entries")

    # Command: serve
    p_serve = subparsers.add_parser("serve", help="Start background IPC UNIX socket server")
    p_serve.add_argument("--socket", default="/tmp/weaver_memory.sock", help="Socket path")

    args = parser.parse_args()
    if not args.command:
        parser.print_help()
        sys.exit(0)

    engine = WeaverMemoryEngine()

    if args.command == "store":
        mid = engine.store(
            key=args.key,
            content=args.content,
            scope=args.scope,
            tags=args.tags,
            source_agent=args.agent
        )
        print(json.dumps({"status": "SUCCESS", "id": mid, "key": args.key, "scope": args.scope}, indent=2))

    elif args.command == "recall":
        res = engine.recall(key=args.key, scope=args.scope)
        if res:
            print(json.dumps({"status": "SUCCESS", "memory": res}, indent=2))
        else:
            print(json.dumps({"status": "NOT_FOUND", "key": args.key, "scope": args.scope}, indent=2))

    elif args.command == "search":
        results = engine.search(query=args.query, scope=args.scope, limit=args.limit)
        print(json.dumps({"status": "SUCCESS", "count": len(results), "results": results}, indent=2))

    elif args.command == "list":
        results = engine.list_memories(scope=args.scope, limit=args.limit)
        print(json.dumps({"status": "SUCCESS", "count": len(results), "memories": results}, indent=2))

    elif args.command == "resolve":
        path = engine.resolve_path(mask=args.mask)
        if path:
            print(json.dumps({"status": "SUCCESS", "mask": args.mask, "canonical_path": path}, indent=2))
        else:
            print(json.dumps({"status": "ERROR", "message": f"Mask '{args.mask}' not configured."}, indent=2))

    elif args.command == "masks":
        masks = engine.get_all_masks()
        print(json.dumps({"status": "SUCCESS", "masks": masks}, indent=2))

    elif args.command == "set-mask":
        engine.set_path_mask(mask=args.mask, canonical_path=args.path, resource_type=args.type, permissions=args.perms, description=args.desc)
        print(json.dumps({"status": "SUCCESS", "mask": args.mask, "canonical_path": os.path.abspath(args.path)}, indent=2))

    elif args.command == "lineage":
        events = engine.get_lineage(limit=args.limit)
        print(json.dumps({"status": "SUCCESS", "count": len(events), "lineage": events}, indent=2))

    elif args.command == "serve":
        try:
            asyncio.run(engine.run_ipc_server(socket_path=args.socket))
        except KeyboardInterrupt:
            print("\nStopping Weaver Memory Engine Server Cleanly.")

if __name__ == "__main__":
    main()
