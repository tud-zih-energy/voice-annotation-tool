"""
The main widget.
Holds a project list on startup, and the project view when a project was
opened.
"""

import os, json, traceback, csv
from PySide6.QtWidgets import QMainWindow, QFileDialog, QErrorMessage, QMessageBox
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
        self.project : Project
        self.settings_file = ""
        self.recent_projects = []
        self.shortcuts = []

        # Layout
        self.verticalLayout.addWidget(self.opened_project_frame)
        self.verticalLayout.addWidget(self.choose_project_frame)
        self.opened_project_frame.hide()

        # Connections
        self.create_project_dialog.project_created.connect(self.project_created)
        self.shortcut_settings_dialog.shortcuts_confirmed.connect(self.shortcuts_confirmed)
        self.choose_project_frame.project_opened.connect(self.project_opened)
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

    def load_settings(self, settings_file):
        """
        Loads the recently used projects into the `recent_projects` list and
        applies the shortcuts.
        """
        self.settings_file = settings_file
        if not os.path.exists(settings_file):
            return
        with open(settings_file) as file:
            data = json.load(file)
            for recent in data["recent_projects"]:
                if os.path.exists(recent):
                    self.recent_projects.append(recent)
            self.choose_project_frame.load_recent_projects(self.recent_projects)

            self.shortcuts = data["shortcuts"]
            self.opened_project_frame.apply_shortcuts(self.shortcuts)
            self.shortcut_settings_dialog.load_buttons(
                    self.opened_project_frame.playbackButtons)
            self.shortcut_settings_dialog.load_existing(self.menuEdit)
            self.shortcut_settings_dialog.load_existing(self.menuFile)

    def save_settings(self):
        """
        Saves the `recent_projects` list and keyboard shortcuts to a json file
        """
        with open(self.settings_file, "w") as file:
            json.dump({
                "recent_projects": list(dict.fromkeys(self.recent_projects)),
                "shortcuts": self.shortcuts,
            }, file)

    def excepthook(self, exc_type, exc_value, exc_tb):
        error_dialog = QErrorMessage(self)
        message = "\n".join(traceback.format_exception(exc_type,
                exc_value, exc_tb))
        print(message)
        error_dialog.showMessage(message, "exception")

    @Slot()
    def project_opened(self, project):
        self.recent_projects.append(project.project_file)
        self.save_settings()
        self.setWindowTitle(os.path.basename(project.project_file))
        self.project = project
        self.opened_project_frame.show()
        self.choose_project_frame.hide()
        self.opened_project_frame.load_project(project)
        for action in self.project_actions:
            action.setEnabled(True)
        if not os.path.exists(project.audio_folder):
            if QMessageBox.warning(self, self.tr("Warning"), self.tr(
                    "The audio folder doesn't exist. Choose another one?"),
                    QMessageBox.StandardButton.Ok,
                    QMessageBox.Cancel) == QMessageBox.Ok:
                folder = QFileDialog.getExistingDirectory(self,
                        self.tr("Open Audio Folder"))
                if folder:
                    project.audio_folder = folder
                    self.project_opened(project)
        print("opened done")

    @Slot()
    def project_created(self, project):
        self.project_opened(project)

    @Slot()
    def new_project(self):
        self.create_project_dialog.exec()

    @Slot()
    def open(self):
        file, _ = QFileDialog.getOpenFileName(self, self.tr("Open Project"), "",
                self.tr("Project Files (*.json)"))
        if file:
            self.project_opened(Project(file))

    @Slot()
    def save_project(self):
        if not self.project.project_file:
            return self.save_project_as()
        self.project.save()

    @Slot()
    def save_project_as(self):
        file, _ = QFileDialog.getSaveFileName(self,
                self.tr("Save Project"), "", self.tr("Project Files (*.json)"))
        if file:
            self.project.project_file = file
            self.project.save()
            self.project_opened(self.project)

    @Slot()
    def delete_project(self):
        if QMessageBox.warning(self, self.tr("Warning"), self.tr(
                "Delete the TSV and project file?"),
                QMessageBox.StandardButton.Ok,
                QMessageBox.Cancel) == QMessageBox.Cancel:
            return
        self.project.delete()
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
        path, _ = QFileDialog.getOpenFileName(self, self.tr("Import CSV"), "",
                self.tr("CSV Files (*.csv)"))
        if not path:
            return
        with open(path, newline='') as file:
            self.project.importCSV(file)

    @Slot()
    def exportCSV(self):
        path, _ = QFileDialog.getSaveFileName(self, self.tr("Export CSV"), "",
                self.tr("CSV Files (*.csv)"))
        if not path:
            return
        with open(path, "w", newline='') as file:
            self.project.exportCSV(file)

    @Slot()
    def importJson(self):
        path, _ = QFileDialog.getOpenFileName(self, self.tr("Import Json"), "",
                self.tr("Json Files (*.json)"))
        if not path:
            return
        with open(path) as file:
            self.project.importJson(file)

    @Slot()
    def exportJson(self):
        path, _ = QFileDialog.getSaveFileName(self, self.tr("Export Json"), "",
                self.tr("Json Files (*.json)"))
        if not path:
            return
        with open(path, "w") as file:
            self.project.exportJson(file)

    @Slot()
    def deleteSelected(self):
        if QMessageBox.warning(self, self.tr("Warning"), self.tr(
                "Really delete selected annotations and audio files?"),
                QMessageBox.StandardButton.Ok,
                QMessageBox.Cancel) == QMessageBox.Ok:
            self.opened_project_frame.delete_selected()

    @Slot()
    def configure_shortcuts(self):
        self.shortcut_settings_dialog.exec()

    @Slot()
    def shortcuts_confirmed(self, shortcuts):
        self.shortcuts = shortcuts
        self.save_settings()
        self.opened_project_frame.apply_shortcuts(shortcuts)
