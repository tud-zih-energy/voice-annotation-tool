import sys
from pathlib import Path
import traceback
from PySide6.QtCore import QCommandLineParser, QLocale, QStandardPaths, QTranslator
from PySide6.QtWidgets import QApplication, QErrorMessage
from .main_window import MainWindow


def get_data_dir() -> Path:
    """Returns the directory where application data is stored."""
    data_dirs = QStandardPaths.standardLocations(QStandardPaths.AppLocalDataLocation)
    data_dir = Path(data_dirs[0]).parent.joinpath("voice-annotation-tool")
    if not data_dir.exists():
        data_dir.mkdir(parents=True)
    return data_dir


def get_settings_file() -> Path:
    """Returns the json file which stores a list of recently used
    projects and the shortcuts.
    """
    return get_data_dir().joinpath("settings.json")


class Application(QApplication):
    """The QApplication instance that handles the initial program state,
    command line arguments, translation, error handling and
    initialization of the GUI.
    """

    def __init__(self, args) -> None:
        super().__init__(args)
        parser = QCommandLineParser()
        parser.setApplicationDescription(
            self.tr("Utility to annotate short voice samples")
        )
        parser.addPositionalArgument("project", self.tr("Project file to open."))
        parser.addHelpOption()
        parser.addVersionOption()
        parser.process(self)

        translator = QTranslator()
        translator.load(QLocale(), "translations/")
        self.installTranslator(translator)

        self.main_window = MainWindow()
        self.main_window.settings_changed.connect(self.save_settings)
        settings_file = get_settings_file()
        if settings_file.is_file():
            with open(settings_file) as file:
                self.main_window.load_settings(file)
        self.save_settings()
        self.main_window.actionAboutQT.triggered.connect(self.aboutQt)

        sys.excepthook = self.excepthook
        self.error_dialog = None

        args = parser.positionalArguments()
        if len(args) > 0:
            path = Path(args[0])
            if not path.is_file():
                print("Project file not found.")
                exit(2) # No such file or directory.
            self.main_window.load_project_from_file(path)

        self.main_window.show()

    def save_settings(self):
        with open(get_settings_file(), "w") as file:
            self.main_window.save_settings(file)

    def excepthook(self, exc_type, exc_value, exc_tb):
        """Method used to show occured exception in a dialog instead of
        crashing the program."""
        if self.error_dialog:
            # Only show one error message to prevent dialog spam.
            self.error_dialog.close()
        self.error_dialog = QErrorMessage(self.main_window)
        message = "\n".join(traceback.format_exception(exc_type, exc_value, exc_tb))
        print(message)
        self.error_dialog.showMessage(message, "exception")
