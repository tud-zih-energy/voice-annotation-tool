"""
Dialog showing information about the program.
"""

import pkg_resources
from PySide6.QtWidgets import QDialog
from PySide6.QtCore import Slot
from .about_ui import Ui_AboutDialog

class AboutDialog(QDialog, Ui_AboutDialog):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.descriptionLabel.setText(self.descriptionLabel.text().format(
            version=pkg_resources.get_distribution("voice-annotation-tool").version))

    @Slot()
    def accept(self):
        super().accept()
