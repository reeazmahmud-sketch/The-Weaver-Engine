#!/bin/sh
#
# FILE: weaver_perimeter_setup.sh
# CREATED BY: GitHub Copilot CLI
# DATE: 09-15-2026
# PROJECT: The-Weaver-Engine
# VERSION: 1.0.0
# ==============================================================================
#
# Description:
#   Establishes the Weaver Engine runtime perimeter, metadata marker, FIFO
#   channels, and dynamic zero-touch path matrix.
#
# Usage:
#   ./weaver_perimeter_setup.sh
#
# ==============================================================================

set -eu

PROJECT_ROOT=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
RUNTIME_ROOT="$PROJECT_ROOT/weaver_runtime"
MODULES_ROOT="$RUNTIME_ROOT/1_universal_modules_weaver"
MEMORY_ROOT="$RUNTIME_ROOT/2_universal_memory_weaver"
GATEWAY_ROOT="$RUNTIME_ROOT/3_universal_gateway_server"
CHANNELS_ROOT="$GATEWAY_ROOT/stdio_channels"
CONFIG_PATH="$MEMORY_ROOT/config_matrix.json"

mkdir -p \
    "$MODULES_ROOT/skills" \
    "$MODULES_ROOT/hooks" \
    "$MODULES_ROOT/mcps" \
    "$MODULES_ROOT/engine_core" \
    "$MEMORY_ROOT/vector_nodes" \
    "$CHANNELS_ROOT"

touch "$RUNTIME_ROOT/.metadata_never_index"

ensure_fifo() {
    pipe_path=$1
    if [ -e "$pipe_path" ]; then
        if [ ! -p "$pipe_path" ]; then
            printf 'error: expected FIFO at %s, found a non-FIFO entry\n' "$pipe_path" >&2
            exit 1
        fi
    else
        mkfifo "$pipe_path"
    fi
}

ensure_fifo "$CHANNELS_ROOT/INPUT_STREAM_PIPE.fifo"
ensure_fifo "$CHANNELS_ROOT/OUTPUT_STREAM_PIPE.fifo"

python3 - "$RUNTIME_ROOT" "$CONFIG_PATH" <<'PY'
import json
import os
import sys
import time

runtime_root = os.path.abspath(sys.argv[1])
config_path = os.path.abspath(sys.argv[2])

pillar_paths = {
    "path_001": os.path.join(runtime_root, "1_universal_modules_weaver"),
    "path_002": os.path.join(runtime_root, "2_universal_memory_weaver"),
    "path_003": os.path.join(runtime_root, "3_universal_gateway_server"),
    "path_root": runtime_root,
}

descriptions = {
    "path_001": "Pillar 1 Universal Modules Directory",
    "path_002": "Pillar 2 Universal Memory Directory",
    "path_003": "Pillar 3 Universal Gateway Server Directory",
    "path_root": "Weaver Engine Runtime Root Directory",
}

now = time.time()
payload = {
    "schema_version": "2.0.0",
    "masks": [
        {
            "mask": mask,
            "canonical_path": os.path.abspath(path),
            "resource_type": "directory",
            "permissions": "rw",
            "environment": "sandbox",
            "description": descriptions[mask],
            "version": 1,
            "updated_at": now,
        }
        for mask, path in pillar_paths.items()
    ],
}

with open(config_path, "w", encoding="utf-8") as config_file:
    json.dump(payload, config_file, indent=4)
    config_file.write("\n")
PY

printf 'Weaver perimeter ready: %s\n' "$RUNTIME_ROOT"
