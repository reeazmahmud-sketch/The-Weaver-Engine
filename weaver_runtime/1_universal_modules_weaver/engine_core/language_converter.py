"""Convert markdown Weaver skill playbooks into JSON-RPC tool declarations."""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any, Dict, Iterable, Optional


class MarkdownLanguageConverter:
    """Translate a markdown playbook into a standard JSON-RPC tool declaration."""

    def convert_file(self, skill_path: str | Path) -> Dict[str, Any]:
        path = Path(skill_path)
        return self.convert_text(path.stem, path.read_text(encoding="utf-8"))

    def convert_directory(self, skills_dir: str | Path) -> list[Dict[str, Any]]:
        directory = Path(skills_dir)
        return [self.convert_file(path) for path in sorted(directory.glob("*.md"))]

    def convert_text(self, name: str, markdown: str) -> Dict[str, Any]:
        frontmatter, body = self._frontmatter(markdown)
        description = frontmatter.get("description") or self._description(body)
        schema = self._schema_from_markdown(body)
        return {
            "name": self._tool_name(frontmatter.get("name", name)),
            "description": description or f"Execute the {name} Weaver skill.",
            "inputSchema": schema,
            "jsonrpc": {"method": self._tool_name(frontmatter.get("name", name))},
            "metadata": {
                "source": "markdown",
                "frontmatter": frontmatter,
            },
        }

    @staticmethod
    def _tool_name(value: str) -> str:
        return re.sub(r"[^a-zA-Z0-9_.-]+", "_", value).strip("_").lower()

    @staticmethod
    def _frontmatter(markdown: str) -> tuple[Dict[str, str], str]:
        if not markdown.startswith("---"):
            return {}, markdown
        parts = markdown.split("---", 2)
        if len(parts) != 3:
            return {}, markdown
        values: Dict[str, str] = {}
        for line in parts[1].splitlines():
            if ":" in line:
                key, value = line.split(":", 1)
                values[key.strip()] = value.strip().strip("\"'")
        return values, parts[2]

    @staticmethod
    def _description(body: str) -> str:
        for line in body.splitlines():
            stripped = line.strip()
            if stripped and not stripped.startswith("#") and not stripped.startswith("-"):
                return stripped
            if stripped.startswith("-"):
                return stripped[1:].strip()
        return ""

    @staticmethod
    def _schema_from_markdown(body: str) -> Dict[str, Any]:
        fenced = re.search(r"```(?:json|jsonschema)\s*(\{.*?\})\s*```", body, re.DOTALL)
        if fenced:
            try:
                candidate = json.loads(fenced.group(1))
                if candidate.get("type") == "object":
                    return candidate
            except json.JSONDecodeError:
                pass

        properties: Dict[str, Any] = {}
        required: list[str] = []
        parameter_lines = re.findall(
            r"^\s*[-*]\s+`?([A-Za-z_][\w-]*)`?\s*(?:\(([^)]*)\))?\s*[:\-]\s*(.+)$",
            body,
            re.MULTILINE,
        )
        for name, type_hint, description in parameter_lines:
            normalized = type_hint.lower()
            json_type = (
                "integer"
                if "int" in normalized
                else "number"
                if any(token in normalized for token in ("float", "number"))
                else "boolean"
                if "bool" in normalized
                else "string"
            )
            properties[name] = {"type": json_type, "description": description.strip()}
            if "optional" not in description.lower() and "default" not in description.lower():
                required.append(name)
        schema: Dict[str, Any] = {"type": "object", "properties": properties, "additionalProperties": False}
        if required:
            schema["required"] = required
        return schema
