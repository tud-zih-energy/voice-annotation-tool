from PySide6.QtWidgets import QPushButton

from voice_annotation_tool.audio_playback_widget import AudioPlaybackWidget


def test_tooltips_have_shortcuts():
    widget = AudioPlaybackWidget()
    play_button: QPushButton = widget.playPauseButton
    assert play_button.shortcut().toString() in play_button.toolTip()


def test_icons_loaded():
    widget = AudioPlaybackWidget()
    image = widget.playPauseButton.icon().pixmap(10, 10).toImage()
    value = image.pixelColor(3, 3).valueF()
    assert value > 0.2 and value < 0.3
