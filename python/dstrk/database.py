# Database class and related functions

# system imports
import os
from datetime import datetime
import hashlib
import glob

# DT imports
from dstrk.exceptions import DatabaseExists, DatabaseDoesNotExist, FileNotFound, NotValidFileOrHash

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

        # add parents
        ds_file_str += "Parents:  " + ' '.join(parents) + "\n\n"

        # add tags
        ds_file_str += "Tags:  \n"
        for tag in tags:
            ds_file_str += ' - ' + tag + "\n"
        ds_file_str += "\n"
        
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

    def get_file_info(self, fname):
        """get the file info of the given file"""
        
        # do we have a valid file?
        if not os.path.exists(fname):
            return {}

        # what is it's hash?
        file_hash = hashlib.sha1(open(fname, "rb").read()).hexdigest()

        # open the file info
        if not os.path.exists( os.path.join(self.db_base_path, file_hash[:2], file_hash[2:4], file_hash) ):
            return {}

        file_info_str = open( os.path.join(self.db_base_path, file_hash[:2], file_hash[2:4], file_hash) ).read()
        file_info = {'ds':file_info_str.split()[0].strip(), 'path':file_info_str.split()[1].split(), 'hash':file_hash}
        return file_info
        
    def find_ds_from_file(self, fname):
        """return the hash of a DS given the file"""

        # do we know about it?
        file_info = self.get_file_info(fname)
        if not file_info:
            return ''
        return file_info['ds']

    def check_ds_hash(self, ds_hash):
        """check that a ds hash is valid"""
        return os.path.exists(os.path.join(self.db_base_path, ds_hash[:2], ds_hash[2:4], ds_hash))

    def expand_hash(self, ds_hash):
        """Expand the given hash if we can, otherwise return nothing"""
        if len(ds_hash) < 7:
            return ''

        # do we have the directory?
        if not os.path.exists(os.path.join(self.db_base_path, ds_hash[:2], ds_hash[2:4])):
            return ''

        # can we match any files?
        hash_list = glob.glob(os.path.join(self.db_base_path, ds_hash[:2], ds_hash[2:4], ds_hash+'*'))
        if len(hash_list) == 0:
            return ''
        elif len(hash_list) != 1:
            return hash
        
        return hash_list[0]
    
    def get_ds_hash_from_file_or_hash(self, file_or_hash):
        """Given a filename or ds hash, return the ds hash if found
        This will expand hashes as well"""
        
        # attempt to find the DS hash
        ds_hash = self.find_ds_from_file(file_or_hash)
        if not ds_hash:
            temp_hash = self.expand_hash(file_or_hash)
            if file_or_hash[0] == '/' or not self.check_ds_hash(temp_hash):
                ds_hash = ''
            else:
                ds_hash = temp_hash

        return ds_hash
            
    def get_ds_info(self, file_or_hash):
        """return the dataset given a file or hash"""

        ds_hash = self.get_ds_hash_from_file_or_hash(file_or_hash)
        if not ds_hash:
            raise NotValidFileOrHash
        
        # we have the DS hash so return the info
        ds_info = {'file_paths':[], 'file_hashes':[], 'ds_hash': ds_hash, 'parents': [], 'tags': []}
        for ln in open( os.path.join(self.db_base_path, ds_hash[:2], ds_hash[2:4], ds_hash)).readlines():
            if ln.startswith("Creation"):
                ds_info['creation'] = ' '.join(ln.split()[1:]).strip()
            elif ln.startswith("Parents"):
                ds_info['parents'] = ln.split()[1:]
            elif ln.startswith("Tags"):
                continue
            elif ln.startswith(" - "):
                ds_info['tags'].append(ln[3:].strip())
            elif len(ln) > 4:
                # file list
                ds_info['file_paths'].append( ln.split()[0].strip() )
                ds_info['file_hashes'].append( ln.split()[1].strip() )
            
        return ds_info

    def get_ds_tree(self, file_or_hash):
        """Return a dictionary that contains the tree info for the given dataset"""

        ds_hash = self.get_ds_hash_from_file_or_hash(file_or_hash)
        if not ds_hash:
            raise NotValidFileOrHash

        # grab the info
        def get_parent_info(ds_hash):
            ds_info = self.get_ds_info(ds_hash)
            tree_info = {'ds_hash':ds_hash, 'parents':[], 'tags':ds_info['tags']}
            for ds in ds_info['parents']:
                tree_info['parents'].append( get_parent_info(ds) )
            return tree_info
        
        return get_parent_info(ds_hash)
