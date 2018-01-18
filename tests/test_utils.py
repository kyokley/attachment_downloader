import mock
import pytest
import subprocess
import os

from utils import (assess_answer,
                   run,
                   create_virtualenv,
                   install_requirements,
                   )

class TestAssessAnswer(object):
    def test_expected_not_iterable(self):
        expected = None
        actual = assess_answer(5, '5\n', conversion_func=int)

        assert expected == actual

    def test_expected_is_actual(self):
        expected = None
        actual = assess_answer([5], '5\n', conversion_func=int)

        assert expected == actual

    def test_expected_is_actual_long_answer(self):
        expected = None
        actual = assess_answer([1, 2, 3, 4, 5], '1\n2\n3\n4\n5\n', conversion_func=int)

        assert expected == actual

    def test_actual_too_long(self):
        expected = 'Extra values provided in answer'
        actual = assess_answer([1, 2, 3, 4, 5], '1\n2\n3\n4\n5\n6\n7\n8\n', conversion_func=int)

        assert expected == actual

    def test_actual_too_short(self):
        expected = 'Not enough values provided in answer'
        actual = assess_answer([1, 2, 3, 4, 5], '1\n2\n3\n', conversion_func=int)

        assert expected == actual

    def test_expected_actual_mismatch(self):
        expected = "Value at index 3 does not match\nExpected: 4 (<class 'int'>) Actual: 3 (<class 'int'>)"
        actual = assess_answer([1, 2, 3, 4, 5], '1\n2\n3\n3\n4\n', conversion_func=int)

        assert expected == actual

    def test_no_conversion_func(self):
        expected = None
        actual = assess_answer(['1', '2', '3', '4', '5'], '1\n2\n3\n4\n5\n')

        assert expected == actual

