# FILE: weaver_gateway_pipeline.py
# CREATED BY: Grok AI Assistant (Admin-provided Gateway + Module Adapter)
# DATE: 09-10-2026
# PROJECT: The-Weaver-Engine
# VERSION: 2.0.0-R2026
# ===============================================================================
#
# Description:
#   Universal Gateway Server + Universal Module Adapter — JSON-RPC style ingest,
#   skill/plugin routing, subprocess hooks, stdio_channels responses.
#
# ===============================================================================

import os
import sys
import json
import time
import queue
import subprocess
from datetime import datetime

class UniversalModuleAdapter:
    """
    The dynamic execution interface proxy. It ingests tools, playbooks, 
    or raw script execution targets and runs them securely, mapping 
    inputs and outputs dynamically.
    """
    def __init__(self, modules_dir):
        self.modules_dir = modules_dir

    def execute_primitive(self, primitive_name, payload):
        """
        Dynamically routes execution based on the module type.
        Supports Markdown Skills, local Python plugins, or external MCP configurations.
        """
        print(f"    [Module Adapter] Resolving target wrapper for: '{primitive_name}'")
        
        # Check if it's a structural Skill playbook
        skill_path = os.path.join(self.modules_dir, "skills", f"{primitive_name}.md")
        plugin_path = os.path.join(self.modules_dir, "hooks", f"{primitive_name}.py")
        
        if os.path.exists(plugin_path):
            # Dynamic Code Execution Wrapper Pattern
            print(f"    [Module Adapter] Executing language plugin script natively via subprocess channel...")
            try:
                # Passes payload safely to a detached process loop via JSON serialization
                proc = subprocess.Popen(
                    [sys.executable, plugin_path, json.dumps(payload)],
                    stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
                )
                stdout, stderr = proc.communicate(timeout=5)
                if proc.returncode == 0:
                    return {"status": "SUCCESS", "output": stdout.strip()}
                else:
                    return {"status": "EXECUTION_ERROR", "error": stderr.strip()}
            except Exception as e:
                return {"status": "ADAPTER_EXCEPTION", "error": str(e)}
                
        elif os.path.exists(skill_path):
            # Text Playbook Interpretation Wrapper Pattern
            print(f"    [Module Adapter] Ingesting text playbook context target directly into runtime...")
            return {
                "status": "SUCCESS", 
                "output": f"Executed semantic skill playbook structure with payload items: {payload}"
            }
            
        else:
            return {"status": "NOT_FOUND", "error": f"Primitive module '{primitive_name}' could not be resolved."}

class UniversalGatewayServer:
    """
    The unified communication perimeter boundary. Converts incoming API, network, 
    or text console frames into standardized internal task operations.
    """
    def __init__(self, runtime_root="./weaver_runtime"):
        self.runtime_root = runtime_root
        self.modules_dir = os.path.join(runtime_root, "1_universal_modules_weaver")
        self.gateway_dir = os.path.join(runtime_root, "3_universal_gateway_server")
        
        self.adapter = UniversalModuleAdapter(self.modules_dir)
        self.incoming_queue = queue.Queue()
        
        print("\n============================================================")
        print("   THE WEAVER ENGINE CORE - UNIVERSAL GATEWAY INITIALIZED   ")
        print("============================================================")
        self.bootstrap_gateway_pipes()

    def bootstrap_gateway_pipes(self):
        """Prepares physical systemic file paths for IO communications."""
        # Creates mock script to serve as a dynamically loaded native hook/plugin
        mock_hook_path = os.path.join(self.modules_dir, "hooks", "crypto_sign.py")
        if not os.path.exists(mock_hook_path):
            with open(mock_hook_path, "w", encoding="utf-8") as f:
                f.write("import sys\nimport json\nimport hashlib\n")
                f.write("if __name__ == '__main__':\n")
                f.write("    input_data = json.loads(sys.argv[1]) if len(sys.argv) > 1 else {}\n")
                f.write("    raw_string = input_data.get('data', '')\n")
                f.write("    hashed = hashlib.md5(raw_string.encode()).hexdigest()\n")
                f.write("    print(json.dumps({'verification_hash': hashed}))\n")

    def submit_incoming_network_request(self, external_packet_json):
        """Simulates receiving a JSON-RPC network transaction chunk over a socket interface."""
        try:
            packet = json.loads(external_packet_json)
            print(f"\n[Gateway Server] Network packet received! ID: {packet.get('id')} | Method: {packet.get('method')}")
            self.incoming_queue.put(packet)
        except Exception as e:
            print(f"[Gateway Error] Dropping malformed transaction packet frame: {str(e)}")

    def process_gateway_pipeline(self):
        """Processes queued requests, passing tasks down to the Adapter layer."""
        if self.incoming_queue.empty():
            print("[Gateway Server] Zero processing queues active in channel buffer.")
            return

        while not self.incoming_queue.empty():
            packet = self.incoming_queue.get()
            target_method = packet.get("method")
            params = packet.get("params", {})
            
            print(f"[Gateway Server] Ingesting method payload into Module Adapter...")
            result = self.adapter.execute_primitive(target_method, params)
            
            # Write final network frame response transmission out to stdio channels
            response_file = os.path.join(self.gateway_dir, "stdio_channels", f"response_{packet.get('id')}.json")
            with open(response_file, 'w', encoding='utf-8') as f:
                json.dump({"id": packet.get("id"), "execution_result": result}, f, indent=4)
                
            print(f"[Gateway Server] Output response transmission packet committed to disk: {os.path.basename(response_file)}")

if __name__ == "__main__":
    if not os.path.exists("./weaver_runtime"):
        print("[Error] Initialize the main filesystem footprint by running 'weaver_core.py' first!")
        sys.exit(1)
        
    gateway = UniversalGatewayServer()
    
    # 1. Simulating an incoming network frame calling a semantic markdown playbook skill
    mock_network_request_1 = json.dumps({
        "id": "tx_9001",
        "method": "data_parser",
        "params": {"text_stream": "Logistics metrics dump string"}
    })
    
    # 2. Simulating an incoming network frame calling a dynamically loaded language code hook module
    mock_network_request_2 = json.dumps({
        "id": "tx_9002",
        "method": "crypto_sign",
        "params": {"data": "Secure-Weaver-Transaction-Payload-Verification-String"}
    })
    
    # Inject both simulation frames through the Gateway boundary layers
    gateway.submit_incoming_network_request(mock_network_request_1)
    gateway.submit_incoming_network_request(mock_network_request_2)
    
    # Fire the loop pipeline engine to translate, adapt, and resolve execution actions
    time.sleep(1)
    gateway.process_gateway_pipeline()
