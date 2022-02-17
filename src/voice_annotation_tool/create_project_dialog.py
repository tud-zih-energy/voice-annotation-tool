"""
Dialog with options to set up a new project.

Asks the user for the audio folder and optionally a tsv file with annotations.
"""

import os
from pathlib import Path
from PySide6.QtWidgets import QDialog, QFileDialog, QDialogButtonBox
from PySide6.QtCore import Signal, Slot
from .project import Project
from .create_project_dialog_ui import Ui_CreateProjectDialog

class CreateProjectDialog(QDialog, Ui_CreateProjectDialog):
    project_created = Signal(Project)

    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.tsv_file = ""
        self.project_file = ""
        self.audio_folder = ""
        self.current_folder = ""
        self.update_buttons()

    def update_buttons(self):
        """Enable the OK button when all paths are specified."""
        self.buttonBox.button(QDialogButtonBox.Ok).setEnabled(
                bool(self.tsv_file) and bool(self.tsv_file)
                and bool(self.project_file))

    def accept(self):
        project = Project(self.project_file)
        project.set_audio_folder(self.audio_folder)
        project.set_tsv_file(self.tsv_file)
        self.project_created.emit(project)
        super().accept()

    @Slot()
    def audio_files_button_clicked(self):
        folder = QFileDialog.getExistingDirectory(self, "Open Audio Folder")
        if not folder:
            return
        self.audio_folder = folder
        self.current_folder = str(Path(folder).parent.absolute())
        self.audioPathEdit.setText(folder)
        self.update_buttons()

    @Slot()
    def tsv_file_button_clicked(self):
        file, _ = QFileDialog.getSaveFileName(self, "Select TSV File Location",
                self.current_folder, "TSV/CSV Files (*.tsv);;CSV Files (*.csv)",
                options=QFileDialog.DontConfirmOverwrite)
        if not file:
            return
        self.tsvPathEdit.setText(file)

    @Slot()
    def open_project_file(self):
        file, _ = QFileDialog.getSaveFileName(self,
                "Select Location of Project File", self.current_folder,
                "Json Files (*)")
        if not file:
            return
        if os.path.exists(file):
            os.remove(file)
        self.projectPathEdit.setText(file)

    @Slot(str)
    def project_path_changed(self, path : str):
        self.project_file = path
        self.update_buttons()

    @Slot(str)
    def audio_path_changed(self, path : str):
        self.audio_folder = path
        self.update_buttons()

    @Slot(str)
    def tsv_path_changed(self, path : str):
        self.tsv_file = path
        self.update_buttons()

