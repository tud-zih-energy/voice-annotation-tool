from typing import Callable, List, Union
from voice_annotation_tool.project import Annotation

class AnnotationMultiselection:
    """
    Provides an abstraction for handling a list of annotations.
    The getters return a string if all selected annotations have the same
    value, None otherwise.
    """

    def __init__(self, selected: List[Annotation]) -> None:
        self.selected = selected

    def get_client_id(self) -> Union[str, None]:
        """
        Get the common client id of the selected annotations, None if there is
        none.
        """
        return self._get_common(Annotation.get_client_id)

    def get_gender(self) -> Union[str, None]:
        """
        Get the common gender of the selected annotations, None if there is
        none.
        """
        return self._get_common(Annotation.get_gender)
    
    def get_accent(self) -> Union[str, None]:
        """
        Get the common accent of the selected annotations, None if there is
        none.
        """
        return self._get_common(Annotation.get_accent)

    def get_age(self) -> Union[str, None]:
        """
        Get the common age of the selected annotations, None if there is none.
        """
        return self._get_common(Annotation.get_age)

    def _get_common(self, getter: Callable[[Annotation],str]) -> Union[str, None]:
        """Generic function to get a common annotation metadata value."""
        common_value = None
        for selected in self.selected:
            value = getter(selected)
            if common_value == None:
                # First value.
                common_value = value
            if value != common_value:
                # No common value.
                return None
        return common_value
