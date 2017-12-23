import getpass

from config import loadConfig
from imap_server import ImapServer
from attachment import decompress_archives

def main():
    config = loadConfig('settings.conf')
    HOST = config.get('IMAP', 'HOST')
    USERNAME = config.get('IMAP', 'USERNAME')
    FOLDER = config.get('IMAP', 'FOLDER')
    PASSWORD = getpass.getpass()

    LOCAL_DIRECTORY = config.get('ATTACHMENTS', 'LOCAL_DIRECTORY')

    imap_server = ImapServer(HOST,
                             USERNAME,
                             PASSWORD,
                             folder=FOLDER,
                             )
    imap_server.download_attachements(directory=LOCAL_DIRECTORY)
    imap_server.logout()

    decompress_archives(LOCAL_DIRECTORY)

if __name__ == '__main__':
    main()
