from PySide6.QtCore import QModelIndex, Slot
from PySide6.QtWidgets import QFrame, QFileDialog, QPushButton, QWidget

from voice_annotation_tool.annotation_list_model import AnnotationListModel, ANNOTATION_ROLE
from voice_annotation_tool.opened_project_frame_ui import Ui_OpenedProjectFrame
from voice_annotation_tool.project import Annotation, Project

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
"Age groups how they are stored in the exported tsv file."

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
"Age groups how they are displayed on the CommonVoice website."

GENDERS = ["", "male", "female", "other"]
"List of possible genders."


class OpenedProjectFrame(QFrame, Ui_OpenedProjectFrame):
    """The main interface used to edit a project.

    Contains the audio player controls, the list of audio samples
    and a text field where the annotation text can be edited.
    """

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

    def get_playback_buttons(self) -> list[QPushButton]:
        """Returns a list of buttons used to control the audio playback."""
        return self.audioPlaybackWidget.playback_buttons

    def get_shortcuts(self) -> list[str]:
        """Returns a list of shortcuts for the audio playback buttons."""
        return self.audioPlaybackWidget.get_shortcuts()

    def apply_shortcuts(self, shortcuts: list[str]):
        """Applies the shortcuts to the buttons.

        The shortcut is also added to the tooltip.
        """
        self.audioPlaybackWidget.apply_shortcuts(shortcuts)

    def update_metadata_header(self):
        """Loads the metadata of the selected annotations into the GUI."""
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

            if all([age == None, gender == None, accent == None, client_id == None]):
                break

        if first:
            # No annotation in the list.
            return

        inputs = [self.ageInput, self.accentEdit, self.genderInput, self.clientIdEdit]
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

    def load_project(self, project: Project):
        """Loads the project's annotations into the GUI."""
        self.project = project
        self.annotationList.setModel(AnnotationListModel(self.project))
        self.annotationList.selectionModel().selectionChanged.connect(
            self.selection_changed
        )
        self.annotationEdit.clear()
        self.update_metadata_widgets()
        if len(project.annotations):
            self.annotationList.setCurrentIndex(self.annotationList.model().index(0, 0))

    def update_metadata_widgets(self):
        """Disables or enables the widgets used to edit the annotation
        metadata depending on if there are any annotations in the project.
        """
        widgets: list[QWidget] = self.get_metadata_inputs()
        widgets += self.get_playback_buttons()
        for widget in widgets:
            widget.setEnabled(len(self.project.annotations) > 0)

    def get_metadata_inputs(self) -> list[QWidget]:
        """Returns a list of the QComboBoxes, QLineEdits, and buttons
        that are used to edit the annotation metadata.
        """
        return [
            self.ageInput,
            self.genderInput,
            self.accentEdit,
            self.clientIdEdit,
            self.importButton,
            self.markUnchangedButton,
            self.annotationEdit,
        ]

    def delete_selected(self):
        """Delete the selected annotations and audio files."""
        for selected in self.get_selected_annotations():
            self.project.delete_annotation(selected)
        self.annotationList.model().layoutChanged.emit()
        self.update_metadata_widgets()

    def get_selected_annotations(self) -> list[Annotation]:
        """Returns all the selected annotations in the annotation panel."""
        annotations: list[Annotation] = []
        for selected_index in self.annotationList.selectionModel().selectedIndexes():
            annotations.append(selected_index.data(ANNOTATION_ROLE))
        return annotations

    @Slot()
    def previous_pressed(self):
        current = self.annotationList.currentIndex().row()
        previous = self.annotationList.model().index(current - 1, 0)
        self.annotationList.clearSelection()
        self.annotationList.setCurrentIndex(previous)

    @Slot()
    def next_pressed(self):
        current = self.annotationList.currentIndex().row()
        next = self.annotationList.model().index(current + 1, 0)
        self.annotationList.clearSelection()
        self.annotationList.setCurrentIndex(next)

    @Slot()
    def gender_selected(self, gender: int):
        if gender == len(GENDERS):
            return
        for selected_item in self.annotationList.selectedIndexes():
            annotation: Annotation = selected_item.data(ANNOTATION_ROLE)
            annotation.gender = GENDERS[gender]
        self.update_metadata_header()

    @Slot()
    def age_selected(self, age: int):
        if age == len(AGES):
            return
        for selected_item in self.annotationList.selectedIndexes():
            annotation: Annotation = selected_item.data(ANNOTATION_ROLE)
            annotation.age = AGES[age]
        self.update_metadata_header()

    @Slot()
    def accent_changed(self, accent: str):
        for selected_item in self.annotationList.selectedIndexes():
            annotation: Annotation = selected_item.data(ANNOTATION_ROLE)
            annotation.accent = accent
        self.update_metadata_header()

    @Slot()
    def client_id_changed(self, client_id: str):
        for selected_item in self.annotationList.selectedIndexes():
            annotation: Annotation = selected_item.data(ANNOTATION_ROLE)
            annotation.client_id = client_id
        self.update_metadata_header()

    @Slot()
    def text_changed(self):
        text: str = self.annotationEdit.toPlainText()
        selected_annotation: Annotation = self.annotationList.currentIndex().data(
            ANNOTATION_ROLE
        )
        if selected_annotation:
            self.project.annotate(selected_annotation, text)

    @Slot()
    def selection_changed(self, selected, deselected):
        self.update_metadata_header()
        index: QModelIndex = self.annotationList.currentIndex()
        self.audioPlaybackWidget.previousButton.setEnabled(index.row() > 0)
        self.audioPlaybackWidget.nextButton.setEnabled(
            index.row() < len(self.project.annotations) - 1
        )
        annotation: Annotation = index.data(ANNOTATION_ROLE)
        if not annotation:
            return
        self.annotationEdit.blockSignals(True)
        self.annotationEdit.setText(annotation.sentence)
        self.annotationEdit.blockSignals(False)
        if annotation.path.is_file():
            self.audioPlaybackWidget.load_file(annotation.path)
        for buttons in self.get_playback_buttons():
            buttons.setEnabled(annotation.path.is_file())

    @Slot()
    def import_profile_pressed(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Import Profile", "", "Text Files (*.txt)"
        )
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
        self.update_metadata_header()

    @Slot()
    def mark_unchanged_pressed(self):
        for annotation in self.get_selected_annotations():
            self.project.mark_unchanged(annotation)
