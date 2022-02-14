from annotation_tool.application import Application

def test_start():
    assert Application(["", "-platform", "minimal"])
