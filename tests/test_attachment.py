from attachment import archive_extension

class TestArchiveExtension(object):
    def test_not_allowed_ext(self):
        filename = 'test.pdf'

        expected = None
        actual = archive_extension(filename)

        assert expected == actual

    def test_tar_gz(self):
        filename = 'test.tar.gz'

        expected = '.tar.gz'
        actual = archive_extension(filename)

        assert expected == actual

    def test_zip(self):
        filename = 'test.zip'

        expected = '.zip'
        actual = archive_extension(filename)

        assert expected == actual
