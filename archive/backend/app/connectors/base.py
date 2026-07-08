from abc import ABC, abstractmethod


class BaseConnector(ABC):
    @abstractmethod
    def discover(self):
        """Return discoverable items."""
        raise NotImplementedError

    @abstractmethod
    def ingest(self):
        """Ingest discovered items into Archive."""
        raise NotImplementedError
