import os
import sys
from datetime import datetime

from blessings import Terminal

from config import loadConfig
from utils import run, create_virtualenv, install_requirements
from test_data import TEST_TRIANGLES

term = Terminal()

BANDIT_EXECUTABLE = os.path.join(os.path.dirname(sys.executable), 'bandit')

class StopExecution(Exception):
    pass

class Result(object):
    def __init__(self,
                 name,
                 time=None,
                 failure_reason=None,
                 solution_directory=None):
        if not time and not failure_reason:
            raise StopExecution('Improperly defined Result')

        self.name = name
        self.time = time
        self.failure_reason = failure_reason
        self.solution_directory = solution_directory

    @property
    def failed(self):
        return bool(self.failure_reason)

    def __str__(self):
        if not self.failed:
            return '{name} completed successfully in {time}'.format(name=self.name,
                                                                    time=self.time)
        else:
            return '{name} failed for {failure_reason}'.format(name=self.name,
                                                               failure_reason=self.failure_reason)

    def write_failure_reason_to_file(self):
        if not self.failure_reason:
            print(term.yellow('No failure to write'))
        elif not self.solution_directory:
            print(term.yellow('Cannot write error file. No directory specified'))
        else:
            full_path = os.path.join(self.solution_directory, 'error.txt')
            with open(full_path, 'w') as f:
                f.write(self.failure_reason)

def run_all():
    config = loadConfig('settings.conf')
    LOCAL_DIRECTORY = config.get('ATTACHMENTS', 'LOCAL_DIRECTORY')
    EXECUTABLE = config.get('EXECUTION', 'EXECUTABLE')

    solutions = os.listdir(LOCAL_DIRECTORY)

    results = []

    for solution in solutions:
        print('Running {}'.format(term.blue(solution)))
        path = os.path.join(LOCAL_DIRECTORY, solution)
        try:
            check_bandit(path)

            venv_path = create_virtualenv(path)
            install_requirements(venv_path, path)

            start_time = datetime.now()
            for test in TEST_TRIANGLES:
                failure_message = check_triangle(path,
                                        python_executable=os.path.join(venv_path, 'bin', 'python3'),
                                        executable=EXECUTABLE,
                                        **test)
                if failure_message:
                    result = Result(solution,
                                    failure_reason=failure_message,
                                    solution_directory=path)
                    result.write_failure_reason_to_file()
                    results.append(result)
                    break
            else:
                finish_time = datetime.now()
                result = Result(solution,
                                time=finish_time - start_time,
                                solution_directory=path)
                results.append(result)

        except StopExecution:
            raise
        except Exception as e:
            print(term.red('Got exception running {}'.format(solution)))
            print(term.red(str(e)))
            failure_message = str(e)

            if hasattr(e, 'stdout') and e.stdout:
                print(term.red(e.stdout))
                failure_message = failure_message + '\nFrom stdout:\n{stdout}'.format(stdout=e.stdout)

            result = Result(solution,
                            failure_reason=failure_message,
                            solution_directory=path)
            result.write_failure_reason_to_file()
            results.append(result)

        print()

    return results

def check_bandit(path):
    run(path,
        '{} -r {}'.format(BANDIT_EXECUTABLE, path),
        suppress_output=True,
        )

def check_triangle(path,
        python_executable='python3',
        executable='traversal.py',
        filename=None,
        expected=None,
        conversion_func=None):
    # filename and expected are actually required args for the function but I define them
    # as kwargs to allow ** unpacking of the test values
    if not filename:
        raise StopExecution('Test solutions have been improperly defined: filename is missing')
    if not expected:
        raise StopExecution('Test solutions have been improperly defined: expected is missing')

    data_directory = os.path.join(
            os.path.abspath(os.path.dirname(__file__)),
            'data')

    return run(path,
               '{} {} {}'.format(python_executable,
                                 executable,
                                 os.path.join(data_directory, filename)),
               executable=executable,
               expected=expected,
               conversion_func=conversion_func)

if __name__ == '__main__':
    run_all()
