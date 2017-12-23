import getpass

from config import loadConfig
from imap_server import ImapServer

def main():
    config = loadConfig('settings.conf')
    HOST = config.get('Settings', 'HOST')
    USERNAME = config.get('Settings', 'USERNAME')
    DIRECTORY = config.get('Settings', 'DIRECTORY')
    PASSWORD = getpass.getpass()

    imap_server = ImapServer(HOST,
                             USERNAME,
                             PASSWORD,
                             directory=DIRECTORY,
                             )
    imap_server.download_attachements()
    imap_server.logout()

if __name__ == '__main__':
    main()
