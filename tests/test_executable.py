# system imports
import pytest
import os
import shutil

test_db_path = os.path.expanduser("~/.dstrk-test")
test_data_path = os.path.expanduser("~/.dstrk-test-data")
test_data_step1 = os.path.join(test_data_path, "step_1", "*.txt")
test_data_step2 = os.path.join(test_data_path, "step_2", "*.txt")
test_data_step3 = os.path.join(test_data_path, "step_3", "*.txt")
ds_hash_step1 = ''
ds_hash_step2 = ''
ds_hash_step3 = ''

# setup/teardown functions
def setup_module(module):
    if os.path.exists(test_db_path):
        shutil.rmtree(test_db_path)

    # create some test data
    if os.path.exists(test_data_path):
        shutil.rmtree(test_data_path)
    os.mkdir(test_data_path)
    for i in range(1, 6):
        os.mkdir(os.path.join(test_data_path, "step_{0}".format(i)))
        for j in range(1, 4):
            open(os.path.join(test_data_path, "step_{0}".format(i), "part{0}.txt".format(j)), "w").write("Data file Step {0} Part {1}".format(i, j))
         
def teardown_module(module):
    if os.path.exists(test_db_path):
        shutil.rmtree(test_db_path)

    #if os.path.exists(test_data_path):
    #    shutil.rmtree(test_data_path)
        
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
    dstrk.main.main(['--dbpath', test_db_path, 'initDB'])
    assert os.path.exists(os.path.expanduser(test_db_path))
    
def test_init_db_already_present():
    import dstrk.main
    from dstrk.exceptions import DatabaseExists
    with pytest.raises(DatabaseExists):
        dstrk.main.main(['--dbpath', test_db_path, 'initDB'])
    assert os.path.exists(os.path.expanduser(test_db_path))
            
def test_add_dataset_req_args():
    import dstrk.main
    with pytest.raises(SystemExit) as pytest_e:
        dstrk.main.main(['--dbpath', test_db_path, 'addDS'])
    assert pytest_e.value.code == 2

def test_add_dataset_no_db():
    import dstrk.main
    from dstrk.exceptions import DatabaseDoesNotExist
    with pytest.raises(DatabaseDoesNotExist) as pytest_e:
        dstrk.main.main(['--dbpath', '~/.dstrk-test-not-present', 'addDS', test_data_step1, '--tags', 'First Step'])

def test_add_dataset_no_files():
    import dstrk.main
    from dstrk.exceptions import DatabaseDoesNotExist
    with pytest.raises(SystemExit) as pytest_e:
        dstrk.main.main(['--dbpath', '~/.dstrk-test-not-present', 'addDS'])
    assert pytest_e.value.code == 2

def test_add_dataset_files_not_existing():
    import dstrk.main
    from dstrk.exceptions import FileNotFound
    with pytest.raises(FileNotFound) as pytest_e:
        dstrk.main.main(['--dbpath', test_db_path, 'addDS', '/no/existing/files', '--tags', 'First Step'])

def test_add_dataset_step_1():
    import dstrk.main
    dstrk.main.main(['--dbpath', test_db_path, 'addDS', test_data_step1, '--tags', 'First Step'])

    # check all files have been hashed
    assert os.path.exists( os.path.join(test_db_path, "72", "c3", "72c3e6964b6f85d30013fb0e51b525597d393e7c") )
    assert os.path.exists( os.path.join(test_db_path, "14", "da", "14da01205db55e211b36888f251a4e86cdf55332") )
    assert os.path.exists( os.path.join(test_db_path, "1e", "5b", "1e5b6e59b6b44412b8ca4d306c9c66064f40be09") )

def test_get_ds_info_no_arg():
    import dstrk.main
    with pytest.raises(SystemExit) as pytest_e:
        dstrk.main.main(['--dbpath', test_db_path, 'DSinfo'])
    assert pytest_e.value.code == 2

def test_get_ds_info_bad_arg():
    import dstrk.main
    from dstrk.exceptions import NotValidFileOrHash
    with pytest.raises(NotValidFileOrHash) as pytest_e:
        dstrk.main.main(['--dbpath', test_db_path, 'DSinfo', 'something_or_other'])

def test_get_ds_info_bad_file():
    import dstrk.main
    from dstrk.exceptions import NotValidFileOrHash
    with pytest.raises(NotValidFileOrHash) as pytest_e:
        dstrk.main.main(['--dbpath', test_db_path, 'DSinfo', os.path.join(test_data_path, "step_2", "part1.txt")])
    
