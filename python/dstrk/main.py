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
    parser.add_argument('command', metavar='cmd', choices=['initDB', 'addDS', 'addfiles', 'lsfiles', 'lstree'], help='command for Datset Tracker to run')
                    
    args = parser.parse_args(arglist)

    # do whatever we were asked to do
    if args.command == 'initDB':

        # Initialise the Database. Default is in ~/.dstrk
        ds_base_path = "~/.dstrk"
        from dstrk.database import DSDatabase
        ds = DSDatabase(os.path.expanduser(ds_base_path))
        ds.init_db()
        
    
