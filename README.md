# Dataset Tracker

This is a basic dataset tracker for managing large numbers of files on a local system.
You can keep track of when a file was produced, by what and what it's heirachy is as well.

## Installation

At present, you'll need to clone the repo and then edit the paths appropriately:
```
export PYTHONPATH=<git-repo-home>/python:$PYTHONPATH
export PATH=<git-repo-home>/bin:$PATH
```

## Usage

The first thing you need to do is create a repository to store the metadata about the files.
Assuming you're OK with the default of `~/.dstrk` then just do:
```
dstrk initDB
```

You can now start adding data! If you want to just play around, run the data creation script
that will just produce a load of test data and a test git repo:
```
python tests/create_test_areas.py
```

Let's start by adding some data to our first dataset. Doing the following will store the info
about the files as a dataset entry in the DB:
```
dstrk addDS ~/.dstrk-test-data/step_1/*.txt --tags "Info about step 1"
```

You can retrieve that info by just querying one of the files:

```
dstrk DSinfo ~/.dstrk-test-data/step_1/part1.txt
```

Note that this is NOT dependent on file location - if you move the files around this will still work!

But what if you wanted to record info from a git repository that was used to create the data? Easy:
```
dstrk addDS ~/.dstrk-test-data/step_1/*.txt --gitinfo ~/.dstrk-test-git
```

and you get appropriate stuff recorded in the DB:
```
dstrk DSinfo ~/.dstrk-test-data/step_1/part1.txt
```

Note that we have just added the same data to two different datasets. This could happen quite a bit if the
exact same file is created by two different versions of software. `dstrk` will always tell you what
datasets a file belongs to but will *default* to using the latest added one.

Let's say you have a chain of analysis steps - how do you preserve the hierachy? Using the `'--parentDS'`
option:
```
dstrk addDS ~/.dstrk-test-data/step_2/*.txt --tags "Info about step 2" --parentDS <hashes_of_parent_DSs>
```

The has for a DS can be found using the `dstrk DSInfo` command above. To give an idea of the hierachy, do the following:
```
dstrk tree ~/.dstrk-test-data/step_2/part1.txt
```

Finally, you can remove datasets or files from the DB using the `'delDS'` and `'delfiles'` options.
