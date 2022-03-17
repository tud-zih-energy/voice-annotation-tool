from voice_annotation_tool.application import Application


def pytest_configure(config):
    # QT widgets need an application to work. There can only be one application
    # at a time.
    Application([])
