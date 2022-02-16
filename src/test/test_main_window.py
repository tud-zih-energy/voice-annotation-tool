from PySide6.QtWidgets import QApplication
from voice_annotation_tool.about_dialog import AboutDialog
from voice_annotation_tool.main_window import MainWindow

def test_about_dialog():
    window = MainWindow()
    window.about()
    assert True
