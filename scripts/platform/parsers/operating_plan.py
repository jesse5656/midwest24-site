#!/usr/bin/env python3
from __future__ import annotations

import re
from pathlib import Path
from typing import Any

OBJECTIVE_SECTION_NAMES = {"current objective", "highest-priority objective"}
HEADING = re.compile(r"^#{1,6}\s+(.+?)\s*$")
FIELD = re.compile(r"^([A-Za-z][A-Za-z0-9 /&()\-]+):\s*(.*)$")

FIELD_MAP = {
    "type": "type",
    "name": "name",
    "status": "status",
    "objective": "objective",
    "scope": "scope",
    "success criteria": "success_criteria",
    "active sprint": "active_sprint",
    "current sprint": "active_sprint",
    "next concrete step": "next_concrete_step",
}


def _clean_value(lines: list[str]) -> str | None:
    values = [
        re.sub(r"^[-*+]\s+", "", line.strip()).strip()
        for line in lines
        if line.strip()
    ]
    values = [value for value in values if value]
    return "\n".join(values) if values else None


def _parse_fields(
    lines: list[str],
    mapping: dict[str, str],
) -> dict[str, str | None]:
    result: dict[str, str | None] = {}
    current_key: str | None = None
    buffer: list[str] = []

    def flush() -> None:
        nonlocal current_key, buffer
        if current_key is not None:
            value = _clean_value(buffer)
            if value is not None:
                result[current_key] = value
        current_key = None
        buffer = []

    for raw in lines:
        stripped = raw.strip()

        if re.fullmatch(r"-{3,}", stripped):
            flush()
            break

        if HEADING.match(stripped):
            flush()
            break

        field = FIELD.match(stripped)
        if field:
            mapped = mapping.get(field.group(1).strip().lower())
            if mapped is not None:
                flush()
                current_key = mapped
                inline_value = field.group(2).strip()
                if inline_value:
                    buffer.append(inline_value)
                continue

        if current_key is not None:
            buffer.append(raw)

    flush()
    return result


def _find_authoritative_objective_block(text: str) -> list[str]:
    lines = text.splitlines()
    start: int | None = None

    for index, raw in enumerate(lines):
        heading = HEADING.match(raw.strip())
        if heading and heading.group(1).strip().lower() in OBJECTIVE_SECTION_NAMES:
            start = index + 1
            break

    if start is None:
        return []

    block: list[str] = []
    for raw in lines[start:]:
        stripped = raw.strip()
        if re.fullmatch(r"-{3,}", stripped) or HEADING.match(stripped):
            break
        block.append(raw)

    return block


def parse_operating_plan(path: Path) -> dict[str, Any]:
    text = path.read_text(encoding="utf-8", errors="replace")
    result: dict[str, Any] = {
        "type": None,
        "name": None,
        "status": None,
        "objective": None,
        "scope": None,
        "success_criteria": None,
        "active_sprint": None,
        "next_concrete_step": None,
    }
    result.update(
        _parse_fields(
            _find_authoritative_objective_block(text),
            FIELD_MAP,
        )
    )
    return result
