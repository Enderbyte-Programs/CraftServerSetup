import os
import random
import staticflags

def generate_temp_dir() -> str:
    flx = f"{staticflags.TEMPDIR}/{hex(round(random.random()*2**64))[2:]}"
    os.mkdir(flx)
    return flx#Random int between 0 and 2^64