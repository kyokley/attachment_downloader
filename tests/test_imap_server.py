import mock

from imap_server import ImapServer

class TestUniqueFilename(object):
    def setup_method(self):
        self.id_gen_patcher = mock.patch('imap_server.id_gen')
        self.mock_id_gen = self.id_gen_patcher.start()

        self.mock_id_gen.__next__.return_value = 100

    def teardown_method(self):
        self.id_gen_patcher.stop()

    def test_tar_gz_no_from_addr(self):
        filename = 'test.tar.gz'

        expected = 'test_100.tar.gz'
        actual = ImapServer._unique_filename(filename)

        assert expected == actual

    def test_zip_no_from_addr(self):
        filename = 'test.zip'

        expected = 'test_100.zip'
        actual = ImapServer._unique_filename(filename)

        assert expected == actual

    def test_tar_gz_with_from_addr(self):
        filename = 'test.tar.gz'

        expected = 'test_100.tar.gz'
        actual = ImapServer._unique_filename(filename)

        assert expected == actual

    def test_zip_with_from_addr(self):
        filename = 'test.zip'

        expected = 'test_100.zip'
        actual = ImapServer._unique_filename(filename)

        assert expected == actual
