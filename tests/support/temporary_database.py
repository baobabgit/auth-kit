import tempfile
from pathlib import Path


class TemporaryDatabase:
    def __init__(self) -> None:
        # ignore_cleanup_errors : sous Windows le fichier SQLite reste
        # parfois verrouillé après fermeture du client HTTP (WinError 32).
        self._directory = tempfile.TemporaryDirectory(ignore_cleanup_errors=True)
        self.path = str(Path(self._directory.name) / "test.sqlite")

    def cleanup(self) -> None:
        self._directory.cleanup()
