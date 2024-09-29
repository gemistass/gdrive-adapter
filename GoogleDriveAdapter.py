from http.client import responses
from google.oauth2 import service_account
from googleapiclient.errors import HttpError
from googleapiclient.discovery import build
import googleapiclient.http
import googleapiclient.discovery
import json
import time
import sys
from PathException import *


class GdriveAdapter:
    # IMPORTANT! Need to  assign the service account
    SERVICE_ACCOUNT = '{"type":"service_account","project_id":"exploring-limgrave","private_key_id":"...."}'
    OAUTH2_SCOPE = ["https://www.googleapis.com/auth/drive"]

    # initialize the adapter and create the google drive service

    def __init__(self):
        config = json.loads(self.SERVICE_ACCOUNT, strict=False)
        credentials = service_account.Credentials.from_service_account_info(
            config,).with_scopes(self.OAUTH2_SCOPE)

        self.drive_service = build("drive", "v3", credentials=credentials)

    # find the id of the target folder
    def getFolderId(self, path):
        print(f'Seeking path: {path} ...')
        files = path.split("/")

        parentFolder = files[len(files)-2]
        targetFolder = files[len(files)-1]

        drive_service = self.drive_service
        page_token = None
        allresponses = list()
        # query Drive API for folder
        while True:
            response = (
                drive_service.files()
                .list(
                    q=f"mimeType = 'application/vnd.google-apps.folder' and ((name = '{parentFolder}' or name = '{targetFolder}'))",
                    spaces="drive",
                    fields="nextPageToken, files(id, name, parents)",
                    pageToken=page_token,
                )
                .execute()
            )
            allresponses.append(response)
            page_token = response.get("nextPageToken", None)
            if page_token is None:
                break
        # find id of the {targetfolder} that has {parentfolder}. Throw error if path does not exist
        targetFolderToSaveId = None
        for response in allresponses:
            for file in response.get("files", []):
                if(file.get('name') == targetFolder):
                    targetFolderId = file.get('id')
                    parentFolderId = file.get('parents')[0]
                    for file in response.get('files', []):
                        if((file.get('name') == parentFolder) & (file.get('id') == parentFolderId)):
                            targetFolderToSaveId = targetFolderId
                            parentFolderToSaveName = file.get('name')
                            print(
                                f'Folder found!  {parentFolderToSaveName} with id: {targetFolderToSaveId} ')
                            break
        if targetFolderToSaveId is None:
            raise PathException(path)
        return targetFolderToSaveId

    # upload the file found in filepath
    """
    :param str file: path to the file to be uploaded
        e.g.: 'resources/kitty.jpg'
    :param str name: new name of the file when uploaded
        e.g.: 'hellokaity.jpg'
    :param str path: path to target folder to be uploaded.There has to be at least one subfolder!!
        e.g.: 'parentfolder/targetfolder or Statistics/MENSUEL MONTHLY/2022/01_2022'
    """

    def uploadFileToFolder(self, filepath, newfilename, folderId):
        print('Uploading...')
        drive_service = self.drive_service

        # ------try to upload
        try:
            file_metadata = {"name": newfilename, "parents": [folderId]}
            media = googleapiclient.http.MediaFileUpload(
                filepath, resumable=True
            )
            new_file = (
                drive_service.files()
                .create(body=file_metadata, media_body=media, fields="id, name")
                .execute()
            )
            print(
                f'File uploaded with success! file: {filepath} uploaded at folder with id: {folderId} as {newfilename} ')
        except HttpError as error:
            print(f'Error occurred while trying to upload: {error}')

    def uploadFile(self, file, name, path):
        """
        find the folder id and upload thre
        """
        folderId = self.getFolderId(path)
        self.uploadFileToFolder(file, name, folderId)

    splittedGivenPath = []
    gDriveFolders = []

    def createDirectory(self, path):
        drive_service = self.drive_service
        self.splitedGivenPath = path.split("/")
        allresponses = list()

        # query Drive API for folder tree
        page_token = None
        while True:
            response = (
                drive_service.files()
                .list(
                    q=f"mimeType = 'application/vnd.google-apps.folder'",
                    spaces="drive",
                    fields="nextPageToken, files(id, name, parents)",
                    pageToken=page_token,
                )
                .execute()
            )
            allresponses.append(response.get('files'))
            page_token = response.get("nextPageToken", None)
            if page_token is None:
                break
        self.gDriveFolders = allresponses
        self.__createFolderByPath(self.splitedGivenPath)

    #
    def __createThisFolder(self, folderName, parentId):
        """
        Create folder with passed name: [folderName] at target folder: [parentId]
        """

        file_metadata = {
            'name': folderName,
            'mimeType': 'application/vnd.google-apps.folder',
            'parents': [parentId]
        }
        file = self.drive_service.files().create(body=file_metadata,
                                                 fields='id, name').execute()

        time.sleep(0.5)
        print(
            f'Folder:{file.get("name")} created!. Folder ID is: {file.get("id")} ')
        return file.get('id')

    def __isRoot(self, foldername):
        """
        Check if the root, shared folder is correct
        """
        for folder in self.gDriveFolders[0]:
            if(folder.get('name') == foldername):
                return folder.get('id')
        raise RootFolderException()

    def __findParentOfgivenChildFolder(self, givenfolder, parentId):
        """
        Check it the given folder:[givenfolder] exists inside parent folder: [parentId]
        """
        for gfolder in self.gDriveFolders[0]:
            if gfolder.get('parents') is None:
                continue
            if (gfolder.get('name') == givenfolder) & (gfolder.get('parents')[0] == parentId):
                return gfolder.get('id')
        return None

    def __createFolderByPath(self, splittedInputPath):
        """
        Create the folder of the path as given in [splittedInputPath]
        """
        parentid = None
        depth = 0

        parentid = self.__isRoot(splittedInputPath[depth])
        depth += 1
        while (depth < len(splittedInputPath)):

            parentIdIfchildExists = self.__findParentOfgivenChildFolder(
                splittedInputPath[depth], parentid)
            if parentIdIfchildExists is None:
                parentid = self.__createThisFolder(
                    splittedInputPath[depth], parentid)
            else:
                parentid = parentIdIfchildExists
            depth += 1


# entrypoint
if __name__ == "__main__":

    path = 'SHARED_ROOT/STATISTICS/'
    name = 'newname.xlsx'
    file = 'resources/fileToUpload.xlsx'

    if(len(sys.argv) == 3):
        path = sys.argv[3]
        name = sys.argv[2]
        file = sys.argv[1]
    else:
        print('Please pass arguments: file to upload, name of uploaded file, google drive path to FOLDER')
    gdriveAdapter = GdriveAdapter()
    try:
        gdriveAdapter.uploadFile(file, name, path)
    except PathException:
        gdriveAdapter.createDirectory(path)
        gdriveAdapter.uploadFile(file, name, path)
