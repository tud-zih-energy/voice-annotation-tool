"""
Shown on startup, a list of recent projects.

Has two buttons to open and create projects.
"""

from PySide6.QtWidgets import QFrame, QListWidgetItem, QFileDialog
from PySide6.QtCore import Signal, Slot, QModelIndex
from .project import Project
from .choose_project_frame_ui import Ui_ChooseProjectFrame


class ChooseProjectFrame(QFrame, Ui_ChooseProjectFrame):
    create_project_pressed = Signal()
    project_opened = Signal(Project)

    def __init__(self):
        super().__init__()
        self.setupUi(self)

    def load_recent_projects(self, projects):
        for project in projects:
            item = QListWidgetItem(project)
            item.setData(0, project)
            self.recentProjectsList.addItem(item)

    @Slot()
    def open_project(self):
        files = QFileDialog.getOpenFileName(
            self, "Open Project", "", "Project Files (*.json)"
        )
        if not files[0]:
            return
        self.project_opened.emit(Project(files[0]))

    @Slot()
    def create_project(self):
        self.create_project_pressed.emit()

    @Slot(QModelIndex)
    def select_recent_project(self, index):
        self.project_opened.emit(Project(index.data()))
