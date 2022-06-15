"""Email sender"""
from __future__ import annotations

from base64 import b64encode
from copy import deepcopy
from datetime import datetime
import json
import os
from os import listdir, remove
from os.path import basename, dirname, join, realpath
from pathlib import Path
from shutil import copyfile, rmtree
from subprocess import run

from numpy import unique


class SendEmails:
    """Send emails

    Parameters
    ----------
    subject: str
        Email subject
    body: str
        Email body. If this is a filename ending in :code:`.html`, then this
        will be read in and treated like a file. Otherwise, the text contained
        here will be used as the message body.
    attachments: list[str], optional, default=[]
        Attachment filenames
    contacts: str or list[str], optional, default=None
        specify receipient emails. Ignored if :code:`send_all`. The default
        receipient is just :code:`mike@lakeslegendaries.com` 
    contacts_backup_dir: str, optional, default='contacts'
        Subdirectory (within :code:`contacts_dir`) to put contacts backups in
    contacts_dir: str, optional, default='/mnt/d/OneDrive/Titans Of Eden/biz'
        Directory containing :code:`contacts_fname`
    contacts_fname: str, optional, default='contacts.txt'
        Master contacts list file
    send_all: bool, optional, default=False
        Send to all recipients on email list
    temp_dir: str, optional, default='.tmp'
        Temporary directory for downloading files from azure
    use_ci: bool, optional, default=False
        upload/download email tokens to sync with server
    """
    def __init__(
        self,
        /,
        subject: str,
        body: str,
        *,
        attachments: list[str] = [],
        contacts: str | list[str] = None,
        contacts_backup_dir: str = 'contacts',
        contacts_dir: str = '/mnt/d/OneDrive/Titans Of Eden/biz',
        contacts_fname: str = 'contacts.txt',
        send_all: bool = False,
        temp_dir: str = '.tmp',
        use_ci: bool = False,
    ):
        # create email dictionary
        is_html = body.endswith('.html')
        if is_html:
            body = open(body, 'r').read()
        email_dict = {
            'message': {
                'subject': subject,
                'body': {
                    'contentType': 'HTML' if is_html else 'Text',
                    'content': body,
                },
                'attachments': [],
            },
            'saveToSentItems': False,
        }

        # add attachments
        for attachment in attachments:
            bytes = b64encode(open(attachment, 'rb').read()).decode('utf-8')
            email_dict['message']['attachments'].append({
                '@odata.type': '#microsoft.graph.fileAttachment',
                'name': basename(attachment),
                'isInline': True,
                'contentId': basename(attachment).rsplit('.')[0],
                'contentType': f"image/{basename(attachment).rsplit('.')[1]}",
                'contentBytes': bytes,
            })

        # get recipient list
        if not send_all:
            if not contacts:
                contacts = ['mike@lakeslegendaries.com']
            elif type(contacts) is str:
                contacts = [contacts]
        else:
            # backup contacts
            contacts_fname = f'{contacts_dir}/{contacts_fname}'
            backup_fname = (
                contacts_fname.rsplit('.')[0]
                + '/' + contacts_backup_dir
                + '-' + datetime.strftime(datetime.now(), r'%Y-%m-%d')
                + '.txt'
            )
            copyfile(contacts_fname, backup_fname)

            # load existing contacts
            contacts = open(contacts_fname, 'r').read().splitlines()

            # autheticate with azure
            os.environ['AZURE_STORAGE_CONNECTION_STRING'] = \
                open(
                    f"{os.environ['SECRETS_DIR']}/titans-fileserver",
                    'r',
                ).read().strip()

            # load subscribes from azure
            Path(temp_dir).mkdir(exist_ok=True, parents=True)
            run(
                [
                    'az',
                    'storage',
                    'blob',
                    'download-batch',
                    '-d',
                    temp_dir,
                    '-s',
                    'subscribe',
                ],
                capture_output=True,
                check=True,
            )
            subscribes = listdir(temp_dir)
            rmtree(temp_dir)

            # load unsubscribes from azure
            Path(temp_dir).mkdir(exist_ok=True, parents=True)
            run(
                [
                    'az',
                    'storage',
                    'blob',
                    'download-batch',
                    '-d',
                    temp_dir,
                    '-s',
                    'unsubscribe',
                ],
                capture_output=True,
                check=True,
            )
            unsubscribes = listdir(temp_dir)
            rmtree(temp_dir)

            # create new master contacts list
            contacts.extend(subscribes)
            contacts = unique([
                contact
                for contact in contacts
                if contact not in unsubscribes
                and len(contact)
            ])

            # save new contacts list
            with open(contacts_fname, 'w') as file:
                for contact in contacts:
                    print(contact, file=file)

        # double-check if mass-sending
        if len(contacts) > 5:
            prompt = (
                f'Sending to {len(contacts)} contacts. '
                'Type \'Y\' to continue: '
            )
            if input(prompt) != 'Y':
                print('Aborting')
                return

        # send to each recipient
        for recipient in contacts:

            # get fresh copy of email
            email = deepcopy(email_dict)

            # substitute in email address
            email['message']['body']['content'] = \
                email['message']['body']['content'].replace(
                    r'#|EMAIL|#',
                    recipient,
                )

            # add recipient to email dictionary
            email['message']['toRecipients'] = [
                {
                    'emailAddress': {
                        'address': recipient,
                    },
                },
            ]

            # write json file
            fname = 'email.json'
            json.dump(
                email,
                open(fname, 'w'),
            )

            # invoke send bash script
            try:
                run_cmd = [
                    join(dirname(realpath(__file__)), 'send.sh'),
                    'email.json',
                ]
                if use_ci:
                    run_cmd.append('--ci')
                run(run_cmd, check=True)
            except Exception:
                print(f'Sending to {recipient} failed.')

            # clean-up
            remove(fname)
