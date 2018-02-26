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
                 failures=None,
                 solution_directory=None):
        self.name = name
        self.time = time
        self.failures = failures or []
        self.solution_directory = solution_directory

    @property
    def has_failures(self):
        return bool(self.failures)

    def __str__(self):
        if not self.has_failures:
            return '{name} completed successfully in {time}'.format(name=self.name,
                                                                    time=self.time)
        else:
            return '{name} failed for {failures}'.format(name=self.name,
                                                         failures='\n'.join(self.failures))

    def write_failures_to_file(self):
        if not self.failures:
            print(term.yellow('No failure to write'))
        elif not self.solution_directory:
            print(term.yellow('Cannot write error file. No directory specified'))
        else:
            full_path = os.path.join(self.solution_directory, 'error.txt')
            with open(full_path, 'w') as f:
                f.write('\n'.join(self.failures))

    def add_failure(self, failure):
        self.failures.append(failure)

def run_all():
    config = loadConfig('settings.conf')
    LOCAL_DIRECTORY = config.get('ATTACHMENTS', 'LOCAL_DIRECTORY')
    EXECUTABLE = config.get('EXECUTION', 'EXECUTABLE')
    STOP_ON_FIRST_FAILURE = config.getboolean('EXECUTION', 'STOP_ON_FIRST_FAILURE')

    solutions = os.listdir(LOCAL_DIRECTORY)

    results = []

    for solution in solutions:
        print('Running {}'.format(term.blue(solution)))

        path = os.path.join(LOCAL_DIRECTORY, solution)

        result = Result(solution,
                        solution_directory=path)

        try:
            check_bandit(path)
        except StopExecution:
            raise
        except Exception as e:
            print(term.red('Got exception running {}'.format(solution)))
            print(term.red(str(e)))
            failure_message = str(e)

            if hasattr(e, 'stdout') and e.stdout:
                print(term.red(e.stdout))
                failure_message = failure_message + '\nFrom stdout:\n{stdout}'.format(stdout=e.stdout)

            result.add_failure(failure_message)
            results.append(result)
            continue

        venv_path = create_virtualenv(path)
        install_requirements(venv_path, path)

        start_time = datetime.now()
        for test in TEST_TRIANGLES:
            try:
                failure_message = check_triangle(path,
                                                 python_executable=os.path.join(venv_path, 'bin', 'python3'),
                                                 executable=EXECUTABLE,
                                                 **test)

                if failure_message:
                    result.add_failure(failure_message)

                    if STOP_ON_FIRST_FAILURE:
                        break
            except StopExecution:
                raise
            except Exception as e:
                print(term.red('ERROR:'))
                print(term.red('Got exception running {}'.format(solution)))
                print(term.red(str(e)))
                failure_message = str(e)

                if hasattr(e, 'stdout') and e.stdout:
                    print(term.red(e.stdout))
                    failure_message = failure_message + '\nFrom stdout:\n{stdout}'.format(stdout=e.stdout)

                result.add_failure(failure_message)

                if STOP_ON_FIRST_FAILURE:
                    break

        finish_time = datetime.now()
        result.time = finish_time - start_time
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
