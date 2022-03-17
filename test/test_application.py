from voice_annotation_tool.application import get_settings_file


def test_settings_are_saved():
    assert get_settings_file().is_file()
