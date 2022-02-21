"""
The entrypoint for the annotation tool.
"""

import sys
from .application import Application


def main():
    app = Application(sys.argv)
    app.exec()


if __name__ == "__main__":
    main()
