"""Fail-closed execution proxy for Weaver skills and Python hooks."""

from __future__ import annotations

import ast
import json
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, Mapping, Optional

from .language_converter import MarkdownLanguageConverter


class ModuleSecurityError(ValueError):
    """Raised when a module violates adapter safety rules."""


class ModuleExecutionError(RuntimeError):
    """Raised when a hook cannot complete successfully."""


class ModuleAdapter:
    """Validate and execute registered skills/hooks with bounded resources."""

    FORBIDDEN_TOKENS = frozenset(
        {"rm -rf", "sudo", "curl ", "wget ", "bash -c", "sh -c", "osascript", "|", "&&", ";", "`"}
    )

    def __init__(self, modules_root: Optional[str | Path] = None, timeout: float = 5.0) -> None:
        base = Path(__file__).resolve().parents[1]
        root = base if modules_root is None else Path(modules_root)
        self.modules_root = (Path.cwd() / root).resolve() if not root.is_absolute() else root.resolve()
        self.timeout = timeout
        self.converter = MarkdownLanguageConverter()

    def execute(self, module_name: str, payload: Mapping[str, Any] | None = None) -> Dict[str, Any]:
        if not module_name or Path(module_name).name != module_name:
            raise ModuleSecurityError("module name must be a simple file stem")
        request = dict(payload or {})
        self._validate_payload(request)

        hook = self.modules_root / "hooks" / f"{module_name}.py"
        skill = self.modules_root / "skills" / f"{module_name}.md"
        if hook.is_file():
            self._validate_python(hook)
            return self._execute_hook(hook, request)
        if skill.is_file():
            return {
                "status": "DECLARED",
                "module": module_name,
                "tool": self.converter.convert_file(skill),
                "payload": request,
            }
        raise FileNotFoundError(f"module not found: {module_name}")

    @classmethod
    def _validate_payload(cls, payload: Mapping[str, Any]) -> None:
        try:
            encoded = json.dumps(payload)
        except (TypeError, ValueError) as exc:
            raise ModuleSecurityError("payload must be JSON serializable") from exc
        lowered = encoded.lower()
        if any(token in lowered for token in cls.FORBIDDEN_TOKENS):
            raise ModuleSecurityError("payload contains a forbidden shell token")
        for value in payload.values():
            if isinstance(value, str) and Path(value).is_absolute():
                raise ModuleSecurityError("absolute paths are not permitted in payloads")

    @classmethod
    def _validate_python(cls, path: Path) -> None:
        source = path.read_text(encoding="utf-8")
        lowered = source.lower()
        if any(token in lowered for token in cls.FORBIDDEN_TOKENS):
            raise ModuleSecurityError(f"hook contains a forbidden shell token: {path.name}")
        tree = ast.parse(source, filename=path.name)
        for node in ast.walk(tree):
            if isinstance(node, ast.Constant) and isinstance(node.value, str):
                if Path(node.value).is_absolute():
                    raise ModuleSecurityError(f"hook contains a hardcoded absolute path: {path.name}")
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id in {"eval", "exec"}:
                raise ModuleSecurityError(f"hook uses forbidden dynamic execution: {path.name}")

    def _execute_hook(self, path: Path, payload: Dict[str, Any]) -> Dict[str, Any]:
        try:
            completed = subprocess.run(
                [sys.executable, str(path), json.dumps(payload)],
                capture_output=True,
                text=True,
                timeout=self.timeout,
                check=False,
                cwd=str(self.modules_root),
            )
        except subprocess.TimeoutExpired as exc:
            raise ModuleExecutionError(f"hook timed out after {self.timeout:.2f}s") from exc
        if completed.returncode != 0:
            raise ModuleExecutionError(completed.stderr.strip() or f"hook exited with {completed.returncode}")
        output = completed.stdout.strip()
        try:
            parsed: Any = json.loads(output) if output else None
        except json.JSONDecodeError:
            parsed = output
        return {"status": "SUCCESS", "module": path.stem, "output": parsed}
