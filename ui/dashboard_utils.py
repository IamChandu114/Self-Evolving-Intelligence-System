from __future__ import annotations

import ast
import re
from datetime import datetime
from pathlib import Path

import pandas as pd


def parse_input_signal(raw_text: str) -> list[int]:
    tokens = re.split(r"[,\s]+", raw_text.strip())
    values = [int(token) for token in tokens if token]
    return values


def format_timestamp(value) -> str:
    if not value:
        return "-"
    if isinstance(value, str):
        return value
    if isinstance(value, datetime):
        return value.strftime("%H:%M:%S")
    return str(value)


def experiences_to_frame(experiences) -> pd.DataFrame:
    if not experiences:
        return pd.DataFrame(
            columns=[
                "timestamp",
                "input",
                "decision",
                "reward",
                "confidence",
                "strategy_weight",
            ]
        )
    return pd.DataFrame(experiences)


def safe_mean(values):
    values = list(values)
    return sum(values) / len(values) if values else 0.0


def clamp(value, lower, upper):
    return max(lower, min(upper, value))


def count_python_symbols(root_path: Path):
    files = []
    classes = 0
    functions = 0

    for path in root_path.rglob("*.py"):
        if "__pycache__" in path.parts:
            continue
        files.append(path)
        try:
            tree = ast.parse(path.read_text(encoding="utf-8"))
        except Exception:
            continue
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                classes += 1
            elif isinstance(node, ast.FunctionDef):
                functions += 1

    return {
        "python_files": len(files),
        "classes": classes,
        "functions": functions,
    }


def build_repository_statistics(root_path: Path):
    symbol_counts = count_python_symbols(root_path)
    tracked_dirs = ["core", "memory", "evolution", "ui", "api"]
    module_dirs = [root_path / name for name in tracked_dirs if (root_path / name).exists()]
    version = None
    server_file = root_path / "api" / "server.py"
    runtime_file = root_path / "runtime.txt"

    if server_file.exists():
        match = re.search(r'version\s*=\s*["\']([^"\']+)["\']', server_file.read_text(encoding="utf-8"))
        if match:
            version = match.group(1)

    runtime_python = runtime_file.read_text(encoding="utf-8").strip() if runtime_file.exists() else None

    return {
        "project_root": str(root_path),
        "project_modules": len(module_dirs),
        "python_files": symbol_counts["python_files"],
        "classes": symbol_counts["classes"],
        "functions": symbol_counts["functions"],
        "directories": len([p for p in root_path.iterdir() if p.is_dir() and p.name != "__pycache__"]),
        "project_version": version,
        "runtime_python": runtime_python,
    }
