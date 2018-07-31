# system imports
import pytest
import os

# setup/teardown functions
def setup_module(module):
    if os.path.exists(os.path.expanduser("~/.dstrk-test")):
        os.rmdir(os.path.expanduser("~/.dstrk-test"))

def teardown_module(module):
    if os.path.exists(os.path.expanduser("~/.dstrk-test")):
        os.rmdir(os.path.expanduser("~/.dstrk-test"))

# Test all the main function
def test_main_import():
    import dstrk.main

def test_no_options():
    import dstrk.main
    with pytest.raises(SystemExit) as pytest_e:
        dstrk.main.main([])
    assert pytest_e.value.code == 2

def test_help_1():
    import dstrk.main
    with pytest.raises(SystemExit) as pytest_e:
        dstrk.main.main(["-h"])
    assert pytest_e.value.code == 0

def test_help_2():
    import dstrk.main
    with pytest.raises(SystemExit) as pytest_e:
        dstrk.main.main(["--help"])
    assert pytest_e.value.code == 0
        
def test_init_db():
    import dstrk.main
    dstrk.main.main(['initDB', '--dbpath', '~/.dstrk-test'])
    assert os.path.exists(os.path.expanduser('~/.dstrk-test'))
    
def test_init_db_already_present():
    import dstrk.main
    from dstrk.exceptions import DatabaseExists
    with pytest.raises(DatabaseExists):
        dstrk.main.main(['initDB', '--dbpath', '~/.dstrk-test'])
    assert os.path.exists(os.path.expanduser('~/.dstrk-test'))
    
        
#def test_add_dataset():
#    raise Exception

#def test_add_files():
#    raise Exception

#def test_ls_tree():
#    raise Exception

#def test_ls_files():
#    raise Exception
