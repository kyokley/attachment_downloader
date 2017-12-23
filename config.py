import os
import ConfigParser

from six.moves import input

def createConfig(path):
    config = ConfigParser.ConfigParser()
    config.add_section('Settings')

    host = input('Enter host: ')
    config.set('Settings', 'HOST', host)

    username = input('Enter username: ')
    config.set('Settings', 'USERNAME', username)

    directory = input('Enter directory: ')
    config.set('Settings', 'DIRECTORY', directory)

    with open(path, 'wb') as f:
        f.write(config)

def loadConfig(path):
    if not os.path.exists(path):
        createConfig(path)

    config = ConfigParser.ConfigParser()
    config.read(path)

    return config
