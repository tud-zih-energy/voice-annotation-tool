from io import StringIO
import os

import pytest
from voice_annotation_tool.project import Annotation
from voice_annotation_tool.project import Project

@pytest.fixture
def project():
    project = Project("")
    project.annotations.append(Annotation({"path": "path", "text": "text"}))
    return project

def test_creation(project):
    assert project

def test_export_csv(project):
    output = StringIO()
    project.exportCSV(output)
    output.seek(0)
    assert output.read() == "path;text\r\n"

def test_export_json(project):
    output = StringIO()
    project.exportJson(output)
    output.seek(0)
    assert output.read() == '[{"path": "text"}]'

def test_import_csv(project):
    project.importCSV(StringIO("path;new"))
    assert project.annotations[0].text == "new"

def test_import_json(project):
    project.importJson(StringIO('[{"path": "new"}]'))
    assert project.annotations[0].text == "new"
