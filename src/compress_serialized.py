#!/usr/bin/env python3
import bz2, pickle, os, time
from settings import group_size

def get_content(filename):
    with bz2.open(filename, 'rb') as picklefile:
        content = pickle.load(picklefile)
    return content

serialized = '../serialized'
temp = '../temp/'

def concatenate():
    filenames = []
    for _, _, files in os.walk(serialized):
        filenames = [filename for filename in files if filename != '.placeholder']
        break
    if len(filenames)>1:
        # Concatenate files
        content = [item for filename in filenames for item in get_content(serialized + filename)] 
        for filename in filenames:
            os.rename(serialized + filename, temp + filename)    # Temporarily move files incase something goes wrong

        # Save concatenated file
        with bz2.open(serialized + 'concatenated', 'wb') as picklefile:
            pickle.dump(content, picklefile)

        # Remove temporary backups
        for _, _, files in os.walk(temp):
            filenames = [filename for filename in files if filename != '.placeholder']
            for filename in filenames:
                os.remove(temp + filename)
                break
    
if __name__ == '__main__':
    concatenate()
