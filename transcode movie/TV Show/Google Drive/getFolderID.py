        #!/usr/bin/env python

        from __future__ import print_function
        import os

        from apiclient.discovery import build
        from httplib2 import Http
        from oauth2client import file, client, tools
        import requests
        try:
            import argparse
            flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()
        except ImportError:
            flags = None

        SCOPES = 'https://www.googleapis.com/auth/drive.file'
        store = file.Storage('storage.json')
        creds = store.get()
        if not creds or creds.invalid:
            flow = client.flow_from_clientsecrets('client_secrets.json', SCOPES)
            creds = tools.run_flow(flow, store, flags) \
                    if flags else tools.run(flow, store)
        DRIVE = build('drive', 'v2', http=creds.authorize(Http()))
        print (DRIVE.children().list( folderId='0BwZkkLKYLl7WQ2FFeXFZcHpReUE').execute()['items'])


