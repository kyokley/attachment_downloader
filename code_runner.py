import os
import sys
import subprocess
import shlex

from config import loadConfig

TIMEOUT = 60

BANDIT_EXECUTABLE = os.path.join(os.path.dirname(sys.executable), 'bandit')

def run_all():
    config = loadConfig('settings.conf')
    LOCAL_DIRECTORY = config.get('ATTACHMENTS', 'LOCAL_DIRECTORY')

    solutions = os.listdir(LOCAL_DIRECTORY)
    data_directory = os.path.join(
            os.path.abspath(os.path.dirname(__file__)),
            'data')

    for solution in solutions:
        path = os.path.join(LOCAL_DIRECTORY, solution)
        try:
            print('Running {}'.format(solution))
            run(path,
                '{} -r {}'.format(BANDIT_EXECUTABLE, path),
                suppress_output=True,
                )
            run(path,
                'python3 traversal.py {}'.format(
                    os.path.join(data_directory, 'small_triangle.txt')),
                expected='387')

            run(path,
                'python3 traversal.py {}'.format(
                    os.path.join(data_directory, 'large_triangle.txt')),
                expected='3549')
        except Exception as e:
            print('Got exception running {}'.format(solution))
            print(e)
            print(e.stdout)


def run(directory, cmd, expected=None, suppress_output=False):
    split_cmd = shlex.split(cmd)
    completed_process = subprocess.run(split_cmd,
                                       stdout=subprocess.PIPE,
                                       stderr=subprocess.STDOUT,
                                       cwd=directory,
                                       timeout=TIMEOUT,
                                       check=True,
                                       encoding='utf-8',
                                       )

    if not expected:
        if not suppress_output:
            print(completed_process.stdout)
    else:
        if completed_process.stdout.strip() == expected:
            print('GOOD: {}'.format(cmd))
        else:
            print('FAILED: {}'.format(cmd))
            print('Got:')
            print(completed_process.stdout)


if __name__ == '__main__':
    run_all()
