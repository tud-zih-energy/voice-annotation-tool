from PySide6.QtGui import QKeyEvent, QKeySequence
from PySide6.QtWidgets import QFrame
from PySide6.QtCore import Qt

from voice_annotation_tool.shortcut_widget_ui import Ui_ShortcutWidget


class ShortcutWidget(QFrame, Ui_ShortcutWidget):
    def __init__(self, name: str, shortcut: QKeySequence):
        super().__init__()
        self.setupUi(self)
        self.label.setText(name)
        self.name = name
        "The description of the shortcut."
        self.shortcut = shortcut
        "The last set shortcut."
        self._update_button_text()

    def get_shortcut(self) -> QKeySequence:
        """Returns the currently set shortcut."""
        return self.shortcut

    def _update_button_text(self):
        self.pushButton.setText(self.shortcut.toString())

    def keyPressEvent(self, event: QKeyEvent) -> None:
        key = event.key()
        for modifier in [
            Qt.ShiftModifier,
            Qt.ControlModifier,
            Qt.AltModifier,
            Qt.MetaModifier,
        ]:
            if event.modifiers() & modifier:
                key += modifier
        self.shortcut = QKeySequence(key)
        self._update_button_text()
