class Annotation:
    """Stores the annotated properties for one sample."""

    # An ordered list of the members of an annotation that are read and written
    # to and from a tsv file.
    TSV_HEADER_MEMBERS = ["client_id", "path", "sentence", "up_votes", "down_votes",
            "age", "gender", "accent"]

    def __init__(self, dict=None):
        self.client_id: str = "0"
        self.path: str = ""
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
        properties = {}
        for key in self.TSV_HEADER_MEMBERS:
            properties[key] = str(getattr(self, key)).replace("\n", "\\r")
        return properties

    def from_dict(self, dict):
        """Loads an annotation from a loaded csv row."""
        for header in self.TSV_HEADER_MEMBERS:
            if not header in dict:
                continue
            value = dict[header]
            if getattr(self, header) is int:
                value = int(value)
            setattr(self, header, value) 
