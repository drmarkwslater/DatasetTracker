# A list of dstrk exceptions

class DatabaseExists(Exception):
    pass

class DatabaseDoesNotExist(Exception):
    pass

class FileNotFound(Exception):
    pass

class NotValidFileOrHash(Exception):
    pass

class GitRepoDoesNotExist(Exception):
    pass
