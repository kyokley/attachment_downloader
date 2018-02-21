import os
import configparser

from six.moves import input
from blessings import Terminal

term = Terminal()

YES_OR_NO = ('y', 'yes', 'n', 'no')

def createConfig(path):
    config = configparser.ConfigParser()
    config.add_section('IMAP')

    host = input(term.yellow('Enter host: '))
    username = input(term.yellow('Enter username: '))
    folder = input(term.yellow('Enter folder: '))
    executable = input(term.yellow('Enter executable: '))
    filename = input(term.yellow('Enter filename for results: '))

    stop_on_first_failure = None
    while stop_on_first_failure is None:
        resp = input(term.yellow('Stop on first failure? [Y/n]: ')).lower() or 'yes'
        if resp in YES_OR_NO:
            stop_on_first_failure = resp in ('y', 'yes')

    config['IMAP'] = {'HOST': host,
                      'USERNAME': username,
                      'FOLDER': folder}

    local_directory = input(term.yellow('Enter local directory: '))
    config['ATTACHMENTS'] = {'LOCAL_DIRECTORY': local_directory}
    config['EXECUTION'] = {'EXECUTABLE': executable,
                           'STOP_ON_FIRST_FAILURE': stop_on_first_failure}
    config['RESULTS'] = {'FILENAME': filename}

    with open(path, 'w') as f:
        config.write(f)

def loadConfig(path):
    if not os.path.exists(path):
        createConfig(path)

    config = configparser.ConfigParser()
    config.read(path)

    return config
