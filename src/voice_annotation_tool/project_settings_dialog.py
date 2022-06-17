from pathlib import Path
from PySide6.QtCore import Signal, Slot
from PySide6.QtWidgets import QDialog, QFileDialog

from voice_annotation_tool.project import Project
from voice_annotation_tool.project_settings_dialog_ui import Ui_ProjectSettingsDialog


class ProjectSettingsDialog(QDialog, Ui_ProjectSettingsDialog):
    settings_confirmed = Signal(object)

    def __init__(self):
        super().__init__()
        self.setupUi(self)

    def load_project(self, project: Project):
        if project.audio_folder:
            self.audioPathEdit.setText(str(project.audio_folder))
        if project.tsv_file:
            self.tsvPathEdit.setText(str(project.tsv_file))

    def accept(self):
        audio: Path = Path(self.audioPathEdit.text())
        tsv: Path = Path(self.tsvPathEdit.text())
        if not audio.is_dir() or not tsv.parent.is_dir():
            # TODO: Show an error dialog.
            return
        self.settings_confirmed.emit(
            {
                "audio": audio,
                "tsv": tsv,
            }
        )
        super().accept()

    @Slot()
    def open_audio_folder_pressed(self):
        folder: str = QFileDialog.getExistingDirectory(self, "Open Audio Folder")
        if not folder:
            return
        self.audio_folder = Path(folder)
        self.audioPathEdit.setText(folder)

    @Slot()
    def select_tsv_file_pressed(self):
        file, _ = QFileDialog.getSaveFileName(
            self,
            "Select TSV File Location",
            "",
            "TSV/CSV Files (*.tsv);;CSV Files (*.csv)",
            options=QFileDialog.DontConfirmOverwrite,
        )
        if not file:
            return
        self.tsvPathEdit.setText(file)
