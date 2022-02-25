from io import StringIO

import pytest
from voice_annotation_tool.annotation import Annotation
from voice_annotation_tool.project import Project


@pytest.fixture
def project():
    project = Project("")
    project.add_annotation(Annotation({"path": "path", "sentence": "text"}))
    return project


def test_creation(project: Project):
    assert project


def test_export_csv(project: Project):
    output = StringIO()
    project.exportCSV(output)
    output.seek(0)
    assert output.read() == "path;text\r\n"


def test_export_json(project: Project):
    output = StringIO()
    project.exportJson(output)
    output.seek(0)
    assert output.read() == '[{"path": "text"}]'


def test_import_csv(project: Project):
    project.importCSV(StringIO("path;new"))
    assert project.annotations[0].sentence == "new"


def test_import_json(project: Project):
    project.importJson(StringIO('[{"path": "new"}]'))
    assert project.annotations[0].sentence == "new"


def test_save(project: Project):
    buffer = StringIO()
    project.save(buffer, Path("tmp"))
    buffer.seek(0)
    content = '{"tsv_file": "project.tsv", "audio_folder": "audio", "modified_annotations": []}'
    assert buffer.read() == content


def test_save_annotations(project: Project):
    buffer = StringIO()
    project.save_annotations(buffer)
    buffer.seek(0)
    content = "client_id\tpath\tsentence\tup_votes\tdown_votes\tage\tgender\taccent\r\n\tpath\ttext\t0\t0\t\t\t\r\n"
    assert buffer.read() == content


def test_load():
    project = Project()
    content = (
        '{"tsv_file":"../file.tsv","audio_folder":"audio","modified_annotations":[]}'
    )
    project.load_json(StringIO(content), Path("tmp"))
    print(project.audio_folder)
    assert project.audio_folder == Path("tmp/audio")
    assert project.tsv_file and project.tsv_file.name == "file.tsv"


def test_load_annotations():
    project = Project()
    project.audio_folder = Path("tmp/audio")
    project.tsv_file = Path("tmp/project.tsv")
    content = """client_id\tpath\tsentence\tup_votes\tdown_votes\tage\tgender\taccent
abc\tsample.mp3\ttext\t2\t2\ttwenties\tother\taccent"""
    project.load_tsv_file(StringIO(content))
    annotation = project.annotations[0]
    assert annotation.sentence == "text"
    assert annotation.age == "twenties"
    assert annotation.accent == "accent"
    assert annotation.up_votes == 2
    assert annotation.down_votes == 2
    assert annotation.gender == "other"
    assert annotation.path == Path("tmp/audio/sample.mp3")
