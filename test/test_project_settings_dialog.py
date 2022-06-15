from pathlib import Path
from voice_annotation_tool.project import Project
from voice_annotation_tool.project_settings_dialog import ProjectSettingsDialog


def test_load_project_shows_paths():
    dialog = ProjectSettingsDialog()
    project = Project()
    project.tsv_file = Path("tsv")
    project.audio_folder = Path("audio")
    dialog.load_project(project)
    assert dialog.audioPathEdit.text() == "audio"
    assert dialog.tsvPathEdit.text() == "tsv"


def test_accept():
    dialog = ProjectSettingsDialog()
    dialog.accept()
