# Test all the main function
def test_main_import():
    import dstrk.main

def test_no_options():
    import dstrk.main
    dstrk.main.main([])
    
def test_init_db():
    import dstrk.main
    dstrk.main.main(['initDB'])

def test_add_dataset():
    raise Exception

def test_add_files():
    raise Exception

def test_ls_tree():
    raise Exception

def test_ls_files():
    raise Exception
