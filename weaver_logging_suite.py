# FILE: weaver_logging_suite.py
# CREATED BY: Grok AI Assistant (Admin-provided Automated Logging Suite; syntax repaired for runnable code)
# DATE: 09-12-2026
# PROJECT: The-Weaver-Engine
# VERSION: 2.0.0-R2026
# ===============================================================================
#
# Description:
#   Autonomous middleware metrics hook — harvests blackboard telemetry, rolling
#   JSON history, ASCII swarm load chart in vector_nodes/.
#
# Syntax repairs vs Admin paste (compaction artifacts):
#   1. import osimport sys → separate os, sys, json, time, datetime
#   2. history = → history = [] (both places)
#   3. history[-selfmax_history_points:] → history[-self.max_history_points:]
#   4. grid[height -  - y_val][x] → grid[height - 1 - y_val][x]
#   5. canvas = → canvas = []
#   6. item["timestamp"][-:] → item["timestamp"][-2:]  # seconds from %H:%M:%S
#   7. history_data[-] → history_data[-1]
#   8. Footer: [CURRENT SYSTEM NODAL STATUS]: {current_status}
#
# ===============================================================================

import os
import sys
import json
import time
from datetime import datetime


class AutomatedLoggingSuite:
    """
    The System Analytics Hook. Continuously monitors the state matrices of
    the engine, logs system performance telemetry, and renders live, text-based
    ASCII line charts directly into the vector memory layer.
    """
    def __init__(self, runtime_root="./weaver_runtime"):
        self.runtime_root = runtime_root
        self.memory_dir = os.path.join(runtime_root, "2_universal_memory_weaver")
        self.blackboard_path = os.path.join(self.memory_dir, "blackboard.json")
        self.metrics_log_path = os.path.join(self.memory_dir, "vector_nodes", "performance_metrics.json")
        self.graph_output_path = os.path.join(self.memory_dir, "vector_nodes", "uptime_dashboard.txt")

        # Max history intervals to preserve for horizontal graph axis width
        self.max_history_points = 20

    def harvest_live_telemetry(self):
        """Extracts data values from the Memory Weaver Blackboard."""
        if not os.path.exists(self.blackboard_path):
            return {"swarm_load": 0, "status_code": 0}

        try:
            with open(self.blackboard_path, 'r', encoding='utf-8') as f:
                state = json.load(f)

            active_swarms = state.get("active_swarms", 0)
            status_str = state.get("system_status", "ONLINE")

            # Map status strings to numerical metrics for graphing arrays
            status_code = 3 if status_str == "PROCESSING_SWARM" else 1
            if status_str == "ONLINE":
                status_code = 2

            return {
                "timestamp": datetime.now().strftime("%H:%M:%S"),
                "swarm_load": active_swarms,
                "status_code": status_code,
                "raw_status": status_str
            }
        except Exception:
            return {"swarm_load": 0, "status_code": 0, "raw_status": "UNKNOWN"}

    def commit_metrics_snapshot(self, snapshot):
        """Appends snapshots to the rolling JSON analytics history matrix."""
        history = []
        if os.path.exists(self.metrics_log_path):
            try:
                with open(self.metrics_log_path, 'r', encoding='utf-8') as f:
                    history = json.load(f)
            except Exception:
                history = []

        history.append(snapshot)

        # Constrain array sliding window size to protect memory overhead
        if len(history) > self.max_history_points:
            history = history[-self.max_history_points:]

        with open(self.metrics_log_path, 'w', encoding='utf-8') as f:
            json.dump(history, f, indent=4)

        return history

    def render_ascii_line_chart(self, history_data):
        """
        Dynamically constructs an ASCII line graph matrix representing
        live swarm system activity load vectors across a timeline.
        """
        if not history_data:
            return "Insufficient metrics data to construct chart framework."

        # Extract numerical arrays for graph rendering
        loads = [item["swarm_load"] for item in history_data]
        max_load = max(loads) if max(loads) > 0 else 4

        # Build graph plot grids (Y-Axis height scaled based on current max burden)
        height = int(max_load) + 1
        width = len(history_data)
        grid = [[" " for _ in range(width)] for _ in range(height)]

        # Map metric points into coordinate coordinates
        for x, item in enumerate(history_data):
            y_val = int(item["swarm_load"])
            # Ensure index constraints don't clip matrix roof boundaries
            if y_val >= height:
                y_val = height - 1
            grid[height - 1 - y_val][x] = "█"  # Filled plot voxel token

        # Construct final text canvas layout report
        canvas = []
        canvas.append("======================================================================")
        canvas.append(f" THE WEAVER ENGINE LIVE INFRASTRUCTURE METRICS MONITOR - v2.0.0-R2026")
        canvas.append(f" REPORT RUNTIME TIMESTAMP: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        canvas.append("======================================================================\n")
        canvas.append(f" [SWARM CLUSTER CONCURRENCY WORKLOAD GRAPH]")

        # Stitch graph lines together with dynamic Y-axis label intervals
        for y_idx in range(height):
            y_label = height - 1 - y_idx
            row_str = "".join(grid[y_idx])
            canvas.append(f"  {y_label} Swarms ┤ {row_str}")

        # Construct dynamic timeline scale axis labels base string
        canvas.append("            └" + "─" * width)
        time_labels = "".join([item["timestamp"][-2:] + " " for item in history_data])
        canvas.append(f"  Sec Index:  {time_labels}\n")

        # Pull latest status string for footer report element
        current_status = history_data[-1]["raw_status"]
        canvas.append(f" [CURRENT SYSTEM NODAL STATUS]: {current_status}")
        canvas.append("======================================================================")

        final_dashboard_output = "\n".join(canvas)

        # Write clean output straight into the text data layer
        with open(self.graph_output_path, 'w', encoding='utf-8') as f:
            f.write(final_dashboard_output)

        return final_dashboard_output

    def run_telemetry_cycle(self):
        """Executes a single end-to-end data metrics capture step."""
        snapshot = self.harvest_live_telemetry()
        history = self.commit_metrics_snapshot(snapshot)
        dashboard_text = self.render_ascii_line_chart(history)
        return dashboard_text


if __name__ == "__main__":
    if not os.path.exists("./weaver_runtime"):
        print("[Error] Initialize the core folders using 'weaver_core.py' first!")
        sys.exit(1)

    suite = AutomatedLoggingSuite()
    print("[Telemetry Node] Launching persistent logging metrics suite tracker...")
    print(f"Monitoring state shifts. Writing live text graph straight to: {os.path.basename(suite.graph_output_path)}")

    # Run a quick telemetry logging sweep loop to generate the initial file asset
    try:
        for loop in range(5):
            print(f" ├── Processing Telemetry Cycle pass #{loop+1}...")
            chart = suite.run_telemetry_cycle()
            time.sleep(1)
        print("\n[Telemetry Node Success] Metrics logged and visual layout compiled. Review 'uptime_dashboard.txt' to view graphs.")
    except KeyboardInterrupt:
        print("\n[Telemetry Node Exception] Process loop stopped safely.")
