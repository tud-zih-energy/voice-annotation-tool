import pkg_resources
from PySide6.QtWidgets import QDialog
from PySide6.QtCore import Slot
from .about_ui import Ui_AboutDialog


class AboutDialog(QDialog, Ui_AboutDialog):
    """Dialog showing information about the program."""

    def __init__(self):
        super().__init__()
        self.setupUi(self)
        version = pkg_resources.get_distribution("voice-annotation-tool").version
        text = self.descriptionLabel.text().format(version=version)
        self.descriptionLabel.setText(text)

    @Slot()
    def accept(self):
        super().accept()
