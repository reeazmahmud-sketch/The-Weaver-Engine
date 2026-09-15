"""
FILE: gateway_engine.py
CREATED BY: Copilot Assistant (Admin-provided Gateway & macOS Subsystems Blueprint)
DATE: 09-15-2026
PROJECT: The-Weaver-Engine / Pillar 3 Universal Gateway Server
VERSION: 2.1.0-R2026

Description:
  Asynchronous UNIX Socket Stream Server & macOS Subsystem Execution Gateway.
  Listens at /tmp/weaver_gateway.sock, parses and validates input payloads,
  and safely routes execution to native AppleScript (osascript) or guarded
  subprocesses with strict token blocklists and Zero-Touch path configuration.
"""

import os
import sys
import json
import asyncio
import subprocess
from typing import Optional

# Optional Pydantic / Pydantic AI integration with robust fallback
try:
    from pydantic import BaseModel, Field
    HAS_PYDANTIC = True
except ImportError:
    HAS_PYDANTIC = False
    class BaseModel:
        def __init__(self, **data):
            for k, v in data.items():
                setattr(self, k, v)
        def dict(self):
            return self.__dict__
    def Field(description=None, default=None):
        return default

try:
    from pydantic_ai import Agent, RunContext
    HAS_PYDANTIC_AI = True
except ImportError:
    HAS_PYDANTIC_AI = False
    Agent = None
    RunContext = None


# ==========================================
# 1. System Automation Schemas & Config
# ==========================================

class MacAutomationAction(BaseModel):
    """Defines clean routing for macOS application commands and bash environments."""
    if HAS_PYDANTIC:
        subsystem: str = Field(description="Must be 'applescript' or 'bash_cli'.")
        target_app: str = Field(description="Target app name (e.g., 'Finder', 'Terminal', 'System Events') or 'shell'.")
        script_payload: str = Field(description="The executable code string or raw bash payload.")
        justification: str = Field(description="Architectural safety reasoning for mutating host parameters.")
    else:
        subsystem: str = "bash_cli"
        target_app: str = "shell"
        script_payload: str = ""
        justification: str = ""


class GatewayEnv:
    SOCKET_PATH = "/tmp/weaver_gateway.sock"
    PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    RUNTIME_ROOT = os.path.join(PROJECT_ROOT, "weaver_runtime")
    CONFIG_MATRIX = {
        "path_001": os.path.join(RUNTIME_ROOT, "1_universal_modules_weaver"),
        "path_002": os.path.join(RUNTIME_ROOT, "2_universal_memory_weaver"),
        "path_003": os.path.join(RUNTIME_ROOT, "3_universal_gateway_server"),
        "path_root": RUNTIME_ROOT
    }


# ==========================================
# 2. Subsystem Execution & Safety Guards
# ==========================================

def execute_mac_subsystem(action: MacAutomationAction) -> str:
    """Executes validated system tasks safely within the native host macOS platform."""
    subsystem = action.subsystem if hasattr(action, 'subsystem') else getattr(action, 'subsystem', 'bash_cli')
    payload = action.script_payload if hasattr(action, 'script_payload') else getattr(action, 'script_payload', '')

    if subsystem == "applescript":
        try:
            # Compile and execute modern AppleScript expressions safely using the system osascript binary
            process = subprocess.Popen(
                ['osascript', '-e', payload],
                stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
            )
            stdout, stderr = process.communicate(timeout=10)
            if process.returncode != 0:
                return f"AppleScript Execution Failure: {stderr.strip()}"
            return f"AppleScript Success: {stdout.strip() if stdout else 'Executed cleanly.'}"
        except subprocess.TimeoutExpired:
            process.kill()
            return "AppleScript Execution Timeout: Process exceeded 10s limit."
        except Exception as e:
            return f"AppleScript Exception: {str(e)}"

    elif subsystem == "bash_cli":
        # Block dangerous destructive command combinations explicitly
        blacklisted_tokens = ["rm -rf /", "rm -rf ~", "mkfs", "dd if=", ":(){ :|:& };:"]
        if any(token in payload for token in blacklisted_tokens):
            return "Execution Rejected: Destructive command token detected in payload stream."

        try:
            # Execute guarded command
            process = subprocess.Popen(
                payload, shell=True,
                stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
            )
            stdout, stderr = process.communicate(timeout=15)
            return f"CLI Run Complete. Output: {stdout.strip()} Error: {stderr.strip()}"
        except subprocess.TimeoutExpired:
            process.kill()
            return "CLI Run Timeout: Process exceeded 15s limit."
        except Exception as e:
            return f"CLI Exception: {str(e)}"

    return "Unknown gateway subsystem action routing type specified."


