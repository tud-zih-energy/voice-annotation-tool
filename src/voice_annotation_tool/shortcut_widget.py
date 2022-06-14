from PySide6.QtGui import QKeyEvent, QKeySequence, QMouseEvent
from PySide6.QtWidgets import QFrame
from PySide6.QtCore import Qt

from voice_annotation_tool.shortcut_widget_ui import Ui_ShortcutWidget

MODIFIERS = {
    Qt.ShiftModifier,
    Qt.ControlModifier,
    Qt.AltModifier,
    Qt.MetaModifier,
}

MODIFIER_KEYS = {
    Qt.Key_Shift,
    Qt.Key_Control,
    Qt.Key_Alt,
    Qt.Key_Meta,
}


class ShortcutWidget(QFrame, Ui_ShortcutWidget):
    """Widget used to record a shortcut."""

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

    def _update_button_text(self) -> None:
        self.pushButton.setText(self.shortcut.toString())

    def mousePressEvent(self, event: QMouseEvent) -> None:
        if event.button() == Qt.MouseButton.RightButton:
            self.shortcut = QKeySequence()
            self._update_button_text()

    def keyPressEvent(self, event: QKeyEvent) -> None:
        key = event.key()
        if key in MODIFIER_KEYS or key == Qt.Key_unknown:
            return
        for modifier in MODIFIERS:
            if event.modifiers() & modifier:
                key += modifier
        self.shortcut = QKeySequence(key)
        self._update_button_text()
