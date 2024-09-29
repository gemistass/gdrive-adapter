class PathException(Exception):
    """Exception raised when given folder to upload doesnt now exist
    """

    def __init__(self, path):
        self.message = f'\nPath {path} does not exist! Please create the directory'
        super().__init__(self.message)


class RootFolderException(PathException):
    """Exception raised when given root shared folder is incorrect
    """

    def __init__(self, message='\nWrong root folder given!'):
        self.message = message
        super().__init__(self.message)
