from PySide6.QtWidgets import QApplication
from annotation_tool.opened_project_frame import OpenedProjectFrame
from annotation_tool.project import Project, Annotation

def test_annotation_list():
    try: QApplication()
    except: pass
    frame = OpenedProjectFrame()
    project = Project("")
    data = {
        "client_id": "0",
        "file": "",
        "text": "",
        "up_votes": 0,
        "down_votes": 0,
        "age": "",
        "gender": "",
        "accent": "",
        "modified": False,
    }
    project.annotations = [Annotation(data)] * 3
    frame.load_project(project)
    assert frame.fileList.count() == 3
