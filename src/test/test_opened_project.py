from PySide6.QtWidgets import QPushButton
import pytest
from voice_annotation_tool.opened_project_frame import AnnotationListModel, OpenedProjectFrame
from voice_annotation_tool.project import Project, Annotation

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

def test_next_button_selects_one(project_frame: OpenedProjectFrame):
    project_frame.next_pressed()
    assert len(project_frame.annotationList.selectedIndexes()) == 1

def test_next_button_selects_correct_annotation(project_frame: OpenedProjectFrame):
    project_frame.next_pressed()
    assert project_frame.annotationList.selectedIndexes()[0].row() == 1

def test_previous_button_selects_one(project_frame: OpenedProjectFrame):
    project_frame.next_pressed()
    project_frame.previous_pressed()
    assert len(project_frame.annotationList.selectedIndexes()) == 1

def test_previous_button_selects_correct_annotation(project_frame: OpenedProjectFrame):
    project_frame.next_pressed()
    project_frame.previous_pressed()
    assert project_frame.annotationList.selectedIndexes()[0].row() == 0
