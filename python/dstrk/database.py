# Database class and related functions

# system imports
import os

# DT imports
import dstrk.exceptions

# -----------------------------------------------------------------------------
# class to handle all DB operations
class DSDatabase:
    def __init__(self, db_base_path):
        self.db_base_path_ = db_base_path

    def init_db(self):
        """Initialise the database at the given location
        Note: This will wipe any previous DB in this location"""
        pass
    
# -----------------------------------------------------------------------------
# helper functions
def create(db_base_path):
    """create the DS database
    
     - Raises exception if DB already exists
    """
    if os.path.exists(db_base_path):
        raise dstrak.DatabaseExists

    # setup DB and initialise
    db = DSDatabase(db_base_path)
    db.init_db()
    
    return db
