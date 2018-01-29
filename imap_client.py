import os
import email
import hashlib
import base64
import re
from imaplib import (IMAP4_SSL,
                     IMAP4,
                     )
from attachment import (archive_extension,
                        archive_basename,
                        BadExtension,
                        )
from blessings import Terminal
term = Terminal()

EMAIL_REGEX = re.compile('(?<=<)[^<>]+(?=>)')
QUOTED_PRINTABLE_ENCODED_REGEX = re.compile('=\S{2}')
OK = 'OK'

def _unique_id():
    count = 1
    while True:
        yield count
        count += 1

id_gen = _unique_id()

class NotConnected(Exception):
    pass

class ImapClient(object):
    def __init__(self,
                 host,
                 username,
                 password,
                 folder=None,
                 ssl=True):
        self.host = host
        self.username = username
        self.password = password
        self.folder = folder
        self._connected = False

        if ssl:
            _imap_class = IMAP4_SSL
        else:
            _imap_class = IMAP4

        self._connection = _imap_class(self.host)
        self._login()

        if self.folder:
            self._select(self.folder)

    @staticmethod
    def _unique_filename(filename, from_addr='', date='', count=0):
        if filename.startswith('='):
            charset, encoding, encoded_filename = filename.split('?')[1:4]
            if encoding in ('b', 'B'):
                filename = base64.b64decode(encoded_filename).decode(charset)
            elif encoding in ('q', 'Q'):
                filename = encoded_filename
                match = QUOTED_PRINTABLE_ENCODED_REGEX.search(filename)
                while match:
                    filename = filename[:match.start()] + chr(int(match.group()[1:], 16)) + filename[match.end():]
                    match = QUOTED_PRINTABLE_ENCODED_REGEX.search(filename)

        filename = filename.strip()
        ext = archive_extension(filename)
        basename = archive_basename(filename)
        hash_obj = hashlib.sha256()

        hash_obj.update(from_addr.encode('utf-8'))
        hash_obj.update(date.encode('utf-8'))
        hash_obj.update(str(count).encode('utf-8'))

        hash_val = hash_obj.hexdigest()[:6]

        return '{basename}_{hash_val}{ext}'.format(basename=basename,
                                                   hash_val=hash_val,
                                                   ext=ext).lower()

    def _login(self):
        typ, data = self._connection.login(self.username, self.password)

        if typ != OK:
            raise Exception('Unable to login: {}'.format(typ))

        self._connected = True

    def _select(self, folder):
        if not self._connected:
            raise NotConnected()

        typ, data = self._connection.select(folder)

        if typ != OK:
            raise Exception('Error attempting to select folder: {}'.format(data))

        return data

    def _search(self, *args):
        if not self._connected:
            raise NotConnected()

        typ, data = self._connection.search(*args)

        if typ != OK:
            raise Exception('Error attempting to search for messages')

        return data

    def _fetch(self, *args):
        if not self._connected:
            raise NotConnected()

        typ, message_parts = self._connection.fetch(*args)

        if typ != OK:
            raise Exception('Error attempting to fetch msg: {}'.format(args[0]))

        return message_parts

    def fetch_messages(self):
        data = self._search(None, 'ALL')

        for msg_id in data[0].split():
            message_parts = self._fetch(msg_id, '(RFC822)')

            email_body = message_parts[0][1]

            mail = email.message_from_string(email_body.decode('utf-8'))
            yield mail

    def download_attachements(self, directory='.'):
        if not os.path.exists(directory):
            os.mkdir(directory)

        for mail in self.fetch_messages():
            count = 0
            for part in mail.walk():
                count += 1
                if (part.get_content_maintype() in ('multipart', 'text') or
                        part.get('Content-Disposition') is None):
                    continue

                orig_filename = part.get_filename()
                if not orig_filename:
                    print(term.red('Could not get filename from {} {}'.format(mail.get('From', ''),
                                                                              mail.get('Subject', ''))))
                    continue

                try:
                    uniq_filename = self._unique_filename(orig_filename,
                                                          from_addr=mail.get('From', ''),
                                                          date=mail.get('Date', ''),
                                                          count=count)
                except BadExtension as e:
                    print(term.red(str(e)))
                    continue

                full_path = os.path.join(directory, uniq_filename)

                if (not os.path.exists(full_path) and
                        not os.path.exists(os.path.join(directory, archive_basename(uniq_filename)))):
                    print('Writing {}'.format(term.blue(uniq_filename)))

                    with open(full_path, 'wb') as f:
                        f.write(part.get_payload(decode=True))

    def get_email_addresses(self): # TODO: Test me
        email_addrs = set()

        for mail in self.fetch_messages():
            match = EMAIL_REGEX.search(mail.get('From', ''))
            if match:
                from_addr = match.group()
                email_addrs.add(from_addr)

        return email_addrs

    def logout(self):
        self._connection.close()
        self._connection.logout()
