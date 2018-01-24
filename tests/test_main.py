from __future__ import print_function

import mock

from main import main

class TestMain(object):
    def setup_method(self):
        self.loadConfig_patcher = mock.patch('main.loadConfig')
        self.mock_loadConfig = self.loadConfig_patcher.start()

        self.getpass_patcher = mock.patch('main.getpass.getpass')
        self.mock_getpass = self.getpass_patcher.start()

        self.ImapServer_patcher = mock.patch('main.ImapServer')
        self.mock_ImapServer = self.ImapServer_patcher.start()

        self.input_patcher = mock.patch('main.input')
        self.mock_input = self.input_patcher.start()

        self.output_results_to_stdout_patcher = mock.patch('main.output_results_to_stdout')
        self.mock_output_results_to_stdout = self.output_results_to_stdout_patcher.start()

        self.output_results_to_file_patcher = mock.patch('main.output_results_to_file')
        self.mock_output_results_to_file = self.output_results_to_file_patcher.start()

    def teardown_method(self):
        self.loadConfig_patcher.stop()
        self.ImapServer_patcher.stop()
        self.getpass_patcher.stop()
        self.input_patcher.stop()
        self.output_results_to_stdout_patcher.stop()
        self.output_results_to_file_patcher.stop()

    def test_download_only(self):
        assert False

    def test_download_and_run_code(self):
        assert False
