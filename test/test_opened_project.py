from pathlib import Path
from PySide6.QtWidgets import QPushButton
from PySide6.QtCore import Qt
import pytest
from voice_annotation_tool.opened_project_frame import (
    AnnotationListModel,
    OpenedProjectFrame,
)
from voice_annotation_tool.project import Project, Annotation

annotation_data = {
    "client_id": "id",
    "path": "",
    "sentence": "",
    "up_votes": 0,
    "down_votes": 0,
    "age": "twenties",
    "gender": "male",
    "accent": "accent",
    "modified": False,
}


@pytest.fixture
def project_frame(tmpdir):
    frame = OpenedProjectFrame()
    project = Project()
    for annotation_num in range(3):
        path: Path = Path(tmpdir) / Path("path_" + str(annotation_num))
        path.touch()
        annotation_data["path"] = str(path)
        annotation_data["sentence"] = f"Sentence {annotation_num}"
        project.add_annotation(Annotation(annotation_data))
    frame.load_project(project)
    return frame


def test_annotation_text_loaded(project_frame: OpenedProjectFrame):
    assert project_frame.annotationEdit.toPlainText() == "Sentence 0"


def test_next_annotation_text(project_frame: OpenedProjectFrame):
    project_frame.annotationList.setCurrentIndex(
        project_frame.annotationList.model().index(1, 0)
    )
    assert project_frame.annotationEdit.toPlainText() == "Sentence 1"


def test_annotation_list_has_rows(project_frame: OpenedProjectFrame):
    model: AnnotationListModel = project_frame.annotationList.model()
    assert model.rowCount() == 3


def test_annotation_list_shows_filename(project_frame: OpenedProjectFrame):
    model: AnnotationListModel = project_frame.annotationList.model()
    assert model.data(model.index(0, 0), Qt.DisplayRole) == "path_0"


def test_metadata_header_filled_on_open(project_frame):
    assert project_frame.accentEdit.text() == "accent"
    assert project_frame.clientIdEdit.text() == "id"
    assert project_frame.genderInput.currentText() == "Male"
    assert project_frame.ageInput.currentText() == "19 - 29"


def test_tooltips_have_shortcuts(project_frame: OpenedProjectFrame):
    play_button: QPushButton = project_frame.get_playback_buttons()[0]
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


def test_mark_unchanged(project_frame: OpenedProjectFrame):
    project_frame.mark_unchanged_pressed()
    project_frame.mark_unchanged_pressed()
    assert not project_frame.project.annotations[0].modified


def test_delete_removes_rows(project_frame: OpenedProjectFrame):
    model: AnnotationListModel = project_frame.annotationList.model()
    start = model.rowCount()
    selected = len(project_frame.get_selected_annotations())
    project_frame.delete_selected()
    assert model.rowCount() == start - selected


def test_delete_removes_files(project_frame: OpenedProjectFrame):
    selected: Annotation = project_frame.get_selected_annotations()[0]
    project_frame.delete_selected()
    assert not selected.path.exists()


def test_buttons_disabled_without_samples(project_frame: OpenedProjectFrame):
    project_frame.load_project(Project())
    assert not project_frame.ageInput.isEnabled()
    assert not project_frame.get_playback_buttons()[0].isEnabled()


def test_text_cleared_after_opening_project(project_frame: OpenedProjectFrame):
    project = Project()
    project.add_annotation(Annotation({"sentence": "text"}))
    project_frame.load_project(project)
    project_frame.load_project(Project())
    assert project_frame.annotationEdit.toPlainText() == ""
