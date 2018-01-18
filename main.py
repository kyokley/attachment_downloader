import getpass

from six.moves import input

from config import loadConfig
from imap_server import ImapServer
from attachment import decompress_archives
from code_runner import run_all
from blessings import Terminal

term = Terminal()

def main():
    config = loadConfig('settings.conf')
    HOST = config.get('IMAP', 'HOST')
    USERNAME = config.get('IMAP', 'USERNAME')
    FOLDER = config.get('IMAP', 'FOLDER')
    FILENAME = config.get('RESULTS', 'FILENAME')
    PASSWORD = getpass.getpass()

    LOCAL_DIRECTORY = config.get('ATTACHMENTS', 'LOCAL_DIRECTORY')

    imap_server = ImapServer(HOST,
                             USERNAME,
                             PASSWORD,
                             folder=FOLDER,
                             )
    imap_server.download_attachements(directory=LOCAL_DIRECTORY)
    imap_server.logout()

    print('Finished downloading attachments')
    print()

    print('Starting decompressing archives')
    decompress_archives(LOCAL_DIRECTORY)
    print('Finished decompressing archives')
    print()

    run_code = input('Run code now? (y/N) ')
    if run_code.lower() in ('y', 'yes'):
        results = run_all()
        successes = [x for x in results if not x.failed]
        successes.sort(key=lambda x: x.time)

        print('Correct Solutions:')
        for result in successes:
            print('{name}\n\t{time}'.format(name=term.blue(result.name),
                                            time=term.magenta(str(result.time))))
            print()

        if FILENAME:
            with open(FILENAME, 'w') as f:
                for result in successes:
                    f.write('{name} {time}\n'.format(name=result.name,
                                                     time=str(result.time)))

    print()
    print('All Done')

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print(term.red('Aborting'))
    except Exception as e:
        print(term.red(str(e)))
