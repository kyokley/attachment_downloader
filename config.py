import os
import configparser

from six.moves import input

def createConfig(path):
    config = configparser.ConfigParser()
    config.add_section('Settings')

    host = input('Enter host: ')
    username = input('Enter username: ')
    directory = input('Enter directory: ')

    config['Settings'] = {'HOST': host,
                          'USERNAME': username,
                          'DIRECTORY': directory}

    with open(path, 'w') as f:
        config.write(f)

def loadConfig(path):
    if not os.path.exists(path):
        createConfig(path)

    config = configparser.ConfigParser()
    config.read(path)

    return config
