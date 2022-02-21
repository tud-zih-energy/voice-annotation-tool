"""
Representation of a project file.

Handles loading and saving projects as well as loading the samples from the
audio folder.
"""

from io import StringIO
from os import PathLike
import os, csv
from pathlib import Path
import json
from typing import List, Union

from .annotation import Annotation

class Project:
    def __init__(self, file: Union[str, PathLike]):
        self.tsv_file: Path = Path()
        self.audio_folder: Path = Path()
        self.project_file: Path = Path(file)
        self.annotations_by_path: dict[str, Annotation] = {}
        self.annotations: List[Annotation] = []
        self.modified_annotations: List[str] = []
        self.load()

    def load(self):
        """
        Loads a project from the `project_file` json file. Paths to the audio
        folder and to the tsv file are loaded relative to the project file.
        """
        if not self.project_file.is_file():
            return
        with open(self.project_file) as file:
            data = json.load(file)
            self.modified_annotations = data["modified_annotations"]
            self.audio_folder = self.project_file.parent.joinpath(data.get("audio_folder"))
            self.set_tsv_file(self.project_file.parent.joinpath(data.get("tsv_file")))
            self.set_audio_folder(self.audio_folder)

    def set_audio_folder(self, to: Path):
        """
        Loads the samples from the audio folder of this project into files.
        """
        self.audio_folder = to
        if not self.audio_folder.is_dir():
            return
        for audio_file in os.listdir(self.audio_folder):
            path = Path(audio_file)
            if path.suffix in [".mp3", ".ogg", ".mp4",
                    ".webm", ".avi", ".mkv", ".wav"]:
                if not audio_file in self.annotations_by_path:
                    annotation = Annotation()
                    annotation.path = path
                    self.add_annotation(annotation)
        print("loaded audio folder")
    
    def annotate(self, annotation: Annotation, text : str) -> None:
        """Changes the text of the given annotation."""
        if not annotation.modified:
            self.modified_annotations.append(annotation.path.name)
        annotation.modified = True
        annotation.sentence = text

    def mark_unchanged(self, annotation : Annotation) -> None:
        annotation.modified = False
        if annotation.path in self.modified_annotations:
            self.modified_annotations.remove(annotation.path)

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
                tsv_path = str(self.tsv_file.relative_to(self.project_file.parent))
            json.dump({
                "tsv_file": tsv_path,
                "audio_folder": str(self.audio_folder.relative_to(self.project_file.parent)),
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
            writer.writeheader()
            for annotation in self.annotations:
                writer.writerow(annotation.to_dict())

    def set_tsv_file(self, to: Path):
        """
        Loads the annotations from the `tsv_file` into the annotations array.
        """
        self.tsv_file = to
        if not self.tsv_file.is_file():
            return
        with open(to, newline='') as file:
            reader = csv.DictReader(file, delimiter='\t')
            for row in reader:
                annotation = Annotation(row)
                if annotation.path.exists():
                    if annotation.path.name in self.modified_annotations:
                        annotation.modified = True
                    self.add_annotation(annotation)
        print("loaded csv")

    def delete(self):
        """Delete the TSV and project file."""
        if self.tsv_file.is_file():
            self.tsv_file.unlink()
        self.project_file.unlink()
 
    def delete_annotation(self, annotation: Annotation):
        """Delete a stored annotation and the audio file on disk."""
        annotation.path.unlink(missing_ok=True)
        self.annotations_by_path.pop(annotation.path.name)
        self.annotations.remove(annotation)

    def add_annotation(self, annotation: Annotation):
        annotation.path = self.audio_folder.joinpath(annotation.path)
        self.annotations_by_path[annotation.path.name] = annotation
        self.annotations.append(annotation)

    def importCSV(self, infile: StringIO):
        reader = csv.reader(infile, delimiter=';')
        for row in reader:
            path = row[0]
            if not path in self.annotations_by_path:
                return
            self.annotate(self.annotations_by_path[path], row[1])

    def exportCSV(self, outfile: StringIO):
        writer = csv.writer(outfile, delimiter=';')
        for annotation in self.annotations:
            writer.writerow([annotation.path, annotation.sentence])

    def importJson(self, infile: StringIO):
        data = json.load(infile)
        for row in data:
            for filename in row:
                if not filename in self.annotations_by_path:
                    continue
                self.annotate(self.annotations_by_path[filename], row[filename])

    def exportJson(self, outfile: StringIO):
        data = []
        for annotation in self.annotations:
            data.append({annotation.path.name: annotation.sentence})
        json.dump(data, outfile)
