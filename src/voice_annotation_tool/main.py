"""
The entrypoint for the annotation tool.
"""

import sys

from PySide6.QtCore import QLocale, QSize, QTranslator
from PySide6.QtGui import QIcon
from voice_annotation_tool.application import Application


def main():
    app = Application(sys.argv)
    try:
        import ctypes
        myappid = u'mycompany.myproduct.subproduct.version' # arbitrary string
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
    except Exception:
        pass
    # Load the translation here so slots have the right locale when using tr.
    translator = QTranslator()
    translator.load(QLocale(), "translations/")
    app.installTranslator(translator)
    app.exec()


if __name__ == "__main__":
    main()
