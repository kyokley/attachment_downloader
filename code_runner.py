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

def run_all():
    config = loadConfig('settings.conf')
    LOCAL_DIRECTORY = config.get('ATTACHMENTS', 'LOCAL_DIRECTORY')
    EXECUTABLE = config.get('EXECUTION', 'EXECUTABLE')

    solutions = os.listdir(LOCAL_DIRECTORY)

    passes = set()
    fails = set()
    timings = dict()

    for solution in solutions:
        print('Running {}'.format(term.blue(solution)))
        passes.add(solution)
        path = os.path.join(LOCAL_DIRECTORY, solution)
        try:
            check_bandit(path)

            venv_path = create_virtualenv(path)
            install_requirements(venv_path, path)

            start_time = datetime.now()
            for test in TEST_TRIANGLES:
                result = check_triangle(path,
                                        python_executable=os.path.join(venv_path, 'bin', 'python3'),
                                        executable=EXECUTABLE,
                                        **test)
                if not result:
                    fails.add(solution)
            finish_time = datetime.now()
            timings[solution] = finish_time - start_time

        except StopExecution:
            raise
        except Exception as e:
            fails.add(solution)
            print(term.red('Got exception running {}'.format(solution)))
            print(term.red(str(e)))
            if hasattr(e, 'stdout') and e.stdout:
                print(term.red(e.stdout))

        print()

    passes.difference_update(fails)
    return passes, fails, timings

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
