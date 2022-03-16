from pathlib import Path
from typing import Any, List, Tuple
from PySide6.QtWidgets import QFrame, QListWidgetItem, QFileDialog
from PySide6.QtCore import Signal, Slot, QModelIndex
from .choose_project_frame_ui import Ui_ChooseProjectFrame


class ChooseProjectFrame(QFrame, Ui_ChooseProjectFrame):
    """Shown on startup, a list of recent projects.

    Has two buttons to open and create projects.
    """

    create_project_pressed = Signal()
    "Emitted when the create project button is pressed."
    project_opened = Signal(Path)
    "Emitted when a recent project was selected."

    def __init__(self):
        super().__init__()
        self.setupUi(self)

    def load_recent_projects(self, paths: List[Path]):
        """Loads the given paths into the list of recent projects."""
        for path in paths:
            item = QListWidgetItem(str(path))
            self.recentProjectsList.addItem(item)

    @Slot()
    def open_project(self):
        files: Tuple[str, Any] = QFileDialog.getOpenFileName(
            self, "Open Project", "", "Project Files (*.json)"
        )
        if not files[0]:
            return
        self.project_opened.emit(Path(files[0]))

    @Slot()
    def create_project(self):
        self.create_project_pressed.emit()

    @Slot(QModelIndex)
    def select_recent_project(self, index):
        self.project_opened.emit(Path(index.data()))
