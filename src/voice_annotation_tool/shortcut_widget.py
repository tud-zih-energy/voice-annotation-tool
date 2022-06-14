from PySide6.QtWidgets import QFrame

from voice_annotation_tool.shortcut_widget_ui import Ui_ShortcutWidget


class ShortcutWidget(QFrame, Ui_ShortcutWidget):
    def __init__(self, name: str):
        super().__init__()
        self.setupUi(self)
        self.name = name
        "The description of the shortcut."

    def get_shortcut(self) -> str:
        return ""
