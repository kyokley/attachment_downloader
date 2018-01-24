from __future__ import print_function

import mock

from main import main

class TestMain(object):
    def setup_method(self):
        self.loadConfig_patcher = mock.patch('main.loadConfig')
        self.mock_loadConfig = self.loadConfig_patcher.start()

        self.getpass_patcher = mock.patch('main.getpass.getpass')
        self.mock_getpass = self.getpass_patcher.start()

        self.ImapClient_patcher = mock.patch('main.ImapClient')
        self.mock_ImapClient = self.ImapClient_patcher.start()

        self.input_patcher = mock.patch('main.input')
        self.mock_input = self.input_patcher.start()

        self.decompress_archives_patcher = mock.patch('main.decompress_archives')
        self.mock_decompress_archives = self.decompress_archives_patcher.start()

        self.output_results_to_stdout_patcher = mock.patch('main.output_results_to_stdout')
        self.mock_output_results_to_stdout = self.output_results_to_stdout_patcher.start()

        self.output_results_to_file_patcher = mock.patch('main.output_results_to_file')
        self.mock_output_results_to_file = self.output_results_to_file_patcher.start()

        self.run_all_patcher = mock.patch('main.run_all')
        self.mock_run_all = self.run_all_patcher.start()

        self.mock_config = mock.MagicMock()
        self.mock_config.get.side_effect = ['test_host',
                                            'test_username',
                                            'test_remote_folder',
                                            'test_results_file',
                                            'test_local_directory',
                                            ]
        self.mock_loadConfig.return_value = self.mock_config
        self.mock_getpass.return_value = 'test_password'

    def teardown_method(self):
        self.loadConfig_patcher.stop()
        self.ImapClient_patcher.stop()
        self.getpass_patcher.stop()
        self.input_patcher.stop()
        self.output_results_to_stdout_patcher.stop()
        self.output_results_to_file_patcher.stop()
        self.run_all_patcher.stop()
        self.decompress_archives_patcher.stop()

    def test_download_only(self):
        self.mock_input.return_value = 'n'

        expected = None
        actual = main()

        assert expected == actual
        self.mock_ImapClient.assert_called_once_with('test_host',
                                                     'test_username',
                                                     'test_password',
                                                     folder='test_remote_folder',
                                                     )
        self.mock_ImapClient.return_value.download_attachements.assert_called_once_with(directory='test_local_directory')
        self.mock_ImapClient.return_value.logout.assert_called_once_with()
        self.mock_decompress_archives.assert_called_once_with('test_local_directory')

        assert not self.mock_run_all.called
        assert not self.mock_output_results_to_stdout.called
        assert not self.mock_output_results_to_file.called

    def test_download_and_run_code(self):
        self.mock_input.return_value = 'y'

        expected = None
        actual = main()

        assert expected == actual
        self.mock_ImapClient.assert_called_once_with('test_host',
                                                     'test_username',
                                                     'test_password',
                                                     folder='test_remote_folder',
                                                     )
        self.mock_ImapClient.return_value.download_attachements.assert_called_once_with(directory='test_local_directory')
        self.mock_ImapClient.return_value.logout.assert_called_once_with()
        self.mock_decompress_archives.assert_called_once_with('test_local_directory')

        self.mock_run_all.assert_called_once_with()
        self.mock_output_results_to_stdout.assert_called_once_with(self.mock_run_all.return_value)
        self.mock_output_results_to_file.assert_called_once_with('test_results_file',
                                                                 self.mock_run_all.return_value)

    def test_download_and_run_no_output_file(self):
        self.mock_config.get.side_effect = ['test_host',
                                            'test_username',
                                            'test_remote_folder',
                                            '',
                                            'test_local_directory',
                                            ]
        self.mock_input.return_value = 'y'

        expected = None
        actual = main()

        assert expected == actual
        self.mock_ImapClient.assert_called_once_with('test_host',
                                                     'test_username',
                                                     'test_password',
                                                     folder='test_remote_folder',
                                                     )
        self.mock_ImapClient.return_value.download_attachements.assert_called_once_with(directory='test_local_directory')
        self.mock_ImapClient.return_value.logout.assert_called_once_with()
        self.mock_decompress_archives.assert_called_once_with('test_local_directory')

        self.mock_run_all.assert_called_once_with()
        self.mock_output_results_to_stdout.assert_called_once_with(self.mock_run_all.return_value)
        assert not self.mock_output_results_to_file.called
