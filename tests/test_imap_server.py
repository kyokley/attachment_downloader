import mock

from imap_server import ImapServer

class TestUniqueFilename(object):
    def setup_method(self):
        self.sha256_patcher = mock.patch('imap_server.hashlib.sha256')
        self.mock_sha256 = self.sha256_patcher.start()

        self.mock_sha256.return_value.hexdigest.return_value = 'e3b0c4'

    def teardown_method(self):
        self.sha256_patcher.stop()

    def test_tar_gz_no_from_addr(self):
        filename = 'test.tar.gz'

        expected = 'test_e3b0c4.tar.gz'
        actual = ImapServer._unique_filename(filename)

        assert expected == actual
        self.mock_sha256.return_value.update.assert_has_calls([mock.call(b''),
                                                               mock.call(b''),
                                                               ])
        self.mock_sha256.return_value.hexdigest.assert_called_once_with()

    def test_zip_no_from_addr(self):
        filename = 'test.zip'

        expected = 'test_e3b0c4.zip'
        actual = ImapServer._unique_filename(filename)

        assert expected == actual
        self.mock_sha256.return_value.update.assert_has_calls([mock.call(b''),
                                                               mock.call(b''),
                                                               ])
        self.mock_sha256.return_value.hexdigest.assert_called_once_with()

    def test_tar_gz_with_from_addr(self):
        filename = 'test.tar.gz'

        expected = 'test_e3b0c4.tar.gz'
        actual = ImapServer._unique_filename(filename, from_addr='test@example.com')

        assert expected == actual
        self.mock_sha256.return_value.update.assert_has_calls([mock.call(b'test@example.com'),
                                                               mock.call(b''),
                                                               ])
        self.mock_sha256.return_value.hexdigest.assert_called_once_with()

    def test_zip_with_from_addr(self):
        filename = 'test.zip'

        expected = 'test_e3b0c4.zip'
        actual = ImapServer._unique_filename(filename, from_addr='test@example.com')

        assert expected == actual
        self.mock_sha256.return_value.update.assert_has_calls([mock.call(b'test@example.com'),
                                                               mock.call(b''),
                                                               ])
        self.mock_sha256.return_value.hexdigest.assert_called_once_with()

    def test_tar_gz_with_date(self):
        filename = 'test.tar.gz'

        expected = 'test_e3b0c4.tar.gz'
        actual = ImapServer._unique_filename(filename, date='1-17-18')

        assert expected == actual
        self.mock_sha256.return_value.update.assert_has_calls([mock.call(b''),
                                                               mock.call(b'1-17-18'),
                                                               ])
        self.mock_sha256.return_value.hexdigest.assert_called_once_with()

    def test_zip_with_date(self):
        filename = 'test.zip'

        expected = 'test_e3b0c4.zip'
        actual = ImapServer._unique_filename(filename, date='1-17-18')

        assert expected == actual
        self.mock_sha256.return_value.update.assert_has_calls([mock.call(b''),
                                                               mock.call(b'1-17-18'),
                                                               ])
        self.mock_sha256.return_value.hexdigest.assert_called_once_with()

    def test_tar_gz_with_date_with_from_addr(self):
        filename = 'test.tar.gz'

        expected = 'test_e3b0c4.tar.gz'
        actual = ImapServer._unique_filename(filename, from_addr='test@example.com', date='1-17-18')

        assert expected == actual
        self.mock_sha256.return_value.update.assert_has_calls([mock.call(b'test@example.com'),
                                                               mock.call(b'1-17-18'),
                                                               ])
        self.mock_sha256.return_value.hexdigest.assert_called_once_with()

    def test_zip_with_date_with_from_addr(self):
        filename = 'test.zip'

        expected = 'test_e3b0c4.zip'
        actual = ImapServer._unique_filename(filename, from_addr='test@example.com', date='1-17-18')

        assert expected == actual
        self.mock_sha256.return_value.update.assert_has_calls([mock.call(b'test@example.com'),
                                                               mock.call(b'1-17-18'),
                                                               ])
        self.mock_sha256.return_value.hexdigest.assert_called_once_with()

    def test_encoded_filename_zip(self):
        filename = '=?UTF-8?b?dGVzdC56aXAK?='

        expected = 'test_e3b0c4.zip'
        actual = ImapServer._unique_filename(filename, from_addr='test@example.com', date='1-17-18')

        assert expected == actual
        self.mock_sha256.return_value.update.assert_has_calls([mock.call(b'test@example.com'),
                                                               mock.call(b'1-17-18'),
                                                               ])
        self.mock_sha256.return_value.hexdigest.assert_called_once_with()

    def test_encoded_filename_tar_gz(self):
        filename = '=?UTF-8?b?dGVzdC50YXIuZ3oK?='

        expected = 'test_e3b0c4.tar.gz'
        actual = ImapServer._unique_filename(filename, from_addr='test@example.com', date='1-17-18')

        assert expected == actual
        self.mock_sha256.return_value.update.assert_has_calls([mock.call(b'test@example.com'),
                                                               mock.call(b'1-17-18'),
                                                               ])
        self.mock_sha256.return_value.hexdigest.assert_called_once_with()
