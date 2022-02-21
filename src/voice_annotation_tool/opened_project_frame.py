"""
The main interface used to edit a project.

Contains the audio player controls, the list of audio samples and a field to
edit the annotation.
"""

import os
from typing import Dict, List
from PySide6.QtGui import QIcon
from PySide6.QtCore import QModelIndex, QSize, Slot, QTime, QUrl
from PySide6.QtMultimedia import QMediaPlayer, QAudioOutput, QAudioDecoder
from PySide6.QtWidgets import QFrame, QFileDialog, QMessageBox, QPushButton

from .annotation_list_model import AnnotationListModel, ANNOTATION_ROLE
from .opened_project_frame_ui import Ui_OpenedProjectFrame
from .project import Annotation, Project

# Age groups how they are displayed on the CommonVoice website and how they are
# stored in the exported tsv file.
AGES = [
    "",
    "teens",
    "twenties",
    "thirties",
    "fourties",
    "fifties",
    "sixties",
    "seventies",
    "eighties",
    "nineteens",
]

AGE_STRINGS = [
    "",
    "< 19",
    "19 - 29",
    "30 - 39",
    "40 - 49",
    "50 - 59",
    "60 - 69",
    "70 - 79",
    "80 - 89",
    "> 89",
]

GENDERS = ["", "male", "female", "other"]

