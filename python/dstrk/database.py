# Database class and related functions

# system imports
import os

# DT imports
from dstrk.exceptions import DatabaseExists

# -----------------------------------------------------------------------------
# class to handle all DB operations
class DSDatabase:
    def __init__(self, db_base_path):
        assert db_base_path
        self.db_base_path = db_base_path

    def init_db(self):
        """Initialise the database at the given location
        Note: This will throw an exception if DB exists"""

        # is there a DB already?
        if os.path.exists(self.db_base_path):
            raise DatabaseExists
        
        # create the dir
        os.mkdir(self.db_base_path)
        
