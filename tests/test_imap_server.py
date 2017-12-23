import mock

from imap_server import ImapServer

class TestUniqueFilename(object):
    def setup_method(self):
        self.urandom_patcher = mock.patch('imap_server.os.urandom')
        self.mock_urandom = self.urandom_patcher.start()

        self.mock_urandom.return_value = bytes.fromhex('c001af')

        self.sha256_patcher = mock.patch('imap_server.hashlib.sha256')
        self.mock_sha256 = self.sha256_patcher.start()
        self.mock_sha256.return_value.hexdigest.return_value = 'b0771e'

    def teardown_method(self):
        self.urandom_patcher.stop()
        self.sha256_patcher.stop()

    def test_tar_gz_no_from_addr(self):
        filename = 'test.tar.gz'

        expected = 'test_c001af.tar.gz'
        actual = ImapServer._unique_filename(filename)

        assert expected == actual
        assert not self.mock_sha256.called

    def test_zip_no_from_addr(self):
        filename = 'test.zip'

        expected = 'test_c001af.zip'
        actual = ImapServer._unique_filename(filename)

        assert expected == actual
        assert not self.mock_sha256.called

    def test_tar_gz_with_from_addr(self):
        filename = 'test.tar.gz'

        expected = 'test_b0771e.tar.gz'
        actual = ImapServer._unique_filename(filename, from_addr='from@example.com')

        assert expected == actual
        self.mock_sha256.assert_called_once_with(b'from@example.com')

    def test_zip_with_from_addr(self):
        filename = 'test.zip'

        expected = 'test_b0771e.zip'
        actual = ImapServer._unique_filename(filename, from_addr='from@example.com')

        assert expected == actual
        self.mock_sha256.assert_called_once_with(b'from@example.com')
