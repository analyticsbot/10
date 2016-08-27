import sys
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive

gpath = '2015'
fname = 'hello.txt'

gauth = GoogleAuth()
gauth.LocalWebserverAuth('client_secrets.json', port_numbers=[8010, 8020])
drive = GoogleDrive(gauth)

def createRemoteFolder(folderName, parentID = None):
        # Create a folder on Drive, returns the newely created folders ID
        body = {
          'title': folderName,
          'mimeType': "application/vnd.google-apps.folder"
        }
        if parentID:
            body['parents'] = [{'id': parentID}]
        root_folder = drive_service.files().insert(body = body).execute()
        return root_folder['id']

id = createRemoteFolder(gpath)
print id
file_list = drive.ListFile({'q': "'root' in parents and trashed=false"}).GetList()
for file1 in file_list:
    if file1['title'] == gpath:
        id = file1['id']

file1 = drive.CreateFile({'title': fname, 
    "parents":  [{"id": id}], 
    "mimeType": "application/vnd.google-apps.folder"})

file1.SetContentFile(fname)
file1.Upload()
