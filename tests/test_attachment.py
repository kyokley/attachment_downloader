from attachment import (archive_extension,
                        archive_basename,
                        _archive_filter,
                        )

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

class TestArchiveBasename(object):
    def test_not_allowed_ext(self):
        filename = 'test.pdf'

        expected = None
        actual = archive_basename(filename)

        assert expected == actual

    def test_tar_gz(self):
        filename = 'test.tar.gz'

        expected = 'test'
        actual = archive_basename(filename)

        assert expected == actual

    def test_zip(self):
        filename = 'test.zip'

        expected = 'test'
        actual = archive_basename(filename)

        assert expected == actual

class TestArchiveFilter(object):
    def test_only_return_allowed_extensions(self):
        test_tar_gz = 'test.tar.gz'
        test_zip = 'test.zip'
        test_pdf = 'test.pdf'
        test_doc = 'test.doc'
        test_txt = 'test.txt'
        test_py = 'test.py'
        test_pyc = 'test.pyc'

        expected = [test_txt, test_py]
        actual = [x for x in _archive_filter([test_tar_gz,
                                              test_zip,
                                              test_pdf,
                                              test_doc,
                                              test_txt,
                                              test_py,
                                              test_pyc,
                                              ], lambda y: y)]
        assert expected == actual

    def test_double_dot_not_allowed(self):
        test_tar_gz = './../test.tr.gz'
        test_zip = './../test.zip'

        expected = []
        actual = [x for x in _archive_filter([test_tar_gz,
                                              test_zip,
                                              ], lambda y: y)]

        assert expected == actual
