"""
The application that handles the initial program state and initialization of
the GUI.
"""

import sys
from pathlib import Path
from PySide6.QtCore import QCommandLineParser, QLocale, QStandardPaths, QTranslator
from PySide6.QtGui import QScreen
from PySide6.QtWidgets import QApplication
from .main_window import MainWindow
from .project import Project

def get_data_dir():
    """Returns the directory where application data is stored."""
    return Path(QStandardPaths.standardLocations(
        QStandardPaths.AppDataLocation)[0]).joinpath("annotation_tool")

def get_settings_file():
    """
    Returns the json file which stores a list of recently used projects and the
    shortcuts.
    """
    return get_data_dir().joinpath("settings.json")

class Application(QApplication):
    def __init__(self, args) -> None:
        super().__init__(args)
        parser = QCommandLineParser()
        parser.setApplicationDescription(
                self.tr("Utility to annotate short voice samples"))
        parser.addPositionalArgument("project", self.tr("Project file to open."))
        parser.addHelpOption()
        parser.addVersionOption()
        parser.process(self)

        translator = QTranslator()
        translator.load(QLocale(), 'translations/')
        self.installTranslator(translator)

        main_window = MainWindow()
        print(get_settings_file())
        main_window.load_settings(get_settings_file())
        main_window.actionAboutQT.triggered.connect(self.aboutQt)

        center = QScreen.availableGeometry(QApplication.primaryScreen()).center()
        geo = main_window.frameGeometry()
        geo.moveCenter(center)
        main_window.move(geo.topLeft())

        sys.excepthook = main_window.excepthook

        args = parser.positionalArguments()
        if len(args) > 0:
            main_window.project_opened(Project(args[0]))

        main_window.show()
