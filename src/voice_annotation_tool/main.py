"""
The entrypoint for the annotation tool.
"""

import ctypes
import sys

from PySide6.QtCore import QLocale, QTranslator
from voice_annotation_tool.application import Application


def main():
    app = Application(sys.argv)
    try:
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(
            "TUDresden.VoiceAnnotationTool.Python.Release"
        )
    except AttributeError:
        pass
    # Load the translation here so slots have the right locale when using tr.
    translator = QTranslator()
    translator.load(QLocale(), "translations/")
    app.installTranslator(translator)
    app.exec()


if __name__ == "__main__":
    main()
