def test_import_wirestead():
    import wirestead

    assert wirestead is not None
    assert wirestead.__version__ == "0.9.0"
