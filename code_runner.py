import os
import sys

from blessings import Terminal

from config import loadConfig
from utils import run

term = Terminal()

BANDIT_EXECUTABLE = os.path.join(os.path.dirname(sys.executable), 'bandit')

def run_all():
    config = loadConfig('settings.conf')
    LOCAL_DIRECTORY = config.get('ATTACHMENTS', 'LOCAL_DIRECTORY')

    solutions = os.listdir(LOCAL_DIRECTORY)

    for solution in solutions:
        print('Running {}'.format(solution))
        path = os.path.join(LOCAL_DIRECTORY, solution)
        try:
            check_bandit(path)

            check_triangle(path, 'degenerate_triangle.txt', 5)
            check_triangle(path, 'small_triangle.txt', 387)
            check_triangle(path, 'large_triangle.txt', 3549)

        except Exception as e:
            print(term.red('Got exception running {}'.format(solution)))
            print(term.red(e))
            print(term.red(e.stdout))

        print()

def check_bandit(path):
    run(path,
        '{} -r {}'.format(BANDIT_EXECUTABLE, path),
        suppress_output=True,
        )

def check_triangle(path, filename, expected):
    data_directory = os.path.join(
            os.path.abspath(os.path.dirname(__file__)),
            'data')

    run(path,
        'python3 traversal.py {}'.format(
            os.path.join(data_directory, filename)),
        expected=expected)

if __name__ == '__main__':
    run_all()
