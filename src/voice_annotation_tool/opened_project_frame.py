"""
The main interface used to edit a project.

Contains the audio player controls, the list of audio samples and a field to
edit the annotation.
"""

import os
from typing import Dict, List
from PySide6.QtCore import QModelIndex, Slot, QTime, QUrl
from PySide6.QtMultimedia import QAudioDecoder
from PySide6.QtWidgets import QFrame, QFileDialog, QMessageBox, QPushButton

from voice_annotation_tool.audio_playback_widget import AudioPlaybackWidget

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

        self.audioPlaybackWidget.next_pressed.connect(self.next_pressed)
        self.audioPlaybackWidget.previous_pressed.connect(self.previous_pressed)
        self.project: Project
        self.annotationList.installEventFilter(self)
        for age in AGE_STRINGS:
            self.ageInput.addItem(age)
        self.ageInput.addItem(self.tr("[Multiple]"))

    def get_playback_buttons(self) -> List[QPushButton]:
        return self.audioPlaybackWidget.playback_buttons

    def apply_shortcuts(self, shortcuts : Dict[int,str]):
        """
        Applies the shortcuts to the buttons.
        The shortcut is also added to the tooltip.
        """
        self.audioPlaybackWidget.apply_shortcuts(shortcuts)

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
        self.current_item = -1
        self.set_annotation_length(-1)
        self.annotationList.setCurrentIndex(self.annotationList.model().index(0,0))
        if not len(self.project.annotations):
            message = QMessageBox()
            message.setText(self.tr(
                "No samples found in the audio folder: {folder}"
                ).format(folder=project.audio_folder))
            message.exec()

    def set_annotation_length(self, length):
        """Set the length of an annotation displayed in the list."""
        if self.current_item > 0 and length > 0:
            item = self.annotationList.item(self.current_item)
            item.setText(f"[{QTime(0, 0).addMSecs(length).toString()}] {item.text()}")
        self.current_item += 1
        decoder = QAudioDecoder()
        decoder.setSource(QUrl.fromLocalFile(os.path.join(
                self.project.audio_folder,
                self.project.annotations[self.current_item].path)))
        decoder.durationChanged.connect(self.set_annotation_length)
        decoder.start()

    def delete_selected(self):
        """Delete the selected annotations and audio files."""
        for selected in self.get_selected_annotations()[::-1]:
            self.project.delete_annotation(selected.row())
        self.annotationList.model().layoutChanged.emit()

    def get_selected_annotations(self) -> List[Annotation]:
        annotations: List[Annotation] = []
        for selected_index in self.annotationList.selectionModel().selectedIndexes():
            annotations.append(selected_index.data(ANNOTATION_ROLE))
        return annotations

    @Slot()
    def previous_pressed(self):
        self.annotationList.setCurrentIndex(self.annotationList.model().index(
                self.annotationList.currentIndex().row() - 1, 0))

    @Slot()
    def next_pressed(self):
        self.annotationList.setCurrentIndex(self.annotationList.model().index(
                self.annotationList.currentIndex().row() + 1, 0))

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
        self.project.annotate(self.annotationList.currentIndex().row(), text)
        self.annotationList.model().layoutChanged.emit()

    @Slot()
    def selection_changed(self, selected, deselected):
        self.update_metadata_header()
        index: QModelIndex = self.annotationList.currentIndex()
        self.audioPlaybackWidget.previousButton.setEnabled(index.row() > 0)
        self.audioPlaybackWidget.nextButton.setEnabled(index.row() < len(self.project.annotations) - 1)
        annotation : Annotation = index.data(ANNOTATION_ROLE)
        self.annotationEdit.blockSignals(True)
        self.annotationEdit.setText(annotation.sentence)
        self.annotationEdit.blockSignals(False)
        self.audioPlaybackWidget.play_file(os.path.join(self.project.audio_folder,
                annotation.path))

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
    def mark_unchanged_pressed(self):
        for annotation in self.get_selected_annotations():
            self.project.mark_unchanged(annotation)
        self.annotationList.model().layoutChanged.emit()
