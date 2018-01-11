import os
import subprocess #nosec
import shlex

from blessings import Terminal

term = Terminal()
SENTINEL = object()

TIMEOUT = 60

def run(directory, cmd, executable=None, expected=SENTINEL, suppress_output=False, conversion_func=None):
    if executable:
        fullpath = None
        for root, dirs, files in os.walk(directory):
            for file in files:
                if file == executable:
                    fullpath = os.path.join(root, file)
                    break

            if fullpath:
                break

        if not fullpath:
            raise Exception('{} not found in {}'.format(executable, directory))

        directory = os.path.dirname(fullpath)

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
        failure_message = assess_answer(expected, completed_process.stdout, conversion_func=conversion_func)
        if not failure_message:
            print(term.green('GOOD: {}'.format(cmd)))
        else:
            print(term.red('FAILED: {}'.format(cmd)))
            if executable:
                print(term.red('Executed in {}'.format(directory)))
            print(term.red('Got:'))
            print(term.red(failure_message))

def assess_answer(expected, actual, conversion_func=None):
    if not conversion_func:
        conversion_func = lambda x: x

    if not isinstance(expected, (list, tuple)):
        expected = [expected]

    try:
        split_actual = actual.strip().split('\n')
        split_actual = [conversion_func(x) for x in split_actual if x]
    except Exception as e:
        return str(e)

    if len(expected) > len(split_actual):
        return 'Not enough values provided in answer'
    elif len(expected) < len(split_actual):
        return 'Extra values provided in answer'

    for idx, val in enumerate(expected):
        if val != split_actual[idx]:
            return 'Value at index {idx} does not match\nExpected: {expected} ({expected_type}) Actual: {actual} ({actual_type})'.format(
                        idx=idx,
                        expected=val,
                        expected_type=type(val),
                        actual=split_actual[idx],
                        actual_type=type(split_actual[idx]))
