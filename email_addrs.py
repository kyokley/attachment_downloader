import getpass

from config import loadConfig
from imap_client import ImapClient

def main():
    config = loadConfig('settings.conf')

    HOST = config.get('IMAP', 'HOST')
    USERNAME = config.get('IMAP', 'USERNAME')
    FOLDER = config.get('IMAP', 'FOLDER')
    PASSWORD = getpass.getpass()

    imap_client = ImapClient(HOST,
                             USERNAME,
                             PASSWORD,
                             folder=FOLDER,
                             )
    email_addrs = sorted(list(imap_client.get_email_addresses()))

    for addr in email_addrs:
        print(addr)

if __name__ == '__main__':
    main()
