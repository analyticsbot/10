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
EXCLUDE_FILE_EXTENSIONS = [''] #.jpg # extensions to be exlcluded
folder_id = {}

def uploadFiles(filename, mimeType, parentId):
    """Function to upload files"""
    metadata = {'name': filename, 'parents': [parentId]}
    if mimeType:
        metadata['mimeType'] = mimeType
    res = DRIVE.files().create(body=metadata, media_body=filename).execute()
    if res:
        print('UPLOADED "%s"' % (filename))

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
##for dirname, dirnames, filenames in os.walk(MAIN_FOLDER):
##    # create sub dirs
##    for subdirname in dirnames:
##        print ("FOUND DIRECTORY: ", (os.path.join(dirname, subdirname)))
##        old_dirname = dirname
##        dirname = dirname.split('\\')[-1]
##        parentId = folder_id.get(dirname, None)
##        print (parentId)
##        print (dirname)
##        id = createRemoteFolder(subdirname, parentId)
##        folder_id[subdirname] = id
##
##    # upload files to respected dirs
##    for filename in filenames:
##        print ("FOUND FILE: ", os.path.join(curFolder, filename))
##        filename_s, file_extension = os.path.splitext(os.path.join(dirname, filename))
##        old_dirname = dirname
##        dirname = dirname.split('\\')[-1]
##        parentId = folder_id.get(dirname, None)
##        print (parentId)
##        print (dirname)
##        if file_extension.lower() not in EXCLUDE_FILE_EXTENSIONS:
##            url = urllib.pathname2url(filename)
##            try:
##                mimeType = mimetypes.guess_type(url)[0]
##            except:
##                mimeType = None
##            print (filename, mimeType, file_extension)
##            uploadFiles(filename, None, parentId)
##
##    if dirname != MAIN_FOLDER:
##        curFolder = os.path.join(curFolder, dirname)
        

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
        uploadFiles(os.path.join(dirname, filename), None, parentId)



