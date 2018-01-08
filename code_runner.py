import os
import sys

from blessings import Terminal

from config import loadConfig
from utils import run
from test_data import TEST_TRIANGLES

term = Terminal()

BANDIT_EXECUTABLE = os.path.join(os.path.dirname(sys.executable), 'bandit')

class StopExecution(Exception):
    pass

def run_all():
    config = loadConfig('settings.conf')
    LOCAL_DIRECTORY = config.get('ATTACHMENTS', 'LOCAL_DIRECTORY')

    solutions = os.listdir(LOCAL_DIRECTORY)

    for solution in solutions:
        print('Running {}'.format(term.blue(solution)))
        path = os.path.join(LOCAL_DIRECTORY, solution)
        try:
            check_bandit(path)

            for test in TEST_TRIANGLES:
                check_triangle(path, **test)

        except StopExecution:
            raise
        except Exception as e:
            print(term.red('Got exception running {}'.format(solution)))
            print(term.red(str(e)))
            print(term.red(e.stdout))

        print()

def check_bandit(path):
    run(path,
        '{} -r {}'.format(BANDIT_EXECUTABLE, path),
        suppress_output=True,
        )

def check_triangle(path, filename=None, expected=None, conversion_func=None):
    # filename and expected are actually required args for the function but I define them
    # as kwargs to allow ** unpacking of the test values
    if not filename:
        raise StopExecution('Test solutions have been improperly defined: filename is missing')
    if not expected:
        raise StopExecution('Test solutions have been improperly defined: expected is missing')

    data_directory = os.path.join(
            os.path.abspath(os.path.dirname(__file__)),
            'data')

    run(path,
        'python3 traversal.py {}'.format(
            os.path.join(data_directory, filename)),
        expected=expected,
        conversion_func=conversion_func)

if __name__ == '__main__':
    run_all()
