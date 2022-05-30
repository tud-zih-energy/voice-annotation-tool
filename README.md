# Voice Annotation Tool

This program allows annotation of a list of audio files and exporting it in a similar format as [Mozilla's CommonVoice dataset](https://commonvoice.mozilla.org).

## Installation

Install the package system-wide:

```bash
pip install voice-annotation-tool
```

## Usage

Launch the program:

```bash
voice-annotation-tool
```

To get started, create a project by providing the folder with the audio samples and the location of the .tsv file in which the annotations will be stored.

The tsv file is exported when the project is saved. Samples added to the audio folder after the project is created are added when the project is opened.

For a more detailed overview of the interface and API please refer to the [documentation](https://voice-annotation-tool.readthedocs.io/en/latest/).

## Screenshots

![opened_project](images/screenshot.png) 

## Translation

To generate the translation file, run the following command:

```bash
pyside6-lupdate src/voice_annotation_tool/* . -ts translations/<LANGUAGE>.ts
```

Then open the file in QT Linguist and update the missing fields. After reinstalling the package the translation is updated.
