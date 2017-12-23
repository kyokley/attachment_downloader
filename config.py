import os
import configparser

from six.moves import input

def createConfig(path):
    config = configparser.ConfigParser()
    config.add_section('IMAP')

    host = input('Enter host: ')
    username = input('Enter username: ')
    folder = input('Enter folder: ')

    config['IMAP'] = {'HOST': host,
                      'USERNAME': username,
                      'FOLDER': folder}

    local_directory = input('Enter local directory: ')
    config['ATTACHMENTS'] = {'LOCAL_DIRECTORY': local_directory}


    with open(path, 'w') as f:
        config.write(f)

def loadConfig(path):
    if not os.path.exists(path):
        createConfig(path)

    config = configparser.ConfigParser()
    config.read(path)

    return config
