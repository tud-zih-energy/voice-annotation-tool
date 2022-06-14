from pathlib import Path
from PySide6.QtCore import QSize, QTime, QUrl, Slot, Signal
from PySide6.QtGui import QIcon
from PySide6.QtMultimedia import QAudioOutput, QMediaPlayer
from PySide6.QtWidgets import QMessageBox, QPushButton, QWidget
from voice_annotation_tool.audio_playback_widget_ui import Ui_AudioPlaybackWidget


class AudioPlaybackWidget(QWidget, Ui_AudioPlaybackWidget):
    """
    Widget to play audio.
    """

    next_pressed = Signal()
    previous_pressed = Signal()

    def __init__(self, parent=None):
        super().__init__()
        self.setupUi(self)
        self.output = QAudioOutput()
        self.player = QMediaPlayer()
        self.player.setAudioOutput(self.output)
        self.buttonTooltips: dict[QPushButton, str] = {}
        self.playback_buttons = [
            self.playPauseButton,
            self.previousButton,
            self.stopButton,
            self.nextButton,
        ]
        self.stopButton.pressed.connect(self.player.stop)
        self.timeSlider.valueChanged.connect(self.player.setPosition)
        self.volumeSlider.valueChanged.connect(self.volume_changed)
        self.player.durationChanged.connect(self.update_duration)
        self.player.positionChanged.connect(self.update_position)
        self.player.errorOccurred.connect(self.playerError)
        self.player.playbackStateChanged.connect(self.playback_state_changed)
        self.reload_button_tooltips()

    def get_button_tooltip(self, button: QPushButton) -> str:
        """Returns the original tooltip of a button.

        Stores the current tooltip if it is accessed for the first time.
        """
        if not button in self.buttonTooltips:
            self.buttonTooltips[button] = button.toolTip()
        return self.buttonTooltips[button]

    def get_shortcuts(self) -> list[str]:
        """Returns a list of the shortcuts of the buttons."""
        shortcuts: list[str] = []
        for button in self.playback_buttons:
            shortcuts.append(button.shortcut().toString())
        return shortcuts

    def apply_shortcuts(self, shortcuts: list[str]):
        """Applies the shortcuts to the buttons.

        The shortcut is also added to the tooltip.
        """
        for buttonNum in range(len(shortcuts)):
            button = self.playback_buttons[buttonNum]
            button.setShortcut(shortcuts[buttonNum])
        self.reload_button_tooltips()

    def reload_button_tooltips(self):
        """Adds the shortcut of the buttons to the tooltips."""
        for button in self.playback_buttons:
            button.setToolTip(
                self.get_button_tooltip(button) + " " + button.shortcut().toString()
            )

    def load_file(self, file: Path) -> None:
        """Loads the given audio file which can then be played by
        pressing the pause/play button.
        """
        self.player.setSource(QUrl.fromLocalFile(file))

    @Slot()
    def playerError(self, error, string):
        message = QMessageBox()
        message.setText(self.tr("Error playing audio: {error}").format(error=string))
        message.exec()

    @Slot()
    def playback_state_changed(self, state):
        playing = state == QMediaPlayer.PlayingState
        file = ":/playback/pause" if playing else ":/playback/play"
        icon = QIcon()
        icon.addFile(file, QSize(), QIcon.Normal, QIcon.Off)
        self.playPauseButton.setIcon(icon)

    @Slot()
    def play_pause_button_pressed(self):
        if self.player.playbackState() == QMediaPlayer.PlayingState:
            self.player.pause()
        else:
            self.player.play()

    @Slot()
    def previous_button_pressed(self):
        self.previous_pressed.emit()

    @Slot()
    def next_button_pressed(self):
        self.next_pressed.emit()

    @Slot()
    def volume_changed(self, to):
        self.output.setVolume(to / 100)

    @Slot()
    def update_duration(self, duration):
        self.totalTimeLabel.setText(QTime(0, 0).addSecs(duration).toString())
        self.timeSlider.setMaximum(duration)

    @Slot()
    def update_position(self, position):
        self.elapsedTimeLabel.setText(QTime(0, 0).addSecs(position).toString())
        self.timeSlider.blockSignals(True)
        self.timeSlider.setValue(position)
        self.timeSlider.blockSignals(False)
