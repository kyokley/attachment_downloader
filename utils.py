import subprocess #nosec
import shlex

from blessings import Terminal

term = Terminal()
SENTINEL = object()

TIMEOUT = 60

def run(directory, cmd, expected=SENTINEL, suppress_output=False, conversion_func=None):
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
        failure_message = test_answer(expected, completed_process.stdout, conversion_func=conversion_func)
        if not failure_message:
            print(term.green('GOOD: {}'.format(cmd)))
        else:
            print(term.red('FAILED: {}'.format(cmd)))
            print(term.red('Got:'))
            print(term.red(failure_message))

def test_answer(expected, actual, conversion_func=None):
    if not conversion_func:
        conversion_func = lambda x: x

    try:
        split_actual = actual.strip().split('\n')
        split_actual = [conversion_func(x) for x in split_actual if x]
    except Exception as e:
        return str(e)

    for idx, val in enumerate(expected):
        if val != split_actual[idx]:
            return 'Value at {idx} does not match\nExpected: {expected} Actual: {actual}'.format(
                        idx=idx,
                        expected=val,
                        actual=split_actual[idx])
