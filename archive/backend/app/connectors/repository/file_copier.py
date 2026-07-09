from __future__ import annotations

import shutil
from pathlib import Path


class RepositoryFileCopier:
    def copy(self, source_path: str | Path, destination_path: str | Path) -> None:
        shutil.copyfile(source_path, destination_path)
