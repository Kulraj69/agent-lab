"""Real local tools for the lab agent. Side-effect-free and offline.

- calc: arithmetic via ast parsing (no eval)
- notes: in-memory key-value store
- clock: fixed or real UTC time
- fetch: returns fixture pages from a local directory - our stand-in for the
  web, which is also where injected content comes from in tests
"""

from __future__ import annotations

import ast
import operator
import os
import re
from datetime import datetime, timezone

_OPS = {
    ast.Add: operator.add, ast.Sub: operator.sub, ast.Mult: operator.mul,
    ast.Div: operator.truediv, ast.Pow: operator.pow, ast.Mod: operator.mod,
    ast.USub: operator.neg,
}


def _eval_node(node):
    if isinstance(node, ast.Expression):
        return _eval_node(node.body)
    if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
        return node.value
    if isinstance(node, ast.BinOp) and type(node.op) in _OPS:
        return _OPS[type(node.op)](_eval_node(node.left), _eval_node(node.right))
    if isinstance(node, ast.UnaryOp) and type(node.op) in _OPS:
        return _OPS[type(node.op)](_eval_node(node.operand))
    raise ValueError("only arithmetic expressions are allowed")


def calc(expression: str) -> str:
    try:
        return str(_eval_node(ast.parse(expression, mode="eval")))
    except (ValueError, SyntaxError, ZeroDivisionError) as e:
        return f"error: {e}"


class Notes:
    def __init__(self):
        self._data = {}

    def run(self, command: str) -> str:
        """Commands: 'set key value...' | 'get key' | 'list'"""
        parts = command.strip().split(None, 2)
        if not parts:
            return "error: empty command"
        if parts[0] == "set" and len(parts) == 3:
            self._data[parts[1]] = parts[2]
            return f"stored {parts[1]}"
        if parts[0] == "get" and len(parts) == 2:
            return self._data.get(parts[1], "not found")
        if parts[0] == "list":
            return ", ".join(sorted(self._data)) or "empty"
        return "error: unknown notes command"


def clock(_: str = "") -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")


class FixtureFetch:
    """Reads pages from a fixture directory. Unknown paths return 404 text."""

    def __init__(self, fixture_dir: str):
        self.fixture_dir = fixture_dir

    def run(self, path: str) -> str:
        safe = re.sub(r"[^A-Za-z0-9_.-]", "", path)
        full = os.path.join(self.fixture_dir, safe)
        if not os.path.isfile(full):
            return f"404: no fixture page {safe}"
        with open(full, "r", encoding="utf-8") as f:
            return f.read()
