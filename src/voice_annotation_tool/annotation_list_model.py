from typing import Any, Union
from PySide6.QtCore import QAbstractListModel, QModelIndex, QPersistentModelIndex
from PySide6.QtGui import QBrush, Qt

from voice_annotation_tool.project import Project, Annotation



class AnnotationListModel(QAbstractListModel):
    """Model that shows the annotations of a project."""

    ANNOTATION_ROLE = Qt.UserRole + 1

    def __init__(self, project: Project, parent=None):
        super().__init__(parent)
        self._data: Project = project

    def rowCount(self, parent=QModelIndex()) -> int:
        if self._data is None:
            return 0
        return len(self._data.annotations)

    def data(self, index: QModelIndex, role: int):
        if not index.isValid():
            return None
        if index.row() >= len(self._data.annotations):
            return None
        annotation = self._data.annotations[index.row()]
        match role:
            case Qt.DisplayRole:
                return annotation.path.name
            case Qt.BackgroundRole:
                return QBrush(Qt.GlobalColor.green) if annotation.modified else QBrush()
            case self.ANNOTATION_ROLE:
                return annotation
            case Qt.EditRole:
                return annotation.path.name
        return None

    def removeRow(self, row: int, parent=QModelIndex()) -> bool:
        if not self._data or row < 0 or row >= self.rowCount():
            return False
        self._data.annotations.remove(row)
        return True

    def flags(self, index) -> Qt.ItemFlags:
        return super().flags(index) | Qt.ItemIsEditable

    def index(self, row: int, column: int = 0, parent=QModelIndex()) -> QModelIndex:
        return self.createIndex(row, column)

    def roleNames(self) -> dict[int, str]:
        role_names = super.roleNames()
        role_names[self.ANNOTATION_ROLE] = "annotation"
        return role_names

    def headerData(self, section: int, orientation: Qt.Orientation, role: int) -> Any:
        if orientation == Qt.Horizontal:
            if role == Qt.DisplayRole:
                return "File Name"
            elif role == self.ANNOTATION_ROLE:
                return "Annotation"
        return None

    def setData(self, index: Union[QModelIndex, QPersistentModelIndex], value: Any, role: int = ...) -> bool:
        if role == Qt.EditRole:
            annotation: Annotation = self.data(index, self.ANNOTATION_ROLE)
            annotation.path = annotation.path.rename(annotation.path.with_name(value))
            return True
        return super().setData(index, value, role)
