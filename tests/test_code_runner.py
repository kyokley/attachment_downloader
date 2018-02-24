import mock
import pytest
from datetime import timedelta

from code_runner import (check_bandit,
                         check_triangle,
                         StopExecution,
                         run_all,
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
        expected = self.mock_run.return_value
        actual = check_triangle('test_path', executable='traversal.py', filename='test_filename', expected=[5])

        assert expected == actual
        self.mock_run.assert_called_once_with('test_path',
                                              'python3 traversal.py test_abspath/data/test_filename',
                                              executable='traversal.py',
                                              expected=[5],
                                              conversion_func=None)

class TestRunAll(object):
    def setup_method(self):
        self.loadConfig_patcher = mock.patch('code_runner.loadConfig')
        self.mock_loadConfig = self.loadConfig_patcher.start()

        self.listdir_patcher = mock.patch('code_runner.os.listdir')
        self.mock_listdir = self.listdir_patcher.start()

        self.check_bandit_patcher = mock.patch('code_runner.check_bandit')
        self.mock_check_bandit = self.check_bandit_patcher.start()

        self.check_triangle_patcher = mock.patch('code_runner.check_triangle')
        self.mock_check_triangle = self.check_triangle_patcher.start()

        self.TEST_TRIANGLES_patcher = mock.patch('code_runner.TEST_TRIANGLES',
                                                 [{'filename': 'test_file1',
                                                   'expected': [5]},
                                                   {'filename': 'test_file2',
                                                    'expected': [1, 2, 3]},
                                                   ])
        self.TEST_TRIANGLES_patcher.start()

        self.term_patcher = mock.patch('code_runner.term')
        self.mock_term = self.term_patcher.start()

        self.create_virtualenv_patcher = mock.patch('code_runner.create_virtualenv')
        self.mock_create_virtualenv = self.create_virtualenv_patcher.start()

        self.install_requirements_patcher = mock.patch('code_runner.install_requirements')
        self.mock_install_requirements = self.install_requirements_patcher.start()

        self.write_failures_to_file_patcher = mock.patch('code_runner.Result.write_failures_to_file')
        self.mock_write_failures_to_file = self.write_failures_to_file_patcher.start()

        self.mock_create_virtualenv.return_value = 'test_venv'

        self.mock_config = mock.MagicMock()
        self.mock_config.get.side_effect = ['test_local_dir',
                                            'test_executable',
                                            True, # STOP_ON_FIRST_FAILURE
                                            ]

        self.mock_loadConfig.return_value = self.mock_config

        self.mock_listdir.return_value = ['test_solution']

        self.mock_check_triangle.side_effect = ['', '']

    def teardown_method(self):
        self.loadConfig_patcher.stop()
        self.listdir_patcher.stop()
        self.check_bandit_patcher.stop()
        self.check_triangle_patcher.stop()
        self.TEST_TRIANGLES_patcher.stop()
        self.term_patcher.stop()
        self.create_virtualenv_patcher.stop()
        self.install_requirements_patcher.stop()
        self.write_failures_to_file_patcher.stop()

    # TODO: Add test for running without STOP_ON_FIRST_FAILURE
    def test_StopExecution_reraises(self):
        self.mock_check_triangle.side_effect = StopExecution('FAIL')
        with pytest.raises(StopExecution):
            run_all()

    def test_bandit_exceptions_continue(self):
        self.mock_check_bandit.side_effect = Exception('FAIL')

        actual = run_all()

        assert len(actual) == 1
        assert actual[0].name == 'test_solution'
        assert actual[0].failures == ['FAIL']
        self.mock_check_bandit.assert_called_once_with('test_local_dir/test_solution')
        self.mock_term.red.assert_any_call('Got exception running test_solution')
        assert not self.mock_check_triangle.called
        assert not self.mock_write_failures_to_file.called

    def test_check_triangle_exception_stop_on_first_failure(self):
        self.mock_check_triangle.side_effect = Exception('FAIL')

        actual = run_all()
        assert actual[0].failures == ['FAIL']

    def test_check_triangle_exception_no_stop_on_first_failure(self):
        self.mock_config.get.side_effect = ['test_local_dir',
                                            'test_executable',
                                            False,
                                            ]
        self.mock_check_triangle.side_effect = Exception('FAIL')

        actual = run_all()
        assert actual[0].failures == ['FAIL', 'FAIL']

    def test_run_all(self):
        actual = run_all()

        assert len(actual) == 1
        assert actual[0].name == 'test_solution'
        assert not actual[0].failures
        self.mock_check_bandit.assert_called_once_with('test_local_dir/test_solution')
        self.mock_create_virtualenv.assert_called_once_with('test_local_dir/test_solution')
        self.mock_install_requirements.assert_called_once_with('test_venv', 'test_local_dir/test_solution')
        self.mock_check_triangle.assert_has_calls([mock.call('test_local_dir/test_solution',
                                                             executable='test_executable',
                                                             filename='test_file1',
                                                             expected=[5],
                                                             python_executable='test_venv/bin/python3'),
                                                   mock.call('test_local_dir/test_solution',
                                                             executable='test_executable',
                                                             filename='test_file2',
                                                             expected=[1, 2, 3],
                                                             python_executable='test_venv/bin/python3'),
                                                   ])
        assert not self.mock_write_failures_to_file.called