class TestRun(object):
    def setup_method(self):
        self.run_patcher = mock.patch('utils.subprocess.run', autospec=True)
        self.mock_run = self.run_patcher.start()

        self.assess_answer_patcher = mock.patch('utils.assess_answer', autospec=True)
        self.mock_assess_answer = self.assess_answer_patcher.start()

        self.TIMEOUT_patcher = mock.patch('utils.TIMEOUT', 60)
        self.TIMEOUT_patcher.start()

        self.term_patcher = mock.patch('utils.term')
        self.mock_term = self.term_patcher.start()

        self.print_patcher = mock.patch('utils.print')
        self.mock_print = self.print_patcher.start()

        self.walk_patcher = mock.patch('utils.os.walk')
        self.mock_walk = self.walk_patcher.start()

    def teardown_method(self):
        self.run_patcher.stop()
        self.assess_answer_patcher.stop()
        self.TIMEOUT_patcher.stop()
        self.term_patcher.stop()
        self.print_patcher.stop()
        self.walk_patcher.stop()

    def test_got_expected_answer(self):
        self.mock_assess_answer.return_value = None

        expected = ''
        actual = run('test_directory', 'python main.py', expected='test_val')

        assert expected == actual
        self.mock_run.assert_called_once_with(['python', 'main.py'],
                                              stdout=subprocess.PIPE,
                                              stderr=subprocess.STDOUT,
                                              cwd='test_directory',
                                              timeout=60,
                                              check=True,
                                              encoding='utf-8')
        self.mock_assess_answer.assert_called_once_with('test_val',
                                                        self.mock_run.return_value.stdout,
                                                        conversion_func=None)
        self.mock_term.green.assert_called_once_with('GOOD: python main.py')
        assert not self.mock_term.red.called

    def test_got_incorrect_answer(self):
        self.mock_assess_answer.return_value = 'Got an incorrect answer'

        expected = 'Got an incorrect answer'
        actual = run('test_directory', 'python main.py', expected='test_val')

        assert expected == actual
        self.mock_run.assert_called_once_with(['python', 'main.py'],
                                              stdout=subprocess.PIPE,
                                              stderr=subprocess.STDOUT,
                                              cwd='test_directory',
                                              timeout=60,
                                              check=True,
                                              encoding='utf-8')
        self.mock_assess_answer.assert_called_once_with('test_val',
                                                        self.mock_run.return_value.stdout,
                                                        conversion_func=None)
        assert not self.mock_term.green.called

        # I wouldn't normally use assert_any_call but I couldn't figure out how to handle the
        # implicit call to __str__ on the term object
        self.mock_term.red.assert_any_call('FAILED: python main.py')
        self.mock_term.red.assert_any_call('Got:')
        self.mock_term.red.assert_any_call('Got an incorrect answer')

    def test_no_expected_good(self):
        expected = ''
        actual = run('test_directory', 'python main.py')

        assert expected == actual
        self.mock_run.assert_called_once_with(['python', 'main.py'],
                                              stdout=subprocess.PIPE,
                                              stderr=subprocess.STDOUT,
                                              cwd='test_directory',
                                              timeout=60,
                                              check=True,
                                              encoding='utf-8')
        self.mock_print.assert_called_once_with(self.mock_run.return_value.stdout)
        assert not self.mock_assess_answer.called
        assert not self.mock_term.green.called
        assert not self.mock_term.red.called

    def test_no_expected_bad(self):
        self.mock_run.side_effect = subprocess.CalledProcessError(1, 'python main.py')
        with pytest.raises(subprocess.CalledProcessError):
            run('test_directory', 'python main.py')

        self.mock_run.assert_called_once_with(['python', 'main.py'],
                                              stdout=subprocess.PIPE,
                                              stderr=subprocess.STDOUT,
                                              cwd='test_directory',
                                              timeout=60,
                                              check=True,
                                              encoding='utf-8')
        assert not self.mock_print.called
        assert not self.mock_assess_answer.called
        assert not self.mock_term.green.called
        assert not self.mock_term.red.called

    def test_no_expected_suppress_output(self):
        expected = ''
        actual = run('test_directory', 'python main.py', suppress_output=True)

        assert expected == actual
        self.mock_run.assert_called_once_with(['python', 'main.py'],
                                              stdout=subprocess.PIPE,
                                              stderr=subprocess.STDOUT,
                                              cwd='test_directory',
                                              timeout=60,
                                              check=True,
                                              encoding='utf-8')
        assert not self.mock_assess_answer.called
        self.mock_term.green.assert_called_once_with('GOOD: python main.py')
        assert not self.mock_term.red.called

    def test_timeout_triggered(self):
        self.mock_run.side_effect = subprocess.TimeoutExpired('python main.py', 60)
        with pytest.raises(subprocess.TimeoutExpired):
            run('test_directory', 'python main.py')

        self.mock_run.assert_called_once_with(['python', 'main.py'],
                                              stdout=subprocess.PIPE,
                                              stderr=subprocess.STDOUT,
                                              cwd='test_directory',
                                              timeout=60,
                                              check=True,
                                              encoding='utf-8')
        assert not self.mock_print.called
        assert not self.mock_assess_answer.called
        assert not self.mock_term.green.called
        assert not self.mock_term.red.called

    def test_executable_modifies_directory(self):
        self.mock_walk.return_value = [('root',
                                        ['dir1', 'dir2'],
                                        ['test1.py', 'main.py', 'test2.py'],
                                        )]
        self.mock_assess_answer.return_value = None

        expected = ''
        actual = run('test_directory', 'python main.py', expected='test_val', executable='main.py')

        assert expected == actual
        self.mock_run.assert_called_once_with(['python', 'main.py'],
                                              stdout=subprocess.PIPE,
                                              stderr=subprocess.STDOUT,
                                              cwd='root',
                                              timeout=60,
                                              check=True,
                                              encoding='utf-8')
        self.mock_assess_answer.assert_called_once_with('test_val',
                                                        self.mock_run.return_value.stdout,
                                                        conversion_func=None)
        self.mock_term.green.assert_called_once_with('GOOD: python main.py')
        assert not self.mock_term.red.called

    def test_executable_not_found_raises(self):
        self.mock_walk.return_value = [('root',
                                        ['dir1', 'dir2'],
                                        ['test1.py', 'main.py', 'test2.py'],
                                        )]
        self.mock_assess_answer.return_value = None

        with pytest.raises(Exception):
            run('test_directory', 'python main.py', expected='test_val', executable='does_not_exist.py')

        assert not self.mock_print.called
        assert not self.mock_assess_answer.called
        assert not self.mock_term.green.called
        assert not self.mock_term.red.called

