"""
The entrypoint for the annotation tool.
"""

import sys

from PySide6.QtCore import QLocale, QTranslator
from .application import Application


def main():
    app = Application(sys.argv)
    # Load the translation here so slots have the right locale when using tr.
    translator = QTranslator()
    translator.load(QLocale(), "translations/")
    app.installTranslator(translator)
    app.exec()


if __name__ == "__main__":
    main()
