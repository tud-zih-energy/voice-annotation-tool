from PySide6.QtCore import Slot, Signal
from PySide6.QtGui import QKeySequence
from PySide6.QtWidgets import (
    QDialog,
    QPushButton,
    QErrorMessage,
    QWidget,
)

from voice_annotation_tool.shortcut_widget import ShortcutWidget
from voice_annotation_tool.shortcut_settings_dialog_ui import Ui_ShortcutSettingsDialog


class ShortcutSettingsDialog(QDialog, Ui_ShortcutSettingsDialog):
    """Dialog used to configure the shortcuts of the buttons."""

    shortcuts_confirmed = Signal(object)
    "Emitted when the dialog is closed by pressing ok."

    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.shortcut_widgets: list[ShortcutWidget] = []
        self.existing: list[str] = []

    def load_existing(self, widget: QWidget):
        """Loads the shortcuts used by the given widget into a list.

        This is used to determine if a shortcut is already used or not.
        """
        for action in widget.actions():
            self.existing.append(action.shortcut().toString())

    def load_buttons(self, buttons: list[QPushButton]):
        """Generates widgets which can be used to edit the shortcuts."""
        for button in buttons:
            if not isinstance(button, QPushButton):
                continue
            shortcut = button.shortcut().toString()
            shortcut_widget = ShortcutWidget(
                button.toolTip().replace(shortcut, ""), button.shortcut()
            )
            self.shortcut_widgets.append(shortcut_widget)
            self.settings.addWidget(shortcut_widget)

    @Slot()
    def accept(self):
        shortcuts: list[QKeySequence] = []
        for widget in self.shortcut_widgets:
            shortcut = widget.get_shortcut()
            shortcuts.append(shortcut)
            if not shortcut.isEmpty() and shortcut in self.existing:
                error = QErrorMessage(self)
                message = self.tr(
                    "{shortcut} is already used elsewhere in the application."
                )
                return error.showMessage(message.format(shortcut=shortcut))
        self.shortcuts_confirmed.emit(shortcuts)
        super().accept()
