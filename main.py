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
        passes, fails, timings = run_all()

        print('Correct Solutions:')
        for solution in passes:
            print('{solution}\n\t{time}'.format(solution=term.blue(solution),
                                                time=term.magenta(str(timings[solution]))))
            print()

        if FILENAME:
            with open(FILENAME, 'w') as f:
                for solution in passes:
                    f.write('{solution} {time}\n'.format(solution=solution,
                                                         time=timings[solution]))

    print()
    print('All Done')

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print(term.red('Aborting'))
    except Exception as e:
        print(term.red(str(e)))