def parse_raw_signal(message: str) -> MacAutomationAction:
    """Fallback deterministic parser when LLM agent is not initialized or for raw JSON signals."""
    try:
        data = json.loads(message)
        if isinstance(data, dict) and "subsystem" in data and "script_payload" in data:
            return MacAutomationAction(
                subsystem=data.get("subsystem", "bash_cli"),
                target_app=data.get("target_app", "shell"),
                script_payload=data.get("script_payload", ""),
                justification=data.get("justification", "JSON-RPC direct invocation")
            )
    except Exception:
        pass

    # Heuristic parsing for text commands
    msg_lower = message.lower()
    if msg_lower.startswith("tell app") or "system events" in msg_lower or "display dialog" in msg_lower or "set volume" in msg_lower:
        return MacAutomationAction(
            subsystem="applescript",
            target_app="System Events",
            script_payload=message,
            justification="AppleScript heuristic syntax match"
        )
    else:
        return MacAutomationAction(
            subsystem="bash_cli",
            target_app="shell",
            script_payload=message,
            justification="Direct shell command invocation"
        )


# ==========================================
# 3. Agent Initialization (if available)
# ==========================================

gateway_agent = None
if HAS_PYDANTIC_AI:
    try:
        gateway_agent = Agent(
            'openai:gpt-4o',
            result_type=MacAutomationAction,
            system_prompt=(
                "You are the network gateway component of the Binary Weaver Engine. "
                "Your task is to take raw text stream signals passed through system pipes "
                "and securely structure them into valid AppleScript scripts or safe terminal execution paths."
            )
        )
    except Exception:
        gateway_agent = None


# ==========================================
# 4. Asynchronous Unix Socket Stream Server
# ==========================================

async def handle_stream_pipe(reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
    """Processes fast-throughput asynchronous input directly from standard POSIX streams."""
    try:
        data = await reader.read(4096)
        message = data.decode('utf-8').strip()

        if not message:
            writer.close()
            await writer.wait_closed()
            return

        print(f"\n[*] Incoming Network Pipeline Signal Captured: '{message}'")

        # Process message through Pydantic AI validation or fallback parser
        context = GatewayEnv()
        action = None

        if gateway_agent and os.getenv("OPENAI_API_KEY"):
            try:
                result = await gateway_agent.run(message, deps=context)
                action = result.output
            except Exception as e:
                print(f"[!] Pydantic AI inference failed ({e}), falling back to deterministic parser.")
                action = parse_raw_signal(message)
        else:
            action = parse_raw_signal(message)

        print(f"[+] Structured Matrix Verified: {action.subsystem.upper()} -> {action.target_app}")
        print(f"[+] Justification: {action.justification}")

        # Run structural host changes
        execution_result = execute_mac_subsystem(action)
        print(f"[=] Engine Execution Output: {execution_result}")

        # Write back output responses to the stream connection pipe
        response_payload = {
            "status": "SUCCESS",
            "subsystem": action.subsystem,
            "target_app": action.target_app,
            "result": execution_result
        }
        writer.write((json.dumps(response_payload, indent=2) + "\n").encode('utf-8'))
        await writer.drain()
    except Exception as e:
        err_msg = json.dumps({"status": "ERROR", "error": str(e)}) + "\n"
        writer.write(err_msg.encode('utf-8'))
        await writer.drain()
    finally:
        writer.close()
        await writer.wait_closed()


async def run_gateway_server():
    context = GatewayEnv()

    # Clean up old sockets safely if they exist in volatile storage
    if os.path.exists(context.SOCKET_PATH):
        try:
            os.remove(context.SOCKET_PATH)
        except OSError:
            pass

    print(f"🚀 Initializing Sovereignty Daemon on IPC Socket Pipe: {context.SOCKET_PATH}")
    server = await asyncio.start_unix_server(handle_stream_pipe, path=context.SOCKET_PATH)

    async with server:
        await server.serve_forever()


if __name__ == "__main__":
    try:
        asyncio.run(run_gateway_server())
    except KeyboardInterrupt:
        print("\nStopping Binary Weaver Gateway Server Daemon Cleanly.")