class TestCreateVirtualenv(object):
    def setup_method(self):
        self.exists_patcher = mock.patch('utils.os.path.exists')
        self.mock_exists = self.exists_patcher.start()

        self.abspath_patcher = mock.patch('utils.os.path.abspath')
        self.mock_abspath = self.abspath_patcher.start()

        self.run_patcher = mock.patch('utils.subprocess.run')
        self.mock_run = self.run_patcher.start()

        self.mock_abspath.return_value = 'test_abspath'

    def teardown_method(self):
        self.exists_patcher.stop()
        self.run_patcher.stop()
        self.abspath_patcher.stop()

    def test_venv_exists(self):
        self.mock_exists.return_value = True

        expected = self.mock_abspath.return_value
        actual = create_virtualenv('test_dir')

        assert expected == actual
        self.mock_exists.assert_called_once_with(self.mock_abspath.return_value)
        assert not self.mock_run.called

    def test_venv_does_not_exist(self):
        self.mock_exists.return_value = False

        expected = self.mock_abspath.return_value
        actual = create_virtualenv('test_dir')

        assert expected == actual
        self.mock_exists.assert_called_once_with(self.mock_abspath.return_value)
        self.mock_run.assert_called_once_with(['virtualenv',
                                               'test_abspath',
                                               '-p',
                                               'python3.6',
                                               '--no-download'],
                                              check=True)

class TestInstallRequirements(object):
    def setup_method(self):
        self.walk_patcher = mock.patch('utils.os.walk')
        self.mock_walk = self.walk_patcher.start()

        self.run_patcher = mock.patch('utils.subprocess.run')
        self.mock_run = self.run_patcher.start()

        self.mock_walk.return_value = [('root',
                                        ['dir1', 'dir2'],
                                        ['test1.py', 'main.py', 'test2.py', 'requirements.txt'],
                                        )]

        self.orig_proxy = os.environ.get('PIP_PROXY', '')

    def teardown_method(self):
        self.walk_patcher.stop()
        self.run_patcher.stop()

        os.environ['PIP_PROXY'] = self.orig_proxy

    def test_no_requirements_file(self):
        self.mock_walk.return_value = [('root',
                                        ['dir1', 'dir2'],
                                        ['test1.py', 'main.py', 'test2.py'],
                                        )]

        expected = None
        actual = install_requirements('test_venv', 'test_dir')

        assert expected == actual
        self.mock_walk.assert_called_once_with('test_dir')
        assert not self.mock_run.called

    def test_requirements_no_proxy(self):
        os.environ['PIP_PROXY'] = ''

        expected = None
        actual = install_requirements('test_venv', 'test_dir')
        assert expected == actual
        self.mock_walk.assert_called_once_with('test_dir')
        self.mock_run.assert_called_once_with(['test_venv/bin/pip',
                                               'install',
                                               '-r',
                                               'root/requirements.txt'],
                                              check=True)

    def test_requirements_with_proxy(self):
        os.environ['PIP_PROXY'] = 'test_proxy'

        expected = None
        actual = install_requirements('test_venv', 'test_dir')
        assert expected == actual
        self.mock_walk.assert_called_once_with('test_dir')
        self.mock_run.assert_called_once_with(['test_venv/bin/pip',
                                               'install',
                                               '-r',
                                               'root/requirements.txt',
                                               '--proxy',
                                               'test_proxy'],
                                              check=True)
