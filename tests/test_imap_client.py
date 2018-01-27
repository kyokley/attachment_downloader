import mock

from imap_client import ImapClient

class TestUniqueFilename(object):
    def setup_method(self):
        self.sha256_patcher = mock.patch('imap_client.hashlib.sha256')
        self.mock_sha256 = self.sha256_patcher.start()

        self.mock_sha256.return_value.hexdigest.return_value = 'e3b0c4'

    def teardown_method(self):
        self.sha256_patcher.stop()

    def test_tar_gz_no_from_addr(self):
        filename = 'test.tar.gz'

        expected = 'test_e3b0c4.tar.gz'
        actual = ImapClient._unique_filename(filename)

        assert expected == actual
        self.mock_sha256.return_value.update.assert_has_calls([mock.call(b''),
                                                               mock.call(b''),
                                                               ])
        self.mock_sha256.return_value.hexdigest.assert_called_once_with()

    def test_zip_no_from_addr(self):
        filename = 'test.zip'

        expected = 'test_e3b0c4.zip'
        actual = ImapClient._unique_filename(filename)

        assert expected == actual
        self.mock_sha256.return_value.update.assert_has_calls([mock.call(b''),
                                                               mock.call(b''),
                                                               ])
        self.mock_sha256.return_value.hexdigest.assert_called_once_with()

    def test_tar_gz_with_from_addr(self):
        filename = 'test.tar.gz'

        expected = 'test_e3b0c4.tar.gz'
        actual = ImapClient._unique_filename(filename, from_addr='test@example.com')

        assert expected == actual
        self.mock_sha256.return_value.update.assert_has_calls([mock.call(b'test@example.com'),
                                                               mock.call(b''),
                                                               ])
        self.mock_sha256.return_value.hexdigest.assert_called_once_with()

    def test_zip_with_from_addr(self):
        filename = 'test.zip'

        expected = 'test_e3b0c4.zip'
        actual = ImapClient._unique_filename(filename, from_addr='test@example.com')

        assert expected == actual
        self.mock_sha256.return_value.update.assert_has_calls([mock.call(b'test@example.com'),
                                                               mock.call(b''),
                                                               ])
        self.mock_sha256.return_value.hexdigest.assert_called_once_with()

    def test_tar_gz_with_date(self):
        filename = 'test.tar.gz'

        expected = 'test_e3b0c4.tar.gz'
        actual = ImapClient._unique_filename(filename, date='1-17-18')

        assert expected == actual
        self.mock_sha256.return_value.update.assert_has_calls([mock.call(b''),
                                                               mock.call(b'1-17-18'),
                                                               ])
        self.mock_sha256.return_value.hexdigest.assert_called_once_with()

    def test_zip_with_date(self):
        filename = 'test.zip'

        expected = 'test_e3b0c4.zip'
        actual = ImapClient._unique_filename(filename, date='1-17-18')

        assert expected == actual
        self.mock_sha256.return_value.update.assert_has_calls([mock.call(b''),
                                                               mock.call(b'1-17-18'),
                                                               ])
        self.mock_sha256.return_value.hexdigest.assert_called_once_with()

    def test_tar_gz_with_date_with_from_addr(self):
        filename = 'test.tar.gz'

        expected = 'test_e3b0c4.tar.gz'
        actual = ImapClient._unique_filename(filename, from_addr='test@example.com', date='1-17-18')

        assert expected == actual
        self.mock_sha256.return_value.update.assert_has_calls([mock.call(b'test@example.com'),
                                                               mock.call(b'1-17-18'),
                                                               ])
        self.mock_sha256.return_value.hexdigest.assert_called_once_with()

    def test_zip_with_date_with_from_addr(self):
        filename = 'test.zip'

        expected = 'test_e3b0c4.zip'
        actual = ImapClient._unique_filename(filename, from_addr='test@example.com', date='1-17-18')

        assert expected == actual
        self.mock_sha256.return_value.update.assert_has_calls([mock.call(b'test@example.com'),
                                                               mock.call(b'1-17-18'),
                                                               ])
        self.mock_sha256.return_value.hexdigest.assert_called_once_with()

    def test_encoded_filename_zip(self):
        filename = '=?UTF-8?b?dGVzdC56aXAK?='

        expected = 'test_e3b0c4.zip'
        actual = ImapClient._unique_filename(filename, from_addr='test@example.com', date='1-17-18')

        assert expected == actual
        self.mock_sha256.return_value.update.assert_has_calls([mock.call(b'test@example.com'),
                                                               mock.call(b'1-17-18'),
                                                               ])
        self.mock_sha256.return_value.hexdigest.assert_called_once_with()

    def test_encoded_filename_tar_gz(self):
        filename = '=?UTF-8?b?dGVzdC50YXIuZ3oK?='

        expected = 'test_e3b0c4.tar.gz'
        actual = ImapClient._unique_filename(filename, from_addr='test@example.com', date='1-17-18')

        assert expected == actual
        self.mock_sha256.return_value.update.assert_has_calls([mock.call(b'test@example.com'),
                                                               mock.call(b'1-17-18'),
                                                               ])
        self.mock_sha256.return_value.hexdigest.assert_called_once_with()

class TestGetEmailAddresses(object):
    def setup_method(self):
        self.imap4_patcher = mock.patch('imap_client.IMAP4')
        self.mock_imap4 = self.imap4_patcher.start()

        self.imap4_ssl_patcher = mock.patch('imap_client.IMAP4_SSL')
        self.mock_imap4_ssl = self.imap4_ssl_patcher.start()

        self.fetch_messages_patcher = mock.patch('imap_client.ImapClient.fetch_messages')
        self.mock_fetch_messages = self.fetch_messages_patcher.start()

        self._login_patcher = mock.patch('imap_client.ImapClient._login')
        self.mock_login = self._login_patcher.start()

        self._select_patcher = mock.patch('imap_client.ImapClient._select')
        self.mock_select = self._select_patcher.start()

        self.imap_client = ImapClient('test_host',
                                      'test_username',
                                      'test_password',
                                      )

    def teardown_method(self):
        self.fetch_messages_patcher.stop()
        self.imap4_patcher.stop()
        self.imap4_ssl_patcher.stop()
        self._login_patcher.stop()
        self._select_patcher.stop()

    def test_get_email_addresses(self):
        self.mock_fetch_messages.return_value = [{'From': 'John Doe <john.doe@example.com>'},
                                                 {'From': 'asdf@example.com <asdf@example.com>'},
                                                 {'From': '<john.doe@example.com>'},
                                                 ]

        expected = set(['john.doe@example.com',
                        'asdf@example.com'])
        actual = self.imap_client.get_email_addresses()

        assert expected == actual
