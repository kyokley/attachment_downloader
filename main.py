import getpass

from config import loadConfig

def main():
    config = loadConfig('settings.conf')
    HOST = config.get('Settings', 'HOST')
    USERNAME = config.get('Settings', 'USERNAME')
    DIRECTORY = config.get('Settings', 'DIRECTORY')
    PASSWORD = getpass.getpass()

if __name__ == '__main__':
    main()
