"""
The entrypoint for the annotation tool.
"""

import sys, os
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QStandardPaths, QTranslator, QLocale, QCommandLineParser
from PySide6.QtGui import QScreen
from .main_window import MainWindow
from .project import Project

def get_data_dir():
    """Returns the directory where application data is stored."""
    return os.path.join(os.path.dirname(QStandardPaths.standardLocations(
        QStandardPaths.AppDataLocation)[0]), "annotation_tool")

def get_settings_file():
    """
    Returns the json file which stores a list of recently used projects and the
    shortcuts.
    """
    return os.path.join(get_data_dir(), "settings.json")

def main():
    app = QApplication(sys.argv)

    parser = QCommandLineParser()
    parser.setApplicationDescription(
            app.tr("Utility to annotate short voice samples"))
    parser.addPositionalArgument("project", app.tr("Project file to open."))
    parser.addHelpOption()
    parser.addVersionOption()
    parser.process(app)

    translator = QTranslator()
    translator.load(QLocale(), 'translations/')
    app.installTranslator(translator)

    main_window = MainWindow()
    main_window.load_settings(get_settings_file())
    main_window.actionAboutQT.triggered.connect(app.aboutQt)

    center = QScreen.availableGeometry(QApplication.primaryScreen()).center()
    geo = main_window.frameGeometry()
    geo.moveCenter(center)
    main_window.move(geo.topLeft())

    sys.excepthook = main_window.excepthook

    args = parser.positionalArguments()
    if len(args) > 0:
        main_window.project_opened(Project(args[0]))

    main_window.show()
    app.exec()

if __name__ == "__main__":
    main()
