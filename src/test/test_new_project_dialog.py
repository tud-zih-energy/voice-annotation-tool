from PySide6.QtWidgets import QApplication
from annotation_tool.create_project_dialog import CreateProjectDialog

def test_create_dialog():
    try: QApplication()
    except: pass
    assert CreateProjectDialog()
