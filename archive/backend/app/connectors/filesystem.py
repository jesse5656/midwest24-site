from pathlib import Path

from app.connectors.base import BaseConnector


class FilesystemConnector(BaseConnector):
    def __init__(self, root: str):
        self.root = Path(root)

    def discover(self):
        return [p for p in self.root.rglob("*") if p.is_file()]

    def ingest(self):
        return self.discover()
