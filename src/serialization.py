import bz2, pickle, os, time
from settings import group_size, serialized, temp

def serialize(data, filename):
    with bz2.open(filename, 'wb') as picklefile:
        pickle.dump(data, picklefile)

def get_content(filename):
    with bz2.open(filename, 'rb') as picklefile:
        content = pickle.load(picklefile)
    return content

def concatenate(source='reddit'):
    print('Trying to concatenate files')
    filenames = []
    # Read top level files only
    for _, _, files in os.walk(serialized):
        filenames = [filename for filename in files if filename != '.placeholder' and filename.startswith(source)]
        break

    print(filenames)
    if len(filenames) > 1:
        print('More than one file found, concatenating..')
        # Concatenate files
        content = [item for filename in filenames for item in get_content(serialized + filename)] 
        for filename in filenames:
            os.rename(serialized + filename, temp + filename)    # Temporarily move files incase something goes wrong

        # Save concatenated file
        serialize(content, serialized + source)

        # Remove temporary backups
        for _, _, files in os.walk(temp):
            filenames = [filename for filename in files if filename != '.placeholder']
            for filename in filenames:
                os.remove(temp + filename)
                break
        print('Done')
