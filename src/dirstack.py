import os

DIR_LIST = [os.getcwd()]
def pushd(directory:str):
    global DIR_LIST
    os.chdir(directory)
    DIR_LIST.insert(0,directory)
def popd():
    global DIR_LIST
    DIR_LIST.pop(0)
    os.chdir(DIR_LIST[0])