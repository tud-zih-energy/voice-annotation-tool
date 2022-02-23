"""
The main widget.
Holds a project list on startup, and the project view when a project was
opened.
"""

from json.decoder import JSONDecodeError
import os, json
from pathlib import Path
from typing import List
from PySide6.QtWidgets import QMainWindow, QFileDialog, QMessageBox
from PySide6.QtCore import Slot
from .project import Project
from .create_project_dialog import CreateProjectDialog
from .opened_project_frame import OpenedProjectFrame
from .shortcut_settings_dialog import ShortcutSettingsDialog
from .choose_project_frame import ChooseProjectFrame
from .about_dialog import AboutDialog
from .main_ui import Ui_MainWindow


class MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

        self.create_project_dialog = CreateProjectDialog()
        self.shortcut_settings_dialog = ShortcutSettingsDialog()
        self.opened_project_frame = OpenedProjectFrame()
        self.choose_project_frame = ChooseProjectFrame()
        self.original_title = self.windowTitle()
        self.project: Project = Project()
        self.project_file: Path | None = None
        self.settings_file: Path
        self.recent_projects: List[str] = []
        self.shortcuts = []

        # Layout
        self.verticalLayout.addWidget(self.opened_project_frame)
        self.verticalLayout.addWidget(self.choose_project_frame)
        self.opened_project_frame.hide()

        # Connections
        self.create_project_dialog.project_created.connect(self.project_created)
        self.shortcut_settings_dialog.shortcuts_confirmed.connect(
            self.shortcuts_confirmed
        )
        self.choose_project_frame.project_opened.connect(self.recent_project_chosen)
        self.choose_project_frame.create_project_pressed.connect(self.new_project)
        self.actionNewProject.triggered.connect(self.new_project)
        self.actionOpen.triggered.connect(self.open)
        self.actionSaveProject.triggered.connect(self.save_project)
        self.actionSaveProjectAs.triggered.connect(self.save_project_as)
        self.actionDeleteProject.triggered.connect(self.delete_project)
        self.actionQuit.triggered.connect(self.quit)
        self.actionAbout.triggered.connect(self.about)
        self.actionImportJson.triggered.connect(self.importJson)
        self.actionExportJson.triggered.connect(self.exportJson)
        self.actionImportCSV.triggered.connect(self.importCSV)
        self.actionExportCSV.triggered.connect(self.exportCSV)
        self.actionDeleteSelected.triggered.connect(self.deleteSelected)
        self.actionConfigureShortcuts.triggered.connect(self.configure_shortcuts)

        self.project_actions = [
            self.actionImportCSV,
            self.actionImportJson,
            self.actionExportCSV,
            self.actionExportJson,
            self.actionSaveProject,
            self.actionSaveProjectAs,
            self.actionDeleteProject,
            self.actionDeleteSelected,
        ]

    def load_settings(self, settings_file: Path):
        """
        Loads the recently used projects into the `recent_projects` list and
        applies the shortcuts.
        """
        self.settings_file = settings_file
        if not settings_file.is_file():
            return
        with open(settings_file) as file:
            try:
                data = json.load(file)
            except JSONDecodeError as error:
                return QMessageBox.warning(
                    self,
                    self.tr("Warning"),
                    self.tr(
                        "Failed to parse the configuration file: {error}".format(
                            error=error.msg
                        )
                    ),
                )
            for recent in data["recent_projects"]:
                if os.path.exists(recent):
                    self.recent_projects.append(recent)
            self.choose_project_frame.load_recent_projects(self.recent_projects)

            self.shortcuts = data["shortcuts"]
            self.opened_project_frame.apply_shortcuts(self.shortcuts)
            self.shortcut_settings_dialog.load_buttons(
                self.opened_project_frame.get_playback_buttons()
            )
            self.shortcut_settings_dialog.load_existing(self.menuEdit)
            self.shortcut_settings_dialog.load_existing(self.menuFile)

    def save_settings(self):
        """
        Saves the `recent_projects` list and keyboard shortcuts to a json file
        """
        with open(self.settings_file, "w") as file:
            json.dump(
                {
                    "recent_projects": list(dict.fromkeys(self.recent_projects)),
                    "shortcuts": self.shortcuts,
                },
                file,
            )

    def load_project(self, project: Project):
        self.project = project
        self.opened_project_frame.show()
        self.choose_project_frame.hide()
        self.opened_project_frame.load_project(project)
        for action in self.project_actions:
            action.setEnabled(True)
        if not project.audio_folder.is_dir():
            result: int = QMessageBox.warning(
                self,
                self.tr("Warning"),
                self.tr("The audio folder doesn't exist. Choose another one?"),
                QMessageBox.StandardButton.Ok,
                QMessageBox.Cancel,
            )
            if result == QMessageBox.Ok:
                folder = QFileDialog.getExistingDirectory(
                    self, self.tr("Open Audio Folder")
                )
                if folder:
                    project.audio_folder = Path(folder)
                    self.load_project(project)
        print("opened done")

    @Slot()
    def project_created(self, project: Project):
        self.load_project(project)

    @Slot()
    def new_project(self):
        self.project_file = None
        self.create_project_dialog.exec()

    @Slot()
    def open(self):
        path, _ = QFileDialog.getOpenFileName(
            self, self.tr("Open Project"), "", self.tr("Project Files (*.json)")
        )
        if not path:
            return
        project: Project = Project()
        self.project_file = Path(path)
        with open(path) as file:
            project.load_json(file, self.project_file.parent)
        project.load_audio_files(self.project_file.joinpath(project.audio_folder))
        with open(project.tsv_file) as file:
            project.load_tsv_file(file)
        self.load_project(project)

    @Slot()
    def recent_project_chosen(self, project_path: str):
        self.project_file = Path(project_path)
        project: Project = Project()
        with open(project_path) as file:
            project.load_json(file, self.project_file.parent)
            with open(self.project_file.parent.joinpath(project.tsv_file)) as file:
                project.load_tsv_file(file)
            project.load_audio_files(self.project_file.parent.joinpath(project.audio_folder))
            self.load_project(project)

    @Slot()
    def save_project(self):
        if not self.project_file:
            return self.save_project_as()
        with open(self.project_file, "w") as file:
            self.project.save(file)
        with open(self.project.tsv_file, "w", newline="") as file:
            self.project.save_annotations(file)

    @Slot()
    def save_project_as(self):
        path, _ = QFileDialog.getSaveFileName(
            self, self.tr("Save Project"), "", self.tr("Project Files (*.json)")
        )
        if not path:
            return
        self.project_file = Path(path)
        self.load_project(self.project)
        self.save_project()

    @Slot()
    def delete_project(self):
        if (
            QMessageBox.warning(
                self,
                self.tr("Warning"),
                self.tr("Delete the TSV and project file?"),
                QMessageBox.StandardButton.Ok,
                QMessageBox.Cancel,
            )
            == QMessageBox.Cancel
        ):
            return
        self.project.delete_tsv()
        self.project_file = None
        self.setWindowTitle(self.original_title)
        self.opened_project_frame.hide()
        self.choose_project_frame.show()
        for action in self.project_actions:
            action.setEnabled(False)

    @Slot()
    def quit(self):
        exit()

    @Slot()
    def about(self):
        AboutDialog().exec()

    @Slot()
    def importCSV(self):
        path, _ = QFileDialog.getOpenFileName(
            self, self.tr("Import CSV"), "", self.tr("CSV Files (*.csv)")
        )
        if not path:
            return
        with open(path, newline="") as file:
            self.project.importCSV(file)

    @Slot()
    def exportCSV(self):
        path, _ = QFileDialog.getSaveFileName(
            self, self.tr("Export CSV"), "", self.tr("CSV Files (*.csv)")
        )
        if not path:
            return
        with open(path, "w", newline="") as file:
            self.project.exportCSV(file)

    @Slot()
    def importJson(self):
        path, _ = QFileDialog.getOpenFileName(
            self, self.tr("Import Json"), "", self.tr("Json Files (*.json)")
        )
        if not path:
            return
        with open(path) as file:
            self.project.importJson(file)

    @Slot()
    def exportJson(self):
        path, _ = QFileDialog.getSaveFileName(
            self, self.tr("Export Json"), "", self.tr("Json Files (*.json)")
        )
        if not path:
            return
        with open(path, "w") as file:
            self.project.exportJson(file)

    @Slot()
    def deleteSelected(self):
        result: int = QMessageBox.warning(
            self,
            self.tr("Warning"),
            self.tr("Really delete selected annotations and audio files?"),
            QMessageBox.StandardButton.Ok,
            QMessageBox.Cancel,
        )
        if result == QMessageBox.Ok:
            self.opened_project_frame.delete_selected()

    @Slot()
    def configure_shortcuts(self):
        self.shortcut_settings_dialog.exec()

    @Slot()
    def shortcuts_confirmed(self, shortcuts):
        self.shortcuts = shortcuts
        self.save_settings()
        self.opened_project_frame.apply_shortcuts(shortcuts)
