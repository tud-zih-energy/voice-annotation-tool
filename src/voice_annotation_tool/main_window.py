from json.decoder import JSONDecodeError
import json
from pathlib import Path
from typing import Any, TextIO
from PySide6.QtGui import QDesktopServices
from PySide6.QtWidgets import QMainWindow, QFileDialog, QMessageBox
from PySide6.QtCore import Signal, Slot

from voice_annotation_tool.project_settings_dialog import ProjectSettingsDialog
from voice_annotation_tool.project import Project
from voice_annotation_tool.opened_project_frame import OpenedProjectFrame
from voice_annotation_tool.shortcut_settings_dialog import ShortcutSettingsDialog
from voice_annotation_tool.choose_project_frame import ChooseProjectFrame
from voice_annotation_tool.about_dialog import AboutDialog
from voice_annotation_tool.main_ui import Ui_MainWindow


class MainWindow(QMainWindow, Ui_MainWindow):
    """The main widget.

    Holds a list of recent projects on startup, and the project view
    when a project was opened. Handles loading and saving the settings.
    """

    settings_changed = Signal()

    def __init__(self):
        super().__init__()
        self.setupUi(self)

        self.project_settings_dialog = ProjectSettingsDialog()
        self.project_settings_dialog.settings_confirmed.connect(self.settings_confirmed)
        self.opened_project_frame = OpenedProjectFrame()
        self.choose_project_frame = ChooseProjectFrame()

        self.original_title = self.windowTitle()
        "The window title before it was changed to the project name."

        self.project: Project = Project()
        """The currently loaded project.

        Even if the user didn't open a project, an empty unsaved project
        is loaded.
        """

        self.project_file: Path | None = None
        """The path the current project was saved to.

        None if the project was never saved."""

        self.last_saved_hash: int = 0
        """The hash of the project when it was last saved.

        Zero if no project is loaded."""

        self.recent_projects: list[Path] = []
        """List of recently opened projects.

        This list should only contain existing paths.
        """

        # Layout
        self.verticalLayout.addWidget(self.opened_project_frame)
        self.verticalLayout.addWidget(self.choose_project_frame)
        self.opened_project_frame.hide()

        # Connections
        self.choose_project_frame.project_opened.connect(self.recent_project_chosen)
        self.choose_project_frame.create_project_pressed.connect(self.new_project)
        self.actionNewProject.triggered.connect(self.new_project)
        self.actionOpen.triggered.connect(self.open)
        self.actionSaveProject.triggered.connect(self.save_project)
        self.actionSaveProjectAs.triggered.connect(self.save_project_as)
        self.actionDeleteProject.triggered.connect(self.delete_project)
        self.actionQuit.triggered.connect(self.quit)
        self.actionAbout.triggered.connect(self.about)
        self.actionProjectSettings.triggered.connect(self.show_project_settings)
        self.actionImportJson.triggered.connect(self.importJson)
        self.actionExportJson.triggered.connect(self.exportJson)
        self.actionImportCSV.triggered.connect(self.importCSV)
        self.actionExportCSV.triggered.connect(self.exportCSV)
        self.actionDeleteSelected.triggered.connect(self.deleteSelected)
        self.actionConfigureShortcuts.triggered.connect(self.configure_shortcuts)
        self.actionDocumentation.triggered.connect(self.open_documentation)

        self.project_actions = [
            self.actionImportCSV,
            self.actionImportJson,
            self.actionExportCSV,
            self.actionExportJson,
            self.actionSaveProject,
            self.actionSaveProjectAs,
            self.actionDeleteProject,
            self.actionDeleteSelected,
            self.actionProjectSettings,
        ]
        "Actions that can only be used with a project open."

    def load_settings(self, file: TextIO):
        """Loads the recently used projects into the `recent_projects` list
        and applies the shortcuts.
        """
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
        for recent in data.get("recent_projects", []):
            path = Path(recent)
            if path.is_file():
                self.recent_projects.append(path)
        self.choose_project_frame.load_recent_projects(self.recent_projects)

        self.opened_project_frame.apply_shortcuts(data.get("shortcuts", []))

    def save_settings(self, to: TextIO):
        """
        Saves the `recent_projects` list and keyboard shortcuts to a json file.
        """
        data: dict[str, str | list[str]] = {
            "recent_projects": list(map(str, self.recent_projects)),
            "shortcuts": self.opened_project_frame.get_shortcuts(),
        }
        json.dump(data, to)

    def set_current_project(self, project: Project):
        """Sets the current project and loads it into the GUI."""
        self.project = project
        self.last_saved_hash = hash(project)
        if self.project_file:
            self.setWindowTitle(self.project_file.name)
        else:
            self.setWindowTitle(self.tr("Unsaved Project"))
        if self.project_file and (not self.project_file in self.recent_projects):
            self.recent_projects.append(self.project_file)
            self.settings_changed.emit()
        self.opened_project_frame.show()
        self.choose_project_frame.hide()
        self.opened_project_frame.load_project(project)
        for action in self.project_actions:
            action.setEnabled(True)
        if (
            not self.project.tsv_file
            or not self.project.audio_folder
            or not self.project.audio_folder.is_dir()
        ):
            result: int = QMessageBox.warning(
                self,
                self.tr("Warning"),
                self.tr(
                    "The audio folder or tsv file doesn't exist. Open project settings?"
                ),
                QMessageBox.StandardButton.Ok,
                QMessageBox.Cancel,
            )
            if result == QMessageBox.Ok:
                self.show_project_settings()
        elif len(self.project.annotations) == 0:
            message = QMessageBox()
            message.setText(
                self.tr("No samples found in the audio folder: {folder}").format(
                    folder=project.audio_folder
                )
            )
            message.exec()
        print("opened done")

    def load_project_from_file(self, path: Path):
        self.project_file = path
        self.project = Project()
        with open(path) as file:
            if not self.project.load_json(file, self.project_file.parent):
                message = QMessageBox()
                message.setIcon(QMessageBox.Critical)
                message.setWindowTitle(self.tr("Error"))
                message.setText(self.tr("Invalid project."))
                return message.exec()
            if self.project.tsv_file and self.project.tsv_file.is_file():
                with open(self.project.tsv_file, newline="") as file:
                    self.project.load_tsv_file(file)
            else:
                message = QMessageBox()
                message.setText(
                    self.tr(
                        "The TSV file doesn't exist. Please change it in the project settings"
                    )
                )
                message.setWindowTitle(self.tr("Warning"))
                message.setIcon(QMessageBox.Warning)
                message.exec()
            if self.project.audio_folder:
                self.project.load_audio_files(self.project.audio_folder)
            else:
                message = QMessageBox()
                message.setText(
                    self.tr(
                        "The audio folder doesn't exist. Please change it in the project settings"
                    )
                )
                message.setWindowTitle(self.tr("Warning"))
                message.setIcon(QMessageBox.Warning)
                message.exec()
        self.set_current_project(self.project)
        print("loaded audio folder")

    def save_current_project(self):
        """Saves the annotations and project file of the current project."""
        if not self.project_file:
            return self.save_project_as()
        self.last_saved_hash = hash(self.project)
        with open(self.project_file, "w") as file:
            self.project.save(file, self.project_file.parent)
        if self.project.tsv_file and self.project.tsv_file.parent.is_dir():
            with open(self.project.tsv_file, "w", newline="") as file:
                self.project.save_annotations(file)
        else:
            message = QMessageBox()
            message.setText(
                self.tr(
                    "The TSV file path is invalid. Please change it in the project settings"
                )
            )
            message.setWindowTitle(self.tr("Warning"))
            message.setIcon(QMessageBox.Warning)
            message.exec()

    @Slot()
    def new_project(self):
        self.project_file = None
        self.set_current_project(Project())

    @Slot()
    def open(self):
        result: tuple[str, Any] = QFileDialog.getOpenFileName(
            self, self.tr("Open Project"), "", self.tr("Project Files (*.json)")
        )
        file = result[0]
        if file:
            self.load_project_from_file(Path(file))

    @Slot()
    def recent_project_chosen(self, path: Path):
        self.load_project_from_file(path)

    @Slot()
    def save_project(self):
        self.save_current_project()

    @Slot()
    def save_project_as(self):
        file, _ = QFileDialog.getSaveFileName(
            self, self.tr("Save Project"), "", self.tr("Project Files (*.json)")
        )
        if file:
            self.project_file = Path(file)
            self.set_current_project(self.project)
            self.save_current_project()

    @Slot()
    def delete_project(self):
        result: int = QMessageBox.warning(
            self,
            self.tr("Warning"),
            self.tr("Delete the TSV and project file?"),
            QMessageBox.Ok,
            QMessageBox.Cancel,
        )
        if result != QMessageBox.Ok:
            return
        self.last_saved_hash = 0
        self.project.delete_tsv()
        if self.project_file:
            self.project_file.unlink()
        self.project_file = None
        self.setWindowTitle(self.original_title)
        self.opened_project_frame.hide()
        self.choose_project_frame.show()
        for action in self.project_actions:
            action.setEnabled(False)

    @Slot()
    def quit(self):
        if self.last_saved_hash and hash(self.project) != self.last_saved_hash:
            message = QMessageBox(self)
            message.setWindowTitle(self.tr("Warning"))
            message.setIcon(QMessageBox.Warning)
            message.setText(self.tr("You have unsaved changes."))
            message.setStandardButtons(
                QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel
            )
            result = message.exec()
            if result == QMessageBox.Save:
                self.save_current_project()
                if not self.project_file:
                    return
            elif result == QMessageBox.Cancel:
                return
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
    def show_project_settings(self):
        self.project_settings_dialog.load_project(self.project)
        self.project_settings_dialog.exec()

    @Slot(dict)
    def settings_confirmed(self, settings: dict[str, Path]):
        self.project.tsv_file = settings["tsv"]
        self.project.audio_folder = settings["audio"]
        if self.project.tsv_file.is_file():
            with open(self.project.tsv_file, newline="") as file:
                self.project.load_tsv_file(file)
        self.project.load_audio_files(self.project.audio_folder)
        self.opened_project_frame.load_project(self.project)

    @Slot()
    def configure_shortcuts(self):
        shortcut_settings_dialog = ShortcutSettingsDialog()
        shortcut_settings_dialog.load_buttons(
            self.opened_project_frame.get_playback_buttons()
        )
        shortcut_settings_dialog.load_existing(self.menuEdit)
        shortcut_settings_dialog.load_existing(self.menuFile)
        shortcut_settings_dialog.shortcuts_confirmed.connect(
            self.shortcuts_confirmed
        )
        shortcut_settings_dialog.exec()

    @Slot()
    def shortcuts_confirmed(self, shortcuts):
        self.settings_changed.emit()
        self.opened_project_frame.apply_shortcuts(shortcuts)

    @Slot()
    def open_documentation(self):
        QDesktopServices.openUrl(
            self.tr("https://voice-annotation-tool.readthedocs.io/en/latest/")
        )
