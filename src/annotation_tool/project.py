"""
Representation of a project file.

Handles loading and saving projects as well as loading the samples from the
audio folder.
"""

import os, csv
from pathlib import Path
import json

class Annotation:
    """Stores the annotated properties for one sample."""

    # An ordered list of the members of an annotation that are read and written
    # to and from a tsv file.
    TSV_HEADER_MEMBERS = ["client_id", "file", "text", "up_votes", "down_votes",
            "age", "gender", "accent"]

    def __init__(self, dict=None):
        self.client_id = "0"
        self.file = ""
        self.text = ""
        self.up_votes = 0
        self.down_votes = 0
        self.age = ""
        self.gender = ""
        self.accent = ""
        self.modified = False

        if dict is not None:
            self.from_dict(dict)
    
    def to_dict(self):
        """
        Returns a dictionary ready to be written to a csv file by a DictWriter.
        """
        properties = {}
        for key in self.TSV_HEADER_MEMBERS:
            properties[key] = str(getattr(self, key)).replace("\n", "\\r")
        return properties

    def from_dict(self, dict):
        """Loads an annotation from a loaded csv row."""
        for header in self.TSV_HEADER_MEMBERS:
            value = dict[header]
            if getattr(self, header) is int:
                value = int(value)
            setattr(self, header, value) 

class Project:
    def __init__(self, file):
        self.tsv_file = ""
        self.audio_folder = ""
        self.project_file = file
        self.annotations = []
        self.modified_annotations = []
        self.files = []
        self.load()

    def load(self):
        """
        Loads a project from the `project_file` json file. Paths to the audio
        folder and to the tsv file are loaded relative to the project file.
        """
        if not os.path.exists(self.project_file):
            return
        with open(self.project_file) as file:
            data = json.load(file)
            self.modified_annotations = data["modified_annotations"]
            self.audio_folder = str(Path(self.project_file).joinpath(
                    data.get("audio_folder")).resolve())
            self.set_tsv_file(str(Path(self.project_file).joinpath(
                    data.get("tsv_file")).resolve()))
            self.set_audio_folder(self.audio_folder)

    def set_audio_folder(self, to : str):
        """
        Loads the samples from the audio folder of this project into files.
        """
        self.audio_folder = to
        if not os.path.exists(self.audio_folder):
            return
        existing = {}
        for annotation in self.annotations:
            existing[annotation.file] = True
        for audio_file in os.listdir(self.audio_folder):
            if os.path.splitext(audio_file)[1] in [".mp3", ".ogg", ".mp4",
                    ".webm", ".avi", ".mkv", ".wav"]:
                if not audio_file in existing:
                    annotation = Annotation()
                    annotation.file = audio_file
                    self.annotations.append(annotation)
        print("loaded audio folder")
    
    def annotate(self, index, text):
        """Changes the text of the given annotation."""
        annotation = self.annotations[index]
        if not annotation.modified:
            self.modified_annotations.append(annotation.file)
        if not text:
            self.modified_annotations.remove(annotation.file)
        annotation.modified = bool(text)
        annotation.text = text

    def get_by_file(self, file : str):
        """Returns the annotation of the given file."""
        for annotationNum in range(len(self.annotations)):
            if self.annotations[annotationNum].file == file:
                return annotationNum

    def save(self):
        """
        Saves this project  to the `project_file` and the annotations to the
        `tsv_file`. Paths to the audio folder and to the tsv file are saved
        relative to the project file.
        """
        with open(self.project_file, "w") as file:
            annotation_data = []
            for annotation in self.annotations:
                annotation_data.append(vars(annotation))
            tsv_path = ""
            if self.tsv_file:
                tsv_path = os.path.relpath(self.tsv_file, self.project_file)
            json.dump({
                "tsv_file": tsv_path,
                "audio_folder": os.path.relpath(self.audio_folder, self.project_file),
                "modified_annotations": self.modified_annotations,
            }, file)
        self.save_annotations()

    def save_annotations(self):
        """
        Exports the project's annotations to its tab separated value (tsv) file.
        """
        with open(self.tsv_file, "w", newline='', ) as file:
            writer = csv.DictWriter(file, Annotation.TSV_HEADER_MEMBERS,
                    delimiter='\t')
            for annotation in self.annotations:
                writer.writerow(annotation.to_dict())

    def set_tsv_file(self, to : str):
        """
        Loads the annotations from the `tsv_file` into the annotations array.
        """
        self.tsv_file = to
        if not os.path.exists(self.tsv_file):
            return
        with open(to, newline='') as file:
            reader = csv.DictReader(file, delimiter='\t')
            for row in reader:
                annotation = Annotation(row)
                if os.path.exists(os.path.join(self.audio_folder,
                        annotation.file)):
                    if annotation.file in self.modified_annotations:
                        annotation.modified = True
                    self.annotations.append(annotation)
        print("loaded csv")

    def delete(self):
        """Delete the TSV and project file."""
        if os.path.exists(self.tsv_file):
            os.remove(self.tsv_file)
        os.remove(self.project_file)
 
    def delete_annotation(self, index : int):
        """Delete a stored annotation and the audio file on disk."""
        annotation : Annotation = self.annotations[index]
        os.remove(os.path.join(self.audio_folder, annotation.file))
        self.annotations.remove(annotation)
