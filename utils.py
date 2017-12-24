import subprocess #nosec
import shlex

from blessings import Terminal

term = Terminal()
SENTINEL = object()

TIMEOUT = 60

def run(directory, cmd, expected=SENTINEL, suppress_output=False):
    split_cmd = shlex.split(cmd)
    completed_process = subprocess.run(split_cmd,
                                       stdout=subprocess.PIPE,
                                       stderr=subprocess.STDOUT,
                                       cwd=directory,
                                       timeout=TIMEOUT,
                                       check=True,
                                       encoding='utf-8',
                                       )

    if expected == SENTINEL:
        if not suppress_output:
            print(completed_process.stdout)
        else:
            print(term.green('GOOD: {}'.format(cmd)))
    else:
        if completed_process.stdout.strip() == str(expected):
            print(term.green('GOOD: {}'.format(cmd)))
        else:
            print(term.red('FAILED: {}'.format(cmd)))
            print(term.red('Got:'))
            print(term.red(completed_process.stdout))
