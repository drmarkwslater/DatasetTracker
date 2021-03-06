# Make this as compatible across Python 2 & 3 as possible
from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

# system imports
import argparse
import os
import sys

# --------------------------------------------------------------------
# run the main program
def main(arglist):
    """Process the given arg list and run the appropriate functions"""
    
    # parse the arguments
    parser = argparse.ArgumentParser(description='Track your datasets and files, what created them, when and from what')
    parser.add_argument('--dbpath', help='Set the DB path to something other than ~/.dstrk')

    # add subparser for initDB
    subparsers = parser.add_subparsers(help='Specific command help')
    parser_initdb = subparsers.add_parser('initDB', help='Initialise the DatasetTracker database. Defaults to ~/.dstrk')
    parser_initdb.set_defaults(func=initDB)
    
    # add subparser for addDS
    parser_addds = subparsers.add_parser('addDS', help='Create and add a Dataset from a filelist')
    parser_addds.add_argument('filelist', nargs="+", help='Globbed list of local files to add to the DS')
    parser_addds.add_argument('--parentDS', default=[], nargs="+", help='The hash of any parent datasets this is derived from')
    parser_addds.add_argument('--tags', default=[], action='append', help='Tag information to add to the entry for this DS')
    parser_addds.add_argument('--gitinfo', default=[], action='append',
                              help='Fill tags from the given git repo(s). Will run: git rev-parse HEAD, git rev-parse --abbrev-ref HEAD, git remote -v')
    parser_addds.set_defaults(func=addDS)

    # add subparser for DSinfo
    parser_dsinfo = subparsers.add_parser('DSinfo', help='Return dataset info given a file or dataset hash')
    parser_dsinfo.add_argument('file_or_hash', help='dataset file or hash to use to lookup the DS info')
    parser_dsinfo.set_defaults(func=DSinfo)

    # add subparser for DSinfo
    parser_tree = subparsers.add_parser('tree', help='show the hierachy of the given dataset')
    parser_tree.add_argument('file_or_hash', help='dataset file or hash to use to lookup the DS info')
    parser_tree.set_defaults(func=tree)

    # add subparser for addfiles
    parser_addfiles = subparsers.add_parser('addfiles', help='Add the given files to an existing dataset')
    parser_addfiles.add_argument('filelist', nargs="+", help='Globbed list of local files to add to the DS')
    parser_addfiles.add_argument('--dataset', help='dataset file or hash to add files to', required=True)
    parser_addfiles.set_defaults(func=addfiles)

    # add subparser for delDS
    parser_delds = subparsers.add_parser('delDS', help='Remove the given Dataset')
    parser_delds.add_argument('file_or_hash', help='dataset file or hash to use to lookup the DS info')
    parser_delds.set_defaults(func=delDS)

    # add subparser for delfiles
    parser_delds = subparsers.add_parser('delfiles', help='Remove the given files')
    parser_delds.add_argument('filelist', nargs="+", help='Globbed list of local files to remove from DB')
    parser_delds.set_defaults(func=delfiles)
    
    args = parser.parse_args(arglist)
    args.func(args)

# --------------------------------------------------------------------
def createDBObject(args):
    """Create the database object"""
    ds_base_path = "~/.dstrk"
    if args.dbpath:
        ds_base_path = args.dbpath
    
    from dstrk.database import DSDatabase
    return DSDatabase(os.path.expanduser(ds_base_path))

    
# --------------------------------------------------------------------
def initDB(args):
    """Initialise the Database"""
    ds = createDBObject(args)
    ds.init_db()

# --------------------------------------------------------------------
def addDS(args):
    """Add a Dataset to the DB"""
    ds = createDBObject(args)
    gitrepos = []
    for repo in args.gitinfo:
        gitrepos.append(os.path.abspath(os.path.expanduser(repo)))
    ds.add_ds(args.filelist, parents=args.parentDS, tags=args.tags, gitinfo=gitrepos)

# --------------------------------------------------------------------
def DSinfo(args):
    """get dataset info given file or hash"""
    ds = createDBObject(args)
    ds_info = ds.get_ds_info(args.file_or_hash)
    print("Datset Created:  {0}\n\nParents:  {1}\n\nDataset:  {2}\n\nTags:".format(ds_info['creation'], ' '.join(ds_info['parents']), ds_info['ds_hash']))
    for t in ds_info['tags']:
        print("{0}".format(t))
    print("\nFile List:")
    for f in ds_info['file_paths']:
        print("{0}".format(f))
    
# --------------------------------------------------------------------
def tree(args):
    """get tree info given file or hash"""
    ds = createDBObject(args)
    ds_tree = ds.get_ds_tree(args.file_or_hash)
    
    def print_leaf(ds_dict):
        max_depth = 0
        for ds in ds_dict['parents']:
            max_depth_temp = print_leaf(ds)
            print("     " * (max_depth+1) + "|")
            if max_depth_temp > max_depth:
                max_depth = max_depth_temp

        
        if len(ds_dict['parents']):
            max_depth += 1
            str_to_print = "     " * max_depth + "+--> " + ds_dict['ds_hash'] + "  {0}".format(ds_dict['tags'])
        else:
            str_to_print = ds_dict['ds_hash'] + "  {0}".format(ds_dict['tags'])
        print(str_to_print)
        return max_depth

    print_leaf(ds_tree)
    
# --------------------------------------------------------------------
def addfiles(args):
    """Add files to an existing dataset"""
    ds = createDBObject(args)
    ds.add_files(args.filelist, dataset=args.dataset)

# --------------------------------------------------------------------
def delDS(args):
    """Delete the dataset from the DB"""
    ds = createDBObject(args)
    ds.del_ds(args.file_or_hash)
    
# --------------------------------------------------------------------
def delfiles(args):
    """Delete the files from the DB"""
    ds = createDBObject(args)
    ds.del_files(args.filelist)
    
