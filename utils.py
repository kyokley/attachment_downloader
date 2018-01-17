import os
import subprocess #nosec
import shlex

from blessings import Terminal

term = Terminal()
SENTINEL = object()

TIMEOUT = 60
REQUIREMENTS = 'requirements.txt'

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

        return True
    else:
        failure_message = assess_answer(expected, completed_process.stdout, conversion_func=conversion_func)
        if not failure_message:
            print(term.green('GOOD: {}'.format(cmd)))
            return True
        else:
            print(term.red('FAILED: {}'.format(cmd)))
            if executable:
                print(term.red('Executed in {}'.format(directory)))
            print(term.red('Got:'))
            print(term.red(failure_message))
            return False

def create_virtualenv(directory):
    venv_path = os.path.abspath(os.path.join(directory, '.venv'))
    if os.path.exists(venv_path):
        print(term.yellow('{} already exists. Continuing...'.format(venv_path)))
    else:
        split_cmd = shlex.split('virtualenv {} -p python3.6 --no-download'.format(venv_path))

        subprocess.run(split_cmd,
                       check=True)
    return venv_path

def install_requirements(venv_path, directory):
    requirements_path = None
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file == REQUIREMENTS:
                requirements_path = os.path.join(root, file)
                break

        if requirements_path:
            break

    if requirements_path:
        if os.environ.get('PIP_PROXY'):
            split_cmd = shlex.split('{pip} install -r {requirements_path} --proxy {proxy}'.format(
                pip=os.path.join(venv_path, 'bin', 'pip'),
                requirements_path=requirements_path,
                proxy=os.environ.get('PIP_PROXY')))
        else:
            split_cmd = shlex.split('{pip} install -r {requirements_path}'.format(
                pip=os.path.join(venv_path, 'bin', 'pip'),
                requirements_path=requirements_path,
                ))

        subprocess.run(split_cmd,
                       check=True)

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