def test_get_ds_info():
    import dstrk.main
    from dstrk.database import DSDatabase
    filelist = DSDatabase(test_db_path).get_ds_info(os.path.join(test_data_path, "step_1", "part1.txt"))['file_paths']
    assert filelist == [os.path.join(test_data_path, "step_1", "part1.txt"),
                        os.path.join(test_data_path, "step_1", "part2.txt"),
                        os.path.join(test_data_path, "step_1", "part3.txt")]
    hashlist = DSDatabase(test_db_path).get_ds_info(os.path.join(test_data_path, "step_1", "part1.txt"))['file_hashes']
    assert hashlist == ["1e5b6e59b6b44412b8ca4d306c9c66064f40be09",
                        "14da01205db55e211b36888f251a4e86cdf55332",
                        "72c3e6964b6f85d30013fb0e51b525597d393e7c"]
    dstrk.main.main(['--dbpath', test_db_path, 'DSinfo', os.path.join(test_data_path, "step_1", "part1.txt")])

def test_add_dataset_step_2():
    import dstrk.main
    from dstrk.database import DSDatabase
    global ds_hash_step1
    
    ds_hash_step1 = DSDatabase(test_db_path).get_ds_info(os.path.join(test_data_path, "step_1", "part1.txt"))['ds_hash']
    dstrk.main.main(['--dbpath', test_db_path, 'addDS', test_data_step2, '--tags', 'Second Step', '--parentDS', ds_hash_step1])

    # check all files have been hashed
    assert os.path.exists( os.path.join(test_db_path, "4f", "80", "4f808fb01a070adffc47ebc40aa63d9c0b0d2504") )
    assert os.path.exists( os.path.join(test_db_path, "90", "00", "90008b458c876ea73f1da15cf79b56bcf2bd383a") )
    assert os.path.exists( os.path.join(test_db_path, "8c", "21", "8c21a6f741ff5cd525785dedff454bc33cbf58f8") )

def test_get_ds_info_parent():
    import dstrk.main
    from dstrk.database import DSDatabase
    global ds_hash_step1, ds_hash_step2
    
    filelist = DSDatabase(test_db_path).get_ds_info(os.path.join(test_data_path, "step_2", "part1.txt"))['file_paths']
    assert filelist == [os.path.join(test_data_path, "step_2", "part1.txt"),
                        os.path.join(test_data_path, "step_2", "part2.txt"),
                        os.path.join(test_data_path, "step_2", "part3.txt")]
    hashlist = DSDatabase(test_db_path).get_ds_info(os.path.join(test_data_path, "step_2", "part1.txt"))['file_hashes']
    assert hashlist == ["4f808fb01a070adffc47ebc40aa63d9c0b0d2504",
                        "90008b458c876ea73f1da15cf79b56bcf2bd383a",
                        "8c21a6f741ff5cd525785dedff454bc33cbf58f8"]
    ds_hash_step2 = DSDatabase(test_db_path).get_ds_info(os.path.join(test_data_path, "step_2", "part1.txt"))['ds_hash']

    assert DSDatabase(test_db_path).get_ds_info(os.path.join(test_data_path, "step_2", "part1.txt"))['parents'][0] == ds_hash_step1
    dstrk.main.main(['--dbpath', test_db_path, 'DSinfo', os.path.join(test_data_path, "step_2", "part1.txt")])

def test_add_dataset_step_3():
    import dstrk.main
    from dstrk.database import DSDatabase
    global ds_hash_step2, ds_hash_step3
    
    ds_hash_step3 = dstrk.main.main(['--dbpath', test_db_path, 'addDS', test_data_step3, '--tags', 'Third Step', '--tags',
                                     'More third step info' ,'--parentDS', ds_hash_step2, ds_hash_step1])

def test_ds_tags():
    import dstrk.main
    from dstrk.database import DSDatabase
    global ds_hash_step2, ds_hash_step3

    assert DSDatabase(test_db_path).get_ds_info(os.path.join(test_data_path, "step_3", "part1.txt"))['tags'][0] == 'Third Step'
    assert DSDatabase(test_db_path).get_ds_info(os.path.join(test_data_path, "step_3", "part1.txt"))['tags'][1] == 'More third step info'
    
def test_ls_tree():
    import dstrk.main
    from dstrk.database import DSDatabase
    global ds_hash_step2, ds_hash_step3

    dstrk.main.main(['--dbpath', test_db_path, 'tree', os.path.join(test_data_path, "step_3", "part1.txt") ])
