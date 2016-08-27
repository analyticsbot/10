#! /usr/bin/env python
# -*- coding: utf-8 -*-

import httplib2
import os

from apiclient.discovery import build
from apiclient.http import MediaFileUpload
from oauth2client.client import SignedJwtAssertionCredentials
from oauth2client.file import Storage


# Don't ask me, where I've got the value for 'SERVICE_NAME'.
SERVICE_NAME = 'drive'

# Can be found here: http://developers.google.com/apis-explorer/#p/
SERVICE_API_VERSION = 'v2'

# Can be chosen from available Google Drive scopes: https://developers.google.com/drive/web/scopes
# (Try to find scope list for other services, heh).
SERVICE_SCOPE = 'https://www.googleapis.com/auth/drive.file'

# Email which was given after creation of Client ID
SERVICE_ACCOUNT_EMAIL = 'YOUR_SERVICE_EMAIL'

# Path to your private key which was given after creation of Client ID
PRIVATE_KEY_PATH = 'YOUR_PRIVATE_KEY_PATH'

# A file, where OAuth credentials will be stored (URIs, tokens and so on).
CREDENTIALS_STORAGE = os.path.join(os.path.dirname(PRIVATE_KEY_PATH),
                                   '{}-credentials.json'.format(SERVICE_NAME))

# ID of the folder you want to upload your files to.
FOLDER_ID = 'YOUR_GOOGLE_DRIVE_FOLDER_ID'


def get_service():
    storage = Storage(CREDENTIALS_STORAGE)
    credentials = storage.get()
    http = httplib2.Http()

    if credentials is None or credentials.invalid:
        with open(PRIVATE_KEY_PATH, 'rb') as f:
            private_key = f.read()
        credentials = SignedJwtAssertionCredentials(SERVICE_ACCOUNT_EMAIL,
                                                    private_key,
                                                    scope=SERVICE_SCOPE)
        storage.put(credentials)
    else:
        credentials.refresh(http)

    http = credentials.authorize(http)
    return build(serviceName=SERVICE_NAME,
                 version=SERVICE_API_VERSION,
                 http=http)


def upload_file(service, filename, description, mime_type, parent_id=None):
    media_body = MediaFileUpload(filename, mimetype=mime_type, resumable=True)
    body = {
        'title': os.path.basename(filename),
        'mimeType': mime_type,
        'description': description,
    }
    if parent_id:
        body['parents'] = [{'id': parent_id}, ]
    return service.files().insert(body=body, media_body=media_body).execute()


filename = "test.txt"
description = "this file is used to test Google Drive API"
mime_type = "text/plain"

service = get_service()
f = upload_file(service=service,
                filename=filename,
                description=description,
                mime_type=mime_type,
                parent_id=FOLDER_ID)
