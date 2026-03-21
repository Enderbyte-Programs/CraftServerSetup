"""Json-gzip reader and writer."""

import json
import gzip

def read(path:str) -> dict:
    with open(path,'rb') as f:
        rd = f.read()
    return json.loads(gzip.decompress(rd).decode())
def write(path:str,data:dict) -> None:
    with open(path,'wb+') as f:
        f.write(gzip.compress(json.dumps(data).encode()))