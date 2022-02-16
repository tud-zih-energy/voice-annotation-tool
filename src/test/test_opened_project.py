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

def test_annotation_list():
    frame = OpenedProjectFrame()
    project = Project("")
    project.annotations = [Annotation(annotation_data)] * 3
    frame.load_project(project)
    model : AnnotationListModel = frame.annotationList.model()
    assert model.rowCount() == 3

def test_metadata_header_filled_on_open():
    frame = OpenedProjectFrame()
    project = Project("")
    project.annotations = [Annotation(annotation_data)] * 3
    frame.load_project(project)
    assert frame.accentEdit.text() == "accent"
    assert frame.clientIdEdit.text() == "id"
    assert frame.genderInput.currentText() == "Male"
    assert frame.ageInput.currentText() == "19 - 29"
