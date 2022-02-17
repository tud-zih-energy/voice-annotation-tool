from typing import Any
from PySide6.QtCore import QAbstractListModel, QModelIndex
from PySide6.QtGui import QBrush, Qt

from .project import Project

ANNOTATION_ROLE = Qt.UserRole + 1

class AnnotationListModel(QAbstractListModel):
    """Model that shows the annotations of a project."""

    def __init__(self, project : Project, parent=None):
        super().__init__(parent)
        self._data: Project = project
    
    def rowCount(self, parent=QModelIndex()) -> int:
        if self._data is None:
            return 0
        return len(self._data.annotations)

    def data(self, index: QModelIndex, role: int) -> Any:
        if not index.isValid():
            return None
        annotation = self._data.annotations[index.row()]
        if role == Qt.DisplayRole:
            return annotation.path
        elif role == Qt.BackgroundRole:
            return QBrush(Qt.GlobalColor.green) if annotation.modified else QBrush()
        elif role == ANNOTATION_ROLE:
            return annotation
        return None

    def removeRow(self, row: int, parent=QModelIndex()) -> bool:
        if not self._data or row < 0 or row >= self.rowCount():
            return False
        self._data.annotations.remove(row)
        return True

    def index(self, row: int, column: int = 0, parent=QModelIndex()) -> QModelIndex:
        return self.createIndex(row, column)

