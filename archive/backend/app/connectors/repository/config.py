from __future__ import annotations

import os
from pathlib import Path


REPOSITORY_ALLOWED_ROOTS_ENV = "MIDWEST24_REPOSITORY_ALLOWED_ROOTS"


def get_repository_allowed_roots() -> list[Path]:
    raw_value = os.getenv(REPOSITORY_ALLOWED_ROOTS_ENV, "")

    return [
        Path(item.strip()).expanduser().resolve()
        for item in raw_value.split(":")
        if item.strip()
    ]
