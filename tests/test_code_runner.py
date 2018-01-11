import mock
import pytest

from code_runner import (check_bandit,
                         check_triangle,
                         StopExecution,
                         )

class TestCheckBandit(object):
    def setup_method(self):
        self.BANDIT_EXECUTABLE_patcher = mock.patch('code_runner.BANDIT_EXECUTABLE', '/path/to/bandit')
        self.BANDIT_EXECUTABLE_patcher.start()

        self.run_patcher = mock.patch('code_runner.run')
        self.mock_run = self.run_patcher.start()

    def teardown_method(self):
        self.BANDIT_EXECUTABLE_patcher.stop()
        self.run_patcher.stop()

    def test_check(self):
        expected = None
        actual = check_bandit('test_path')

        assert expected == actual
        self.mock_run.assert_called_once_with('test_path',
                                              '/path/to/bandit -r test_path',
                                              suppress_output=True)

class TestCheckTriangle(object):
    def setup_method(self):
        self.run_patcher = mock.patch('code_runner.run')
        self.mock_run = self.run_patcher.start()

        self.abspath_patcher = mock.patch('code_runner.os.path.abspath')
        self.mock_abspath = self.abspath_patcher.start()
        self.mock_abspath.return_value = 'test_abspath'

    def teardown_method(self):
        self.run_patcher.stop()
        self.abspath_patcher.stop()

    def test_no_filename_raises(self):
        with pytest.raises(StopExecution):
            check_triangle('test_path', expected=5)

    def test_no_expected_raises(self):
        with pytest.raises(StopExecution):
            check_triangle('test_path', filename='test_filename')

    def test_check(self):
        expected = None
        actual = check_triangle('test_path', filename='test_filename', expected=[5])

        assert expected == actual
        self.mock_run.assert_called_once_with('test_path',
                                              'python3 traversal.py test_abspath/data/test_filename',
                                              expected=[5],
                                              conversion_func=None)
