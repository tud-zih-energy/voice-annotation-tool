from io import StringIO
import json
from pathlib import Path
from PySide6.QtGui import QKeySequence
import pytest
from voice_annotation_tool.project import Project

from voice_annotation_tool.main_window import MainWindow


@pytest.fixture
def main_window():
    return MainWindow()


def test_load_settings(main_window: MainWindow, tmpdir):
    folder = Path(tmpdir)
    first = folder / "test.json"
    second = folder / "other.json"
    first.touch()
    second.touch()
    settings = {"shortcuts": ["Ctrl+L"], "recent_projects": [str(first), str(second)]}
    main_window.load_settings(StringIO(json.dumps(settings)))
    playback_buttons = main_window.opened_project_frame.get_playback_buttons()
    assert main_window.recent_projects == [first, second]
    assert playback_buttons[0].shortcut() == QKeySequence("Ctrl+L")


def test_save_settings(main_window: MainWindow):
    settings = {"shortcuts": ["Ctrl+L"], "recent_projects": []}
    main_window.load_settings(StringIO(json.dumps(settings)))
    output = StringIO()
    main_window.save_settings(output)
    output.seek(0)
    assert json.loads(output.read())["shortcuts"][0] == "Ctrl+L"


def test_set_current_project(main_window: MainWindow, tmpdir):
    folder = Path(tmpdir)
    audio_folder = folder / "audio"
    audio_folder.mkdir()
    audio_file = audio_folder / "audio.mp3"
    audio_file.touch()
    project = Project()
    project.load_audio_files(audio_folder)
    project.tsv_file = folder / "project.tsv"
    main_window.set_current_project(project)
    assert main_window.windowTitle() == "Unsaved Project"
    assert main_window.actionProjectSettings.isEnabled()
    assert main_window.actionDeleteProject.isEnabled()
    assert main_window.actionExportCSV.isEnabled()
    assert main_window.choose_project_frame.isHidden()


def test_loading_project_from_file(main_window: MainWindow, tmpdir):
    folder = Path(tmpdir)
    project_path = folder / "project.json"
    with open(project_path, "w") as file:
        file.write(
            '{"tsv_file":"project.tsv","audio_folder":"audio","modified_annotations":[]}'
        )
    audio_folder: Path = folder / "audio"
    audio_folder.mkdir(parents=True)
    audio_file = audio_folder / "audio.mp3"
    other_audio_file = audio_folder / "other.mp3"
    audio_file.touch()
    other_audio_file.touch()
    tsv_file = folder / "project.tsv"
    with open(tsv_file, "w") as file:
        content = """client_id\tpath\tsentence\tup_votes\tdown_votes\tage\tgender\taccent
abc\taudio.mp3\ttext\t2\t2\ttwenties\tother\taccent"""
        file.write(content)
    main_window.load_project_from_file(project_path)
    assert main_window.project
    assert main_window.project.audio_folder == audio_folder
    assert main_window.project.tsv_file == tsv_file
    assert main_window.project.annotations[0].sentence == "text"
    assert main_window.project.annotations[0].path == audio_file
    assert main_window.project.annotations[1].sentence == ""
    assert main_window.project.annotations[1].path == other_audio_file
