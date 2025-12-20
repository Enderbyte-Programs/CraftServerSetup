import os

DIR_LIST = [os.getcwd()]

def clean_dir_list():
    global DIR_LIST
    DIR_LIST = [d for d in DIR_LIST if os.path.isdir(d)]

def pushd(directory:str):
    global DIR_LIST
    os.chdir(directory)
    DIR_LIST.insert(0,directory)
def popd():
    global DIR_LIST
    try:
        DIR_LIST.pop(0)

        os.chdir(DIR_LIST[0])
    except:
        DIR_LIST = [os.getcwd()]
        os.chdir(DIR_LIST[0])
