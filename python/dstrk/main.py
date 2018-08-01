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
    parser_addds.add_argument('filelist', help='Globbed list of local files to add to the DS')
    parser_addds.add_argument('--parentDS', nargs="+", help='The hash of any parent datasets this is derived from')
    parser_addds.add_argument('--tags', help='Tag information to add to the entry for this DS')
    parser_addds.set_defaults(func=addDS)
    
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
    ds.add_ds(args.filelist, parents=args.parentDS, tags=args.tags)
    
    
