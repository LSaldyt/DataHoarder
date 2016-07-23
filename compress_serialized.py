import bz2, pickle, os, time
from settings import group_size

def get_content(filename):
    with bz2.open(filename, 'rb') as picklefile:
        return pickle.load(picklefile)

def concatenate(): 
    files = walk('serialized').next()[2]
    if len(files>1):
        content = [item for file in files for item in get_content(file)] 
        for filename in files:
            os.rename('serialized/' + filename, 'temp/' + filename)    # Temporarily move files incase something goes wrong
        with bz2.open('serialized/concatenated', 'wb') as picklefile:
            pickle.dump(content, picklefile)
        os.remove('temp/*')                                            # Delete them once everything is safe/done
