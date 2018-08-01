# system imports
import pytest
import os
import shutil

# setup/teardown functions
def setup_module(module):
    test_db_path = os.path.expanduser("~/.dstrk-test")
    if os.path.exists(test_db_path):
        shutil.rmtree(test_db_path)

    # create some test data
    test_data_path = os.path.expanduser("~/.dstrk-test-data")
    if os.path.exists(test_data_path):
        shutil.rmtree(test_data_path)
    os.mkdir(test_data_path)
    for i in range(1, 4):
        os.mkdir(os.path.join(test_data_path, "step_{0}".format(i)))
        for j in range(1, 4):
            open(os.path.join(test_data_path, "step_{0}".format(i), "part{0}.txt".format(j)), "w").write("Data file Step {0} Part {1}".format(i, j))
         
def teardown_module(module):
    if os.path.exists(os.path.expanduser("~/.dstrk-test")):
        shutil.rmtree(os.path.expanduser("~/.dstrk-test"))
        
    if os.path.exists(os.path.expanduser("~/.dstrk-test-data")):
        shutil.rmtree(os.path.expanduser("~/.dstrk-test-data"))
        
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
    dstrk.main.main(['--dbpath', '~/.dstrk-test', 'initDB'])
    assert os.path.exists(os.path.expanduser('~/.dstrk-test'))
    
def test_init_db_already_present():
    import dstrk.main
    from dstrk.exceptions import DatabaseExists
    with pytest.raises(DatabaseExists):
        dstrk.main.main(['--dbpath', '~/.dstrk-test', 'initDB'])
    assert os.path.exists(os.path.expanduser('~/.dstrk-test'))
            
def test_add_dataset_req_args():
    import dstrk.main
    with pytest.raises(SystemExit) as pytest_e:
        dstrk.main.main(['--dbpath', '~/.dstrk-test', 'addDS'])
    assert pytest_e.value.code == 2

def test_add_dataset_no_db():
    import dstrk.main
    from dstrk.exceptions import DatabaseDoesNotExist
    with pytest.raises(DatabaseDoesNotExist) as pytest_e:
        dstrk.main.main(['--dbpath', '~/.dstrk-test-not-present', 'addDS', '~/dstrk-tests/step_1/*.txt', '--tags', 'First Step'])

def test_add_dataset_step_1():
    import dstrk.main
    dstrk.main.main(['--dbpath', '~/.dstrk-test', 'addDS', '~/dstrk-tests/step_1/*.txt', '--tags', 'First Step'])
    
#def test_add_files():
#    raise Exception

#def test_ls_tree():
#    raise Exception

#def test_ls_files():
#    raise Exception
