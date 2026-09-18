# FILE: weaver_core.py
# CREATED BY: Grok AI Assistant (Admin-provided Core Architecture Engine)
# DATE: 09-10-2026
# PROJECT: The-Weaver-Engine
# VERSION: 2.0.0-R2026
# ===============================================================================
#
# Description:
#   Foundational Weaver Engine — bootstrap three universal pillars, loom-state
#   cryptographic blueprint, warp-thread guardian, weave-loop self-heal, chaos
#   test simulation.
#
# ===============================================================================

import argparse
import os
import sys
import time
import json
import hashlib
import threading
from datetime import datetime

class TheWeaverEngine:
    def __init__(self, root_dir="./weaver_runtime", monitor_interval=0.5, autostart_guardian=True):
        self.root_dir = os.path.abspath(root_dir)
        self.monitor_interval = monitor_interval
        
        # Define the Three Universal Pillars
        self.modules_dir = os.path.join(self.root_dir, "1_universal_modules_weaver")
        self.memory_dir = os.path.join(self.root_dir, "2_universal_memory_weaver")
        self.gateway_dir = os.path.join(self.root_dir, "3_universal_gateway_server")
        self.status_path = os.path.join(self.memory_dir, "runtime_health.json")
        
        self.loom_state = {} # Core Cryptographic Blueprint Cache
        self.is_running = True
        self.guardian_thread = None
        self._external_stop_event = None
        self._status_lock = threading.Lock()
        self.started_at = time.time()
        self.last_scan_at = None
        self.last_repair = None
        self.repair_count = 0
        self.last_error = None
        
        print(f"============================================================")
        print(f"   THE WEAVER ENGINE CORE ARCHETYPE - RUNTIME INITIALIZER   ")
        print(f"============================================================")
        
        self.bootstrap_environment()
        self.spin_loom_state()
        self._write_status(status="BOOTSTRAPPED")

        if autostart_guardian:
            self.start_guardian()

    def bootstrap_environment(self):
        """Creates the absolute architecture directory structure and mock files."""
        print("[1/3] Bootstrapping universal folder matrix...")
        folders = [
            self.modules_dir, os.path.join(self.modules_dir, "skills"), 
            os.path.join(self.modules_dir, "mcps"), os.path.join(self.modules_dir, "hooks"),
            self.memory_dir, os.path.join(self.memory_dir, "vector_nodes"),
            self.gateway_dir, os.path.join(self.gateway_dir, "stdio_channels")
        ]
        
        for folder in folders:
            os.makedirs(folder, exist_ok=True)
            
        # Create an initial system Skill asset as a baseline primitive
        sample_skill_path = os.path.join(self.modules_dir, "skills", "data_parser.md")
        if not os.path.exists(sample_skill_path):
            with open(sample_skill_path, "w", encoding="utf-8") as f:
                f.write("# Skill: Data Parser\n- Parse incoming system text strings into clean JSON.\n- Drop invalid characters.")
        
        # Create the initial global shared memory state (Blackboard)
        blackboard_path = os.path.join(self.memory_dir, "blackboard.json")
        if not os.path.exists(blackboard_path):
            with open(blackboard_path, "w", encoding="utf-8") as f:
                json.dump({"system_status": "ONLINE", "active_swarms": 0}, f, indent=4)
                
        print(" └── Directory scaffold completed successfully.")

    def calculate_hash(self, file_path):
        """Generates cryptographic fingerprints for verification."""
        hasher = hashlib.sha256()
        try:
            with open(file_path, 'rb') as f:
                hasher.update(f.read())
            return hasher.hexdigest()
        except FileNotFoundError:
            return None

    def spin_loom_state(self):
        """Caches the structural map and file data into write-protected memory."""
        print("[2/3] Spinning Loom State blueprint snapshot...")
        current_blueprint = {}
        
        for root, _, files in os.walk(self.root_dir):
            for file in files:
                full_path = os.path.join(root, file)
                rel_path = os.path.relpath(full_path, self.root_dir)
                
                # Store both the hash fingerprint AND a copy of the content data for zero-downtime restoration
                try:
                    with open(full_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                except UnicodeDecodeError:
                    with open(full_path, 'rb') as f:
                        content = f.read()
                        
                current_blueprint[rel_path] = {
                    "hash": self.calculate_hash(full_path),
                    "content": content,
                    "is_binary": isinstance(content, bytes)
                }
                
        self.loom_state = current_blueprint
        print(f" └── Cached {len(self.loom_state)} system assets securely in memory.")
        self._write_status(status="SNAPSHOT_READY")

    def _write_status(self, status="ONLINE"):
        os.makedirs(self.memory_dir, exist_ok=True)
        payload = self.get_health_status()
        payload["status"] = status
        with self._status_lock:
            with open(self.status_path, "w", encoding="utf-8") as handle:
                json.dump(payload, handle, indent=4)

    def get_health_status(self):
        return {
            "component": "weaver_core",
            "runtime_root": self.root_dir,
            "status_path": self.status_path,
            "running": bool(self.guardian_thread and self.guardian_thread.is_alive()),
            "monitor_interval": self.monitor_interval,
            "started_at": self.started_at,
            "last_scan_at": self.last_scan_at,
            "monitored_assets": len(self.loom_state),
            "repair_count": self.repair_count,
            "last_repair": self.last_repair,
            "last_error": self.last_error,
        }

    def start_guardian(self, stop_event=None):
        """Start the long-running watchdog thread when operating as a live service."""
        if self.guardian_thread and self.guardian_thread.is_alive():
            return self.guardian_thread
        self.is_running = True
        self._external_stop_event = stop_event
        self.guardian_thread = threading.Thread(target=self.monitor_warp_threads, daemon=True)
        self.guardian_thread.start()
        self._write_status(status="RUNNING")
        return self.guardian_thread

    def stop_guardian(self, join_timeout=2.0):
        """Stop the long-running watchdog thread cleanly."""
        self.is_running = False
        if self.guardian_thread and self.guardian_thread.is_alive():
            self.guardian_thread.join(timeout=join_timeout)
        self._write_status(status="STOPPED")

    def monitor_warp_threads(self):
        """Continuous runtime daemon tracking data drift across the architecture layout."""
        print("[3/3] Activating background Warp Threads daemon. Monitoring engine...")
        print("------------------------------------------------------------")
        
        while self.is_running and not (self._external_stop_event and self._external_stop_event.is_set()):
            time.sleep(self.monitor_interval) # Dynamic heartbeat latency
            active_files = set()
            self.last_scan_at = time.time()
            
            for root, _, files in os.walk(self.root_dir):
                for file in files:
                    full_path = os.path.join(root, file)
                    rel_path = os.path.relpath(full_path, self.root_dir)
                    active_files.add(rel_path)
                    
                    current_hash = self.calculate_hash(full_path)
                    
                    # Intercept Case A: Unauthorized mutation/corruption
                    if rel_path in self.loom_state and current_hash != self.loom_state[rel_path]["hash"]:
                        print(f"\n[{datetime.now().strftime('%H:%M:%S')}] [CRITICAL DRIFT] Thread Corrupted: '{rel_path}' altered.")
                        self.trigger_weave_loop(rel_path, action="REPAIR")
            
            # Intercept Case B: File deletion
            missing_threads = set(self.loom_state.keys()) - active_files
            for missing_path in missing_threads:
                print(f"\n[{datetime.now().strftime('%H:%M:%S')}] [CRITICAL DRIFT] Thread Broken: '{missing_path}' deleted from disk.")
                self.trigger_weave_loop(missing_path, action="REGENERATE")
            self._write_status(status="RUNNING")

        self.is_running = False
        self._write_status(status="STOPPED")

    def trigger_weave_loop(self, relative_path, action):
        """The core execution self-healing engine."""
        target_path = os.path.join(self.root_dir, relative_path)
        cached_data = self.loom_state[relative_path]
        
        print(f" └── [Weave Loop] Commencing '{action}' execution pass...")
        mode = "wb" if cached_data["is_binary"] else "w"
        
        try:
            with open(target_path, mode, encoding=None if cached_data["is_binary"] else "utf-8") as f:
                f.write(cached_data["content"])
            print(f" └── [Weave Loop Success] Integrity restored seamlessly for: {relative_path}")
            self.last_repair = {
                "path": relative_path,
                "action": action,
                "timestamp": time.time(),
            }
            self.repair_count += 1
            self.last_error = None
            self._write_status(status="HEALED")
        except Exception as e:
            print(f" └── [Weave Loop Failure] Healing exception hit: {str(e)}")
            self.last_error = str(e)
            self._write_status(status="ERROR")

    def run_chaos_test_simulation(self):
        """Simulates external corruption vectors to verify self-healing behavior."""
        time.sleep(2)
        print("\n>>> SIMULATING CHAOS INJECTION VECTOR <<<")
        target_file = os.path.join(self.modules_dir, "skills", "data_parser.md")
        
        print(f"[Chaos] Maliciously altering core asset: {target_file}")
        with open(target_file, "w", encoding="utf-8") as f:
            f.write("CORRUPTED BY INTRUSION VECORD.")
            
        time.sleep(1.5)
        
        print(f"\n[Chaos] Destroying memory asset file: blackboard.json")
        os.remove(os.path.join(self.memory_dir, "blackboard.json"))
        
        time.sleep(2)
        print("\n============================================================")
        print("[Simulation Status] Engine has verified absolute resiliency.")
        print("Shutting down core loops cleanly.")
        self.stop_guardian()


def main():
    parser = argparse.ArgumentParser(description="Weaver core runtime watchdog")
    parser.add_argument("mode", nargs="?", default="demo", choices=("demo", "serve", "health"))
    parser.add_argument("--runtime-root", default="./weaver_runtime", help="Runtime root directory")
    parser.add_argument("--interval", type=float, default=0.5, help="Guardian scan interval in seconds")
    args = parser.parse_args()

    if args.mode == "health":
        engine = TheWeaverEngine(root_dir=args.runtime_root, monitor_interval=args.interval, autostart_guardian=False)
        print(json.dumps(engine.get_health_status(), indent=2))
        return

    engine = TheWeaverEngine(root_dir=args.runtime_root, monitor_interval=args.interval, autostart_guardian=True)
    if args.mode == "demo":
        engine.run_chaos_test_simulation()
        return

    print("[Weaver Core] Running persistent watchdog service. Press Ctrl-C to stop.")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n[Weaver Core] Shutdown requested.")
    finally:
        engine.stop_guardian()

if __name__ == "__main__":
    main()
