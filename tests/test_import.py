from importlib.metadata import version


def test_import_wirestead():
    import wirestead

    assert wirestead is not None
    assert wirestead.__version__ == version("wirestead")
