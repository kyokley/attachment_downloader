import os
import email
from imaplib import (IMAP4_SSL,
                     IMAP4,
                     )

OK = 'OK'

class NotConnected(Exception):
    pass

class ImapServer(object):
    def __init__(self,
                 host,
                 username,
                 password,
                 directory=None,
                 ssl=True):
        self.host = host
        self.username = username
        self.password = password
        self.directory = directory
        self._connected = False

        if ssl:
            _imap_class = IMAP4_SSL
        else:
            _imap_class = IMAP4

        self._connection = _imap_class(self.host)
        self._login()

        if self.directory:
            self._connection.select(self.directory)

    def _login(self):
        typ, data = self._connection.login(self.username, self.password)

        if typ != OK:
            raise Exception('Unable to login: {}'.format(typ))

        self._connected = True

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

            mail = email.message_from_string(email_body)
            yield mail

    def download_attachements(self, directory='.'):
        for mail in self.fetch_messages():
            for part in mail.walk():
                if (part.get_content_maintype() == 'multipart' or
                        part.get('Content-Disposition') is None):
                    continue

                filename = part.get_filename()
                full_path = os.path.join(directory, filename)

                if not os.path.exists(full_path):
                    print('Writing {}'.format(filename))

                    with open(full_path, 'wb') as f:
                        f.write(part.get_payload(decode=True))

    def logout(self):
        self._connection.close()
        self._connection.logout()
