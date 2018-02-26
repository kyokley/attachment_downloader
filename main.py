import getpass

from six.moves import input

from config import loadConfig
from imap_client import ImapClient
from attachment import decompress_archives
from code_runner import run_all
from blessings import Terminal
from utils import (output_results_to_stdout,
                   output_results_to_file,
                   )

term = Terminal()

def main():
    config = loadConfig('settings.conf')
    HOST = config.get('IMAP', 'HOST')
    USERNAME = config.get('IMAP', 'USERNAME')
    FOLDER = config.get('IMAP', 'FOLDER')
    FILENAME = config.get('RESULTS', 'FILENAME')
    PASSWORD = getpass.getpass()

    LOCAL_DIRECTORY = config.get('ATTACHMENTS', 'LOCAL_DIRECTORY')

    imap_client = ImapClient(HOST,
                             USERNAME,
                             PASSWORD,
                             folder=FOLDER,
                             )
    imap_client.download_attachements(directory=LOCAL_DIRECTORY)
    imap_client.logout()

    print('Finished downloading attachments')
    print()

    print('Starting decompressing archives')
    decompress_archives(LOCAL_DIRECTORY)
    print('Finished decompressing archives')
    print()

    run_code = input('Run code now? (y/N) ')
    if run_code.lower() in ('y', 'yes'):
        results = run_all()

        output_results_to_stdout(results)

        if FILENAME:
            output_results_to_file(FILENAME, results)

        for result in results:
            if result.has_failures:
                result.write_failures_to_file()

    print()
    print('All Done')

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print(term.red('Aborting'))
    #except Exception as e:
        #print(term.red(str(e)))
