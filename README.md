# __Upload files to/from google drive__

### In order to interact with gdrive we need to 
1. Create a project in google cloud platform
123. Create a service account and a 
312. Add a principal and grant access with a role that has permission, e.g.: Editor role
132. Enable google Drive Api in our project
321. Create and place the key into uploadFile.py -> SERVICE_ACCOUNT='...'
123. Arguments:   

        - file: path to the file to be uploaded e.g.: 'resources/kitty.jpg' 

        - name: new name of the file when uploaded e.g.: 'hellokaity.jpg'

        -  path: path to target folder to be uploaded.There has to be at least one subfolder and the root shared folder must exist and be correct. e.g.: 'parentfolder/targetfolder or Statistics/MENSUEL MONTHLY/2022/01_2022'
    




#### Upload file  
> `python3 GoogleDriveAdapter.py resources/kitty.jpg helloKaitty.jpg kittyhome/kittyharem`

#### Use GdriveAdapter
    from GoogleDriveAdapter import GdriveAdapter

    gdriveAdapter = GdriveAdapter()
    gdriveAdapter.createDirectory(path)
    gdriveAdapter.uploadFile(file, name, path)
    