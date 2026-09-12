import tempfile
from pathlib import Path


class TemporaryDatabase:
    def __init__(self) -> None:
        self._directory = tempfile.TemporaryDirectory()
        self.path = str(Path(self._directory.name) / "test.sqlite")

    def cleanup(self) -> None:
        self._directory.cleanup()
