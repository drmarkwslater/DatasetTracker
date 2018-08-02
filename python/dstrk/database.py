# Database class and related functions

# system imports
import os
from datetime import datetime
import hashlib
import glob

# DT imports
from dstrk.exceptions import DatabaseExists, DatabaseDoesNotExist, FileNotFound

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
        
    def write_hash_file(self, file_str, file_hash=''):
        """Write a hash file in the appropriate place given the contents"""
        if not file_hash:
            file_hash = hashlib.sha1(file_str).hexdigest()
            
        if not os.path.exists(os.path.join(self.db_base_path, file_hash[:2])):
            os.mkdir(os.path.join(self.db_base_path, file_hash[:2]))
            
        if not os.path.exists(os.path.join(self.db_base_path, file_hash[:2], file_hash[2:4])):
            os.mkdir(os.path.join(self.db_base_path, file_hash[:2], file_hash[2:4]))

        open(os.path.join(self.db_base_path, file_hash[:2], file_hash[2:4], file_hash), "w").write(file_str)
        return file_hash
    
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
        ds_file_str += "Creation:  " + datetime.now().isoformat() + "\n\n"

        # add the list of DS files
        ds_files = []
        for fname in filelist:
            ds_files += glob.glob(fname)
        ds_files = sorted(ds_files)
        if not ds_files:
            raise FileNotFound
        
        file_hash = {}
        for f in ds_files:
            file_hash[f] = hashlib.sha1(open(f, "rb").read()).hexdigest()
            ds_file_str += f + "  " + file_hash[f] + "\n"
            
        # hash the contents and create the file
        ds_hash = self.write_hash_file(ds_file_str)

        # create a hash for each of the given files
        for f in ds_files:
            file_str = "{0}\n\n{1}\n".format(ds_hash, f)
            self.write_hash_file(file_str, file_hash=file_hash[f])

