# Database class and related functions

# system imports
import os
from datetime import datetime
import hashlib
import glob
import subprocess

# DT imports
from dstrk.exceptions import DatabaseExists, DatabaseDoesNotExist, FileNotFound, NotValidFileOrHash, GitRepoDoesNotExist

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

    def write_ds_info(self, ds_info):
        """Modify the given dataset info file"""
        
        ds_file_str = ""

        # add creation time
        ds_file_str += "Creation:  " + ds_info['creation'] + "\n\n"

        # add parents
        ds_file_str += "Parents:  " + ' '.join(ds_info['parents']) + "\n\n"

        # add tags
        ds_file_str += "Tags:  \n"
        for tag in ds_info['tags']:
            ds_file_str += ' - ' + tag + "\n"
            
        ds_file_str += "\n"

        # add the list of DS files
        for i in range(0, len(ds_info['file_paths'])):
            ds_file_str += ds_info['file_paths'][i] + "  " + ds_info['file_hashes'][i] + "\n"
            
        # hash the contents and create the file
        ds_hash = self.write_hash_file(ds_file_str, ds_info['ds_hash'])
        return ds_hash
    
    def add_ds(self, filelist, parents=[], tags=[], file_hash={}, ds_hash='', gitinfo=[]):
        """Add the given dataset and all associated files"""

        self.check_db()

        ds_info = {}
        ds_info['creation'] = datetime.now().isoformat()
        ds_info['parents'] = parents

        # add tags
        ds_info['tags'] = tags
        
        for repo_path in gitinfo:
            if not os.path.exists(repo_path):
                raise GitRepoDoesNotExist
            tags.append( 'GIT HEAD: ' + subprocess.check_output("git -C {0} rev-parse HEAD".format(repo_path), shell=True).strip())
            tags.append( 'GIT Branch: ' + subprocess.check_output("git -C {0} rev-parse --abbrev-ref HEAD".format(repo_path), shell=True).strip())
            tags.append( 'GIT Remote: ' + subprocess.check_output("git -C {0} remote -v".format(repo_path), shell=True).replace('\n', ' ').strip())
            tags.append( 'GIT Path: ' + repo_path)
            
        # add the list of DS files
        ds_files = []
        for fname in filelist:
            ds_files += glob.glob(fname)
        ds_files = sorted(ds_files)
        if not ds_files:
            raise FileNotFound

        ds_info['file_paths'] =[]
        ds_info['file_hashes'] =[]
        for f in ds_files:
            if not f in file_hash:
                file_hash[f] = hashlib.sha1(open(f, "rb").read()).hexdigest()

            ds_info['file_paths'].append(f)
            ds_info['file_hashes'].append(file_hash[f])
            
        # hash the contents and create the file
        ds_info['ds_hash'] = ds_hash
        ds_hash = self.write_ds_info(ds_info)
        
        # create a hash for each of the given files
        for f in ds_files:
            # check if we have a duplicate file
            file_info = self.get_file_info(f, file_hash[f])
            if file_info:
                # attempting to add file to same ds
                if ds_hash in file_info['ds']:
                    continue
                
                print("WARNING: File {0} already present in dataset(s) {1}".format(f, file_info['ds']))
                file_info['ds'].insert(0, ds_hash)
                file_str = "{0}\n{1}\n".format(" ".join(file_info['ds']), f)
            else:
                file_str = "{0}\n{1}\n".format(ds_hash, f)
                
            self.write_hash_file(file_str, file_hash=file_hash[f])

    def get_file_info(self, fname, file_hash=""):
        """get the file info of the given file"""
        
        # do we have a valid file?
        if not os.path.exists(fname) and not file_hash:
            return {}

        # what is it's hash?
        if not file_hash:
            file_hash = hashlib.sha1(open(fname, "rb").read()).hexdigest()
        
        # open the file info
        if not os.path.exists( os.path.join(self.db_base_path, file_hash[:2], file_hash[2:4], file_hash) ):
            return {}

        file_info_lines = open( os.path.join(self.db_base_path, file_hash[:2], file_hash[2:4], file_hash) ).readlines()
        file_info = {'ds':[], 'path':file_info_lines[1].strip(), 'hash':file_hash}
        for ds in file_info_lines[0].split():
            file_info['ds'].append(ds.strip())
            
        return file_info
        
    def find_ds_from_file(self, fname):
        """return the hash of a DS given the file"""

        # do we know about it?
        file_info = self.get_file_info(fname)
        if not file_info:
            return ''

        if len(file_info['ds']) > 1:
            print("WARNING: File {0} present in multiple datasets ({1}). Assuming latest one ({2})".format(fname, file_info['ds'], file_info['ds'][0]))
        return file_info['ds'][0]

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
        
        return os.path.basename(hash_list[0])
    
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

    def add_files(self, filelist, dataset):
        """Add the given files to the given dataset"""

        # first, does the dataset exist?
        ds_info = self.get_ds_info(dataset)

        if not ds_info:
            raise NotValidFileOrHash

        ds_info['file_paths'] += filelist
        file_hash = {}
        for i in range(0, len(ds_info['file_hashes'])):
            file_hash[ ds_info['file_paths'][i] ] = ds_info['file_hashes'][i]

        self.add_ds(ds_info['file_paths'], parents=ds_info['parents'], tags=ds_info['tags'], file_hash=file_hash, ds_hash=ds_info['ds_hash'])
        
    def del_ds(self, file_or_hash):
        """Delete the given dataset from the DB"""

        # first, does the dataset exist?
        ds_info = self.get_ds_info(file_or_hash)

        # clear out DS info from the files
        for fhash in ds_info['file_hashes']:
            file_info = self.get_file_info('', file_hash=fhash)
            file_info['ds'].remove(ds_info["ds_hash"])
            if len(file_info['ds']) == 0:
                # no other datasets so remove it
                os.remove(os.path.join(self.db_base_path, file_hash[:2], file_hash[2:4], file_hash))
            else:
                # re-write the info file with this change
                file_str = "{0}\n{1}\n".format(" ".join(file_info['ds']), file_info['path'])
                self.write_hash_file(file_str, file_hash=fhash)

        # finally, remove the DS entry
        os.remove(os.path.join(self.db_base_path, ds_info['ds_hash'][:2], ds_info['ds_hash'][2:4], ds_info['ds_hash']))
    
    def del_files(self, filelist):
        """Remove these files from the DB"""

        # glob the files and check if they all exist
        all_files = []
        for fname in filelist:
            all_files +=  glob.glob(fname)

        if not all_files:
            raise FileNotFound

        # now remove each one
        ds_list = []
        all_file_info = []
        for fname in all_files:
            file_info = self.get_file_info(fname)
            all_file_info.append((file_info['path'], file_info['hash']))
            
            # keep track of the datasets to check afterwards
            ds_list += file_info['ds']

            # remove the file info
            os.remove(os.path.join(self.db_base_path, file_info['hash'][:2], file_info['hash'][2:4], file_info['hash']))
            
        # remove duplicate DS checks
        ds_list = list(set(ds_list))

        for ds in ds_list:
            ds_info = self.get_ds_info(ds)

            for finfo in all_file_info:
                ds_info['file_paths'].remove(finfo[0])
                ds_info['file_hashes'].remove(finfo[1])

            if len(ds_info['file_paths']) == 0:
                # the DS has no more files, remove it
                os.remove(os.path.join(self.db_base_path, ds_info['ds_hash'][:2], ds_info['ds_hash'][2:4], ds_info['ds_hash']))
            else:
                # otherwise, rewrite the ds_info file
                self.write_ds_info(ds_info)
