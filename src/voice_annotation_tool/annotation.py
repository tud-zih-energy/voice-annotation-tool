from pathlib import Path


class Annotation:
    """Stores the annotated properties for one sample."""

    # An ordered list of the members of an annotation that are read and written
    # to and from a tsv file.
    TSV_HEADER_MEMBERS = [
        "client_id",
        "path",
        "sentence",
        "up_votes",
        "down_votes",
        "age",
        "gender",
        "accent",
    ]

    def __init__(self, dict=None):
        self.client_id: str = "0"
        self.path: Path
        self.sentence: str = ""
        self.up_votes: int = 0
        self.down_votes: int = 0
        self.age: str = ""
        self.gender: str = ""
        self.accent: str = ""
        self.modified: bool = False

        if dict is not None:
            self.from_dict(dict)

    def to_dict(self):
        """
        Returns a dictionary ready to be written to a csv file by a DictWriter.
        """
        properties = {
            "client_id": self.client_id,
            "path": str(self.path.name),
            "sentence": self.sentence,
            "age": self.age,
            "gender": self.gender,
            "accent": self.accent,
            "down_votes": self.down_votes,
            "up_votes": self.up_votes,
        }
        return properties

    def from_dict(self, dict):
        """Loads an annotation from deserialized csv row."""
        self.client_id = dict.get("client_id", "")
        self.path = Path(dict.get("path", ""))
        self.sentence = dict.get("sentence", "")
        self.age = dict.get("age", "")
        self.gender = dict.get("gender", "")
        self.accent = dict.get("accent", "")
        self.down_votes = int(dict.get("down_votes", 0))
        self.up_votes = int(dict.get("up_votes", 0))