class OpenedProjectFrame(QFrame, Ui_OpenedProjectFrame):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

        self.project : Project
        self.output = QAudioOutput()
        self.player = QMediaPlayer()
        self.player.setAudioOutput(self.output)
        self.playback_buttons = [self.playPauseButton, self.previousButton,
                self.stopButton, self.nextButton]
        self.buttonTooltips : Dict[QPushButton, str] = {}

        self.annotationList.installEventFilter(self)
        self.stopButton.pressed.connect(self.player.stop)
        self.timeSlider.valueChanged.connect(self.player.setPosition)
        self.volumeSlider.valueChanged.connect(self.volume_changed)
        self.player.durationChanged.connect(self.update_duration)
        self.player.positionChanged.connect(self.update_position)
        self.player.errorOccurred.connect(self.playerError)
        self.player.playbackStateChanged.connect(self.playback_state_changed)

        for age in AGE_STRINGS:
            self.ageInput.addItem(age)
        self.ageInput.addItem(self.tr("[Multiple]"))
        self.reload_button_tooltips()

    def get_button_tooltip(self, button : QPushButton) -> str:
        """
        Returns the original tooltip of a button.
        Stores the current tooltip if it is accessed for the first time.
        """
        if not button in self.buttonTooltips:
            self.buttonTooltips[button] = button.toolTip()
        return self.buttonTooltips[button]

    def apply_shortcuts(self, shortcuts : List[str]):
        """
        Applies the shortcuts to the buttons.
        The shortcut is also added to the tooltip.
        """
        for buttonNum in range(len(shortcuts)):
            button = self.playback_buttons[buttonNum]
            button.setShortcut(shortcuts[buttonNum])
        self.reload_button_tooltips()

    def reload_button_tooltips(self):
        """Adds the shortcut of the buttons to the tooltips."""
        for button in self.playback_buttons:
            button.setToolTip(self.get_button_tooltip(button) + " " +
                    button.shortcut().toString())

    def update_metadata_header(self):
        """Loads the profile metadata of the selected files into the GUI."""
        first = True
        age = None
        gender = None
        accent = None
        client_id = None
        for annotation in self.get_selected_annotations():
            if first:
                age = annotation.age
                gender = annotation.gender
                accent = annotation.accent
                client_id = annotation.client_id
                first = False
            if annotation.age != age:
                age = None
            if annotation.gender != gender:
                gender = None
            if annotation.accent != accent:
                accent = None
            if annotation.client_id != client_id:
                client_id = None

            if all([age == None, gender == None,
                    accent == None, client_id == None]):
                break

        if first:
            # No annotation in the list.
            return

        inputs = [self.ageInput, self.accentEdit,
                self.genderInput, self.clientIdEdit]
        for input in inputs:
            input.blockSignals(True)

        # The last index of the ages and genders combo box is the "multiple"
        # option.
        gender_index = len(GENDERS) if gender == None else GENDERS.index(gender)
        self.genderInput.setCurrentIndex(gender_index)
        self.genderInput.view().setRowHidden(len(GENDERS), gender != None)

        age_index = len(AGES) if age == None else AGES.index(age)
        self.ageInput.setCurrentIndex(age_index)
        self.ageInput.view().setRowHidden(len(AGES), age != None)

        self.clientIdEdit.clear()
        if client_id:
            self.clientIdEdit.insert(client_id)

        self.accentEdit.clear()
        if accent:
            self.accentEdit.insert(accent)

        for input in inputs:
            input.blockSignals(False)

    def load_project(self, project : Project):
        """Loads the project's samples and annotations."""
        self.project = project
        self.annotationList.setModel(AnnotationListModel(self.project))
        self.annotationList.selectionModel().selectionChanged.connect(self.selection_changed)
        self.annotationList.setCurrentIndex(self.annotationList.model().index(0,0))
        if not len(self.project.annotations):
            message = QMessageBox()
            message.setText(self.tr(
                "No samples found in the audio folder: {folder}"
                ).format(folder=project.audio_folder))
            message.exec()

    def delete_selected(self):
        """Delete the selected annotations and audio files."""
        for selected in self.get_selected_annotations():
            self.project.delete_annotation(selected)
        self.annotationList.model().layoutChanged.emit()

    def get_selected_annotations(self) -> List[Annotation]:
        """ Returns all the selected annotations in the annotation panel. """
        annotations: List[Annotation] = []
        for selected_index in self.annotationList.selectionModel().selectedIndexes():
            annotations.append(selected_index.data(ANNOTATION_ROLE))
        return annotations

    @Slot()
    def playerError(self, error, string):
        message = QMessageBox()
        message.setText(self.tr(
            "Error playing audio: {error}"
            ).format(error=string))
        message.exec()
    
    @Slot()
    def playback_state_changed(self, state):
        icon = QIcon()
        playing = state == QMediaPlayer.PlayingState
        icon.addFile(u":/playback/pause" if playing else u":/playback/play",
                QSize(), QIcon.Normal, QIcon.Off)
        self.playPauseButton.setIcon(icon)

    @Slot()
    def gender_selected(self, gender : int):
        if gender == len(GENDERS):
            return
        for selected_item in self.annotationList.selectedIndexes():
            annotation: Annotation = selected_item.data(ANNOTATION_ROLE)
            annotation.gender = GENDERS[gender]
        self.update_metadata_header()

    @Slot()
    def age_selected(self, age : int):
        if age == len(AGES):
            return
        for selected_item in self.annotationList.selectedIndexes():
            annotation: Annotation = selected_item.data(ANNOTATION_ROLE)
            annotation.age = AGES[age]
        self.update_metadata_header()

    @Slot()
    def accent_changed(self, accent : str):
        for selected_item in self.annotationList.selectedIndexes():
            annotation: Annotation = selected_item.data(ANNOTATION_ROLE)
            annotation.accent = accent
        self.update_metadata_header()

    @Slot()
    def client_id_changed(self, client_id : str):
        for selected_item in self.annotationList.selectedIndexes():
            annotation: Annotation = selected_item.data(ANNOTATION_ROLE)
            annotation.client_id = client_id
        self.update_metadata_header()

    @Slot()
    def text_changed(self):
        text = self.annotationEdit.toPlainText()
        selected_annotation: Annotation = self.annotationList.currentIndex()\
                .data(ANNOTATION_ROLE)
        self.project.annotate(selected_annotation, text)
        self.annotationList.model().layoutChanged.emit()

    @Slot()
    def selection_changed(self, selected, deselected):
        self.update_metadata_header()
        index: QModelIndex = self.annotationList.currentIndex()
        self.previousButton.setEnabled(index.row() > 0)
        self.nextButton.setEnabled(index.row() < len(self.project.annotations) - 1)
        annotation : Annotation = index.data(ANNOTATION_ROLE)
        self.annotationEdit.blockSignals(True)
        self.annotationEdit.setText(annotation.sentence)
        self.annotationEdit.blockSignals(False)
        self.player.setSource(QUrl.fromLocalFile(os.path.join(self.project.audio_folder,
                annotation.path)))

    @Slot()
    def import_profile_pressed(self):
        path, _ = QFileDialog.getOpenFileName(self, "Import Profile", "",
                "Text Files (*.txt)")
        if not path:
            return
        properties = {}
        with open(path) as file:
            for line in file:
                parts = line.split(": ")
                properties[parts[0]] = parts[1].rstrip()
        for annotation in self.get_selected_annotations():
            if "age" in properties:
                annotation.age = properties["age"]
            if "gender" in properties:
                annotation.gender = properties["gender"]
            if "accent" in properties:
                annotation.accent = properties["accent"]
        self.annotationList.model().layoutChanged.emit()
        self.update_metadata_header()

    @Slot()
    def play_pause_pressed(self):
        if self.player.playbackState() == QMediaPlayer.PlayingState:
            self.player.pause()
        else:
            self.player.play()

    @Slot()
    def previous_pressed(self):
        self.annotationList.setCurrentIndex(self.annotationList.model().index(
                self.annotationList.currentIndex().row() - 1, 0))

    @Slot()
    def next_pressed(self):
        self.annotationList.setCurrentIndex(self.annotationList.model().index(
                self.annotationList.currentIndex().row() + 1, 0))

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

    @Slot()
    def mark_unchanged_pressed(self):
        for annotation in self.get_selected_annotations():
            self.project.mark_unchanged(annotation)
        self.annotationList.model().layoutChanged.emit()
