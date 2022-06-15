from io import StringIO
import os, csv
from pathlib import Path
import json
from typing import TextIO

from voice_annotation_tool.annotation import Annotation


def relative_or_absolute(path: Path, relative_to: Path) -> Path:
    """Returns the path relative to a second path, or the
    absolute path if that isn't possible.
    """
    try:
        return path.relative_to(relative_to)
    except ValueError:
        return path


class Project:
    """Representation of a project file.

    Handles loading and saving the project to json files, loading and
    writing the tsv file which holds the sample metadata as well as
    loading the samples from the audio folder.
    Provides methods for importing and exporting json, text and csv
    files.
    The tsv file and audio folder of a project can be None.
    """

    def __init__(self):
        self.tsv_file: Path | None = None
        "The file where the metadata of the samples is stored."
        self.audio_folder: Path | None = None
        "The folder containing the speech samples."
        self.annotations_by_path: dict[str, Annotation] = {}
        """A dictionary that maps the name of the sample file to the
        annotations"""
        self.annotations: list[Annotation] = []
        "The annotations of the project."
        self.modified_annotations: list[str] = []
        """A list of sample file names whose text was modified since
        the project was created."""

    def load_json(self, file: TextIO, location: Path = Path()) -> bool:
        """Loads a project from a json file.

        Paths to the audio folder and to the tsv file are loaded relative
        to the given location. This does not load the contents of the
        tsv file or the audio folder.
        """
        data = json.load(file)
        if not all(
            ["modified_annotations" in data, "audio_folder" in data, "tsv_file" in data]
        ):
            return False
        self.modified_annotations = data["modified_annotations"]
        self.audio_folder = location.joinpath(data.get("audio_folder"))
        self.tsv_file = location.joinpath(data.get("tsv_file"))
        return True

    def load_audio_files(self, folder: Path):
        """Creates empty annotations for the audio files in the given
        folder which are not already loaded from a tsv file.
        """
        self.audio_folder = folder
        if not self.audio_folder.is_dir():
            return
        for audio_file in os.listdir(self.audio_folder):
            path = Path(audio_file)
            if not path.suffix in [
                ".mp3",
                ".ogg",
                ".mp4",
                ".webm",
                ".avi",
                ".mkv",
                ".wav",
            ]:
                continue
            annotation = Annotation()
            annotation.path = self.audio_folder.joinpath(path)
            self.add_annotation(annotation)

    def annotate(self, annotation: Annotation, text: str) -> None:
        """Changes the text of the given annotation and marks it as
        modified.
        """
        if not annotation.modified:
            self.modified_annotations.append(annotation.path.name)
        annotation.modified = True
        annotation.sentence = text

    def mark_unchanged(self, annotation: Annotation) -> None:
        """Remove the modified mark of the given annotation."""
        annotation.modified = False
        if annotation.path in self.modified_annotations:
            self.modified_annotations.remove(annotation.path)

    def save(self, file: TextIO, location: Path = Path()):
        """Saves this project to the given buffer. Paths to the audio
        folder and to the tsv file are saved relative to the project file.
        """
        data = {
            "tsv_file": "",
            "audio_folder": "",
            "modified_annotations": self.modified_annotations,
        }
        if self.tsv_file:
            data["tsv_file"] = str(relative_or_absolute(self.tsv_file, location))
        if self.audio_folder:
            data["audio_folder"] = str(
                relative_or_absolute(self.audio_folder, location)
            )
        json.dump(data, file)

    def save_annotations(self, file: TextIO):
        """Exports the project's annotations to a tab separated
        value (tsv) file.
        """
        writer = csv.DictWriter(file, Annotation.TSV_HEADER_MEMBERS, delimiter="\t")
        writer.writeheader()
        for annotation in self.annotations:
            writer.writerow(annotation.to_dict())

    def load_tsv_file(self, file: TextIO):
        """Loads the annotations from the `tsv_file` into the
        annotations array.
        """
        reader = csv.DictReader(file, delimiter="\t")
        for row in reader:
            annotation = Annotation(row)
            if annotation.path.name in self.modified_annotations:
                annotation.modified = True
            self.add_annotation(annotation, overwrite=True)
        print("loaded csv")

    def delete_tsv(self):
        """Deletes the TSV file."""
        if self.tsv_file and self.tsv_file.is_file():
            self.tsv_file.unlink()

    def delete_annotation(self, annotation: Annotation):
        """Deletes a stored annotation and the audio file on disk."""
        annotation.path.unlink(missing_ok=True)
        self.annotations_by_path.pop(annotation.path.name)
        self.annotations.remove(annotation)

    def add_annotation(self, annotation: Annotation, overwrite=False):
        """Adds the annotation to the project. If an annotation with
        the same path already exists and overwrite is true it is replaced.

        If the audio folder is specified, it is added to the annotation path.
        """
        if self.audio_folder:
            annotation.path = self.audio_folder.joinpath(annotation.path)
        if annotation.path.name in self.annotations_by_path:
            if overwrite:
                existing = self.annotations.index(
                    self.annotations_by_path[annotation.path.name]
                )
                self.annotations[existing] = annotation
            else:
                return
        else:
            self.annotations.append(annotation)
        self.annotations_by_path[annotation.path.name] = annotation

    def importCSV(self, infile: StringIO):
        """Imports a CSV file created using the export function."""
        reader = csv.DictReader(infile, delimiter=";")
        for row in reader:
            if not row["file"] in self.annotations_by_path:
                return
            self.annotate(self.annotations_by_path[row["file"]], row["text"])

    def exportCSV(self, outfile: StringIO):
        """Exports a CSV file with the path and text of the annotations
        as columns.
        """
        writer = csv.writer(outfile, delimiter=";")
        writer.writerow(["file", "text"])
        for annotation in self.annotations:
            writer.writerow([annotation.path.name, annotation.sentence])

    def importJson(self, infile: StringIO):
        """Imports a Json file created using the exportJson function."""
        data = json.load(infile)
        for row in data:
            if "file" in row and "text" in row:
                if not row["file"] in self.annotations_by_path:
                    continue
                self.annotate(self.annotations_by_path[row["file"]], row["text"])

    def exportJson(self, outfile: StringIO):
        """Exports a Json file with a list of dictionaries containing
        the annotation path as key and the text as value.
        """
        data: list[dict[str, str]] = []
        for annotation in self.annotations:
            data.append({"file": annotation.path.name, "text": annotation.sentence})
        json.dump(data, outfile)

    def __hash__(self):
        return hash(frozenset(map(hash, self.annotations)))
