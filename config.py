import os
import configparser

from six.moves import input
from blessings import Terminal

term = Terminal()

def createConfig(path):
    config = configparser.ConfigParser()
    config.add_section('IMAP')

    host = input(term.yellow('Enter host: '))
    username = input(term.yellow('Enter username: '))
    folder = input(term.yellow('Enter folder: '))

    config['IMAP'] = {'HOST': host,
                      'USERNAME': username,
                      'FOLDER': folder}

    local_directory = input(term.yellow('Enter local directory: '))
    config['ATTACHMENTS'] = {'LOCAL_DIRECTORY': local_directory}


    with open(path, 'w') as f:
        config.write(f)

def loadConfig(path):
    if not os.path.exists(path):
        createConfig(path)

    config = configparser.ConfigParser()
    config.read(path)

    return config
