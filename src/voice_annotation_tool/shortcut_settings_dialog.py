from typing import List
from PySide6.QtCore import Slot, Signal
from PySide6.QtWidgets import (
    QDialog,
    QHBoxLayout,
    QLineEdit,
    QLabel,
    QSizePolicy,
    QPushButton,
    QErrorMessage,
    QWidget,
)
from .shortcut_settings_dialog_ui import Ui_ShortcutSettingsDialog


class ShortcutSettingsDialog(QDialog, Ui_ShortcutSettingsDialog):
    """Dialog used to configure the shortcuts of the buttons."""

    shortcuts_confirmed = Signal(object)
    "Emitted when the dialog is closed by pressing ok."

    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.shortcut_edits: List[QLineEdit] = []
        self.existing: List[str] = []

    def load_existing(self, widget: QWidget):
        """Loads the shortcuts used by the given widget into a list.

        This is used to determine if a shortcut is already used or not.
        """
        for action in widget.actions():
            self.existing.append(action.shortcut().toString())

    def load_buttons(self, buttons: List[QPushButton]):
        """Generates widgets which can be used to edit the shortcuts."""
        for button in buttons:
            if not isinstance(button, QPushButton):
                continue
            shortcut = button.shortcut().toString()
            layout = QHBoxLayout()
            label = QLabel(self)
            label.setText(button.toolTip().replace(shortcut, ""))
            label.setSizePolicy(
                QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred
            )
            line_edit = QLineEdit(self)
            line_edit.setText(shortcut)
            line_edit.setSizePolicy(
                QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred
            )
            layout.addWidget(label)
            layout.addWidget(line_edit)
            self.shortcut_edits.append(line_edit)
            self.settings.addLayout(layout)

    @Slot()
    def accept(self):
        shortcuts: List[str] = []
        for edit in self.findChildren(QLineEdit):
            shortcuts.append(edit.text())
        for shortcut in shortcuts:
            if shortcut in self.existing:
                error = QErrorMessage(self)
                message = self.tr(
                    "{shortcut} is already used elsewhere in the application."
                )
                error.showMessage(message.format(shortcut=shortcut))
                return
        self.shortcuts_confirmed.emit(shortcuts)
        super().accept()
