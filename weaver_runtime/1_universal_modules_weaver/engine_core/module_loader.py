"""Discover Weaver skills, hooks, and MCP definitions without machine-local paths."""

from __future__ import annotations

import ast
import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Dict, Iterable, Optional


@dataclass(frozen=True)
class ModuleRecord:
    """Normalized registry entry for one runtime module."""

    name: str
    module_type: str
    relative_path: str
    signature: Dict[str, Any]
    metadata: Dict[str, Any]

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class ModuleLoader:
    """Scan a modules pillar and build a deterministic runtime registry."""

    _PATTERNS = {
        "skill": ("skills", "*.md"),
        "hook": ("hooks", "*.py"),
        "mcp": ("mcps", "*.json"),
    }

    def __init__(self, modules_root: Optional[str | Path] = None) -> None:
        base = Path(__file__).resolve().parents[1]
        self.modules_root = self._resolve_root(modules_root, base)

    @staticmethod
    def _resolve_root(value: Optional[str | Path], default: Path) -> Path:
        if value is None:
            return default
        candidate = Path(value)
        return candidate if candidate.is_absolute() else (Path.cwd() / candidate).resolve()

    def scan(self) -> Dict[str, Dict[str, Any]]:
        """Return module records keyed by a stable module name."""
        registry: Dict[str, Dict[str, Any]] = {}
        for module_type, (folder, pattern) in self._PATTERNS.items():
            for path in sorted((self.modules_root / folder).glob(pattern)):
                record = self._inspect(path, module_type)
                registry[record.name] = record.to_dict()
        return dict(sorted(registry.items()))

    def build_registry_index(self, output_path: Optional[str | Path] = None) -> Dict[str, Dict[str, Any]]:
        """Build the registry and optionally persist it as JSON."""
        registry = self.scan()
        if output_path is not None:
            destination = Path(output_path)
            if not destination.is_absolute():
                destination = Path.cwd() / destination
            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.write_text(json.dumps(registry, indent=2, sort_keys=True), encoding="utf-8")
        return registry

    def _inspect(self, path: Path, module_type: str) -> ModuleRecord:
        relative_path = path.relative_to(self.modules_root).as_posix()
        if module_type == "skill":
            metadata = self._markdown_metadata(path)
            signature = {"format": "markdown", "sections": metadata["sections"]}
        elif module_type == "hook":
            metadata, signature = self._python_metadata(path)
        else:
            metadata, signature = self._mcp_metadata(path)
        return ModuleRecord(path.stem, module_type, relative_path, signature, metadata)

    @staticmethod
    def _markdown_metadata(path: Path) -> Dict[str, Any]:
        lines = path.read_text(encoding="utf-8").splitlines()
        sections = [line.lstrip("#").strip() for line in lines if line.startswith("#")]
        description = next(
            (line[2:].strip() for line in lines if line.startswith("- ") and line[2:].strip()),
            "",
        )
        return {"sections": sections, "description": description, "line_count": len(lines)}

    @staticmethod
    def _python_metadata(path: Path) -> tuple[Dict[str, Any], Dict[str, Any]]:
        source = path.read_text(encoding="utf-8")
        tree = ast.parse(source, filename=path.name)
        functions = [
            node.name
            for node in ast.walk(tree)
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
        ]
        classes = [node.name for node in ast.walk(tree) if isinstance(node, ast.ClassDef)]
        metadata = {"docstring": ast.get_docstring(tree) or "", "line_count": len(source.splitlines())}
        signature = {"functions": functions, "classes": classes, "entrypoint": "__main__" in source}
        return metadata, signature

    @staticmethod
    def _mcp_metadata(path: Path) -> tuple[Dict[str, Any], Dict[str, Any]]:
        document = json.loads(path.read_text(encoding="utf-8"))
        metadata = {
            "description": document.get("description", ""),
            "schema_version": document.get("schema_version"),
        }
        signature = {
            "keys": sorted(document.keys()),
            "tools": document.get("tools", []),
        }
        return metadata, signature
