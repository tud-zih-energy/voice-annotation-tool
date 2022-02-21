from PySide6 import QtWidgets


def pytest_configure(config):
    # QT widgets need an application to work. There can only be one application
    # at a time.
    QtWidgets.QApplication([])
