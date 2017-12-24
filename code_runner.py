import os
import subprocess
import shlex

from config import loadConfig

TIMEOUT = 60

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
                'python3 traversal.py {}'.format(
                    os.path.join(data_directory, 'small_triangle.txt')),
                expected='387')
        except Exception as e:
            print('Got exception running {}'.format(solution))
            print(e)
            print(e.stdout)


def run(directory, cmd, expected=None):
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
        print(completed_process.stdout)
    else:
        if completed_process.stdout.strip() == expected:
            print('Good')
        else:
            print('FAILED')
            print('Got:')
            print(completed_process.stdout)


if __name__ == '__main__':
    run_all()
