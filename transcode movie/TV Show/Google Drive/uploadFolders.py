#!/usr/bin/env python
# all imports
from __future__ import print_function
import os, sys

from apiclient.discovery import build
from httplib2 import Http
from oauth2client import file, client, tools
import urllib, mimetypes
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
DRIVE = build('drive', 'v3', http=creds.authorize(Http()))

# static variables
MAIN_FOLDER = 'New_folder' # main root folder
MAIN_FOLDER_PARENT_ID = None #id of the parent folder for root folder
folder_id = {}
file_dict = {}

def uploadFiles(filename, mimeType, parentId):
    """Function to upload files"""
    metadata = {'name': filename.split('\\')[-1], 'parents': [parentId]}
    if mimeType:
        metadata['mimeType'] = mimeType
    res = DRIVE.files().create(body=metadata, media_body=filename).execute()
    if res:
        print('UPLOADED "%s"' % (filename))
    return res['id']

def createRemoteFolder(folderName, parentID):
        # Create a folder on Drive, returns the newly created folder ID
        body = {
          'name': folderName,
          'mimeType': "application/vnd.google-apps.folder"
        }
        if parentID:
            body['parents'] = [parentID]
        root_folder = DRIVE.files().create(body = body).execute()
        return root_folder['id']

# create the root folder and store the id
id = createRemoteFolder(MAIN_FOLDER, MAIN_FOLDER_PARENT_ID)
folder_id[MAIN_FOLDER] = id

curFolder = os.path.abspath(MAIN_FOLDER)
# recursive function
for dirname, dirnames, filenames in os.walk(MAIN_FOLDER):
    for subdirname in dirnames:
        print ("FOUND DIRECTORY: ", os.path.join(dirname, subdirname))
        print (dirname, subdirname)
        parentId = folder_id.get(dirname.split('\\')[-1], None)
        id = createRemoteFolder(subdirname, parentId)
        folder_id[subdirname] = id
    for filename in filenames:
        print ("FOUND FILE: ", os.path.join(dirname, filename))
        parentId = folder_id.get(dirname.split('\\')[-1], None)
        file_id = uploadFiles(os.path.join(dirname, filename), None, parentId)
        file_dict[dirname.split('\\')[-1] + filename] = file_id


