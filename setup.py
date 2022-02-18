#!/usr/bin/env python3

import os, sys
from PySide6.scripts import pyside_tool
from setuptools import setup

args = sys.argv

# Convert .ui to ui.py files
ui_folder = "ui"
for filename in os.listdir(ui_folder):
    output = f"src/voice_annotation_tool/{os.path.splitext(filename)[0]}_ui.py"
    sys.argv = ["", "--from-imports", "-o", output, f"{ui_folder}/{filename}"]
    try:
        pyside_tool.uic()
    except SystemExit:
        pass

# Convert .ts to .qm files
translation_folder = "translations"
for filename in os.listdir(translation_folder):
    sys.argv = ["", os.path.join(translation_folder, filename)]
    try:
        pyside_tool.lrelease()
    except SystemExit:
        pass

# Generate resource python library.
sys.argv = ["", "resources.qrc", "-o", "src/voice_annotation_tool/resources_rc.py"]
try:
    pyside_tool.rcc()
except SystemExit:
    pass

sys.argv = args
setup()
