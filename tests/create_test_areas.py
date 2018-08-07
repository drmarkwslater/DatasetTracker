import pytest
import os
import shutil
import sys

test_db_path = os.path.expanduser("~/.dstrk-test")
test_data_path = os.path.expanduser("~/.dstrk-test-data")
test_git_path = os.path.expanduser("~/.dstrk-test-git")
 
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

# create a test repo
if os.path.exists(test_git_path):
    shutil.rmtree(test_git_path)
os.mkdir(test_git_path)
os.system("cd {0} && git init && echo 'HELLO' > test.txt && git add test.txt && git commit -m 'basic commit'".format(test_git_path))
