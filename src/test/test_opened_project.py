from PySide6.QtWidgets import QPushButton
import pytest
from annotation_tool.opened_project_frame import AnnotationListModel, OpenedProjectFrame
from annotation_tool.project import Project, Annotation

annotation_data = {
    "client_id": "id",
    "path": "",
    "text": "",
    "up_votes": 0,
    "down_votes": 0,
    "age": "twenties",
    "gender": "male",
    "accent": "accent",
    "modified": False,
}

@pytest.fixture
def project_frame():
    frame = OpenedProjectFrame()
    project = Project("")
    project.annotations = [Annotation(annotation_data)] * 3
    frame.load_project(project)
    return frame

def test_annotation_list(project_frame):
    model : AnnotationListModel = project_frame.annotationList.model()
    assert model.rowCount() == 3

def test_metadata_header_filled_on_open(project_frame):
    assert project_frame.accentEdit.text() == "accent"
    assert project_frame.clientIdEdit.text() == "id"
    assert project_frame.genderInput.currentText() == "Male"
    assert project_frame.ageInput.currentText() == "19 - 29"

def test_tooltips_have_shortcuts(project_frame):
    play_button : QPushButton = project_frame.playPauseButton
    assert play_button.shortcut().toString() in play_button.toolTip()
