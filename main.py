import getpass

from six.moves import input

from config import loadConfig
from imap_server import ImapServer
from attachment import decompress_archives
from code_runner import run_all

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

    run_code = input('Run code now? (y/N) ')
    if run_code.lower() in ('y', 'yes'):
        run_all()

if __name__ == '__main__':
    main()
