# Database class and related functions

# system imports
import os
from datetime import datetime
import hashlib

# DT imports
from dstrk.exceptions import DatabaseExists, DatabaseDoesNotExist

# -----------------------------------------------------------------------------
# class to handle all DB operations
class DSDatabase:
    def __init__(self, db_base_path):
        assert db_base_path
        self.db_base_path = db_base_path

    def check_db(self):
        """Check that the DB is present"""
        if not os.path.exists(self.db_base_path):
            raise DatabaseDoesNotExist
        
    def write_hash_file(self, file_contents):
        """Write a hash file in the appropriate place given the contents"""
        file_hash = hashlib.sha1(file_contents).hexdigest()
        if not os.path.exists(os.path.join(self.db_base_path, file_hash[:2])):
            os.mkdir(os.path.join(self.db_base_path, file_hash[:2]))
            
        if not os.path.exists(os.path.join(self.db_base_path, file_hash[:2], file_hash[2:4])):
            os.mkdir(os.path.join(self.db_base_path, file_hash[:2], file_hash[2:4]))

        open(os.path.join(self.db_base_path, file_hash[:2], file_hash[2:4], file_hash), "w").write(file_contents)

    def init_db(self):
        """Initialise the database at the given location
        Note: This will throw an exception if DB exists"""

        # is there a DB already?
        if os.path.exists(self.db_base_path):
            raise DatabaseExists
        
        # create the dir
        os.mkdir(self.db_base_path)

    def add_ds(self, filelist, parents=[], tags=[]):
        """Add the given dataset and all associated files"""

        self.check_db()
        
        ds_file_str = ""

        # add creation time
        ds_file_str += "Creation:  " + datetime.now().isoformat()

        # hash the contents and create the file
        self.write_hash_file(ds_file_str)

        
