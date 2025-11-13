"""Tools for working with java .properties files"""

def load(s: str) -> dict:
    """Load raw text from a properties file and parse it into a dict"""
    dat = s.splitlines()
    dat = [d for d in dat if d.replace(" ","") != ""]
    dat = [d for d in dat if d[0] != "#"]
    final = {}
    for d in dat:
        key = d.split("=")[0]
        val = "=".join(d.split("=")[1:])
        try:
            val = float(val)# Convert to int if you can
        except:
            pass
        else:
            try:
                val = int(str(val))
            except:
                if val == int(val):
                    val = int(val)
                pass
        if val == "true" or val == "false":
            val = val == "true"# Convert to bool if you can
        final[key] = val
    return final

def dump(d: dict) -> str:
    """Dump a dictionary to a .properties string"""
    l = ""
    for f in d.items():
        lout = f[1]
        if isinstance(lout,float):
            if int(lout) == lout:
                lout = int(lout)#Prevent unnescendsary decimals
        if isinstance(lout,bool):
            if lout:
                lout = "true"
            else:
                lout = "false"
        l += f[0] + "=" + str(lout) + "\n"
    return l

def loadf(filename:str) -> dict:
    """Load a properties file"""
    with open(filename) as f:
        return load(f.read())
    
def dumpf(filename:str,data:dict) -> None:
    """Write a properties file"""
    with open(filename,"w+") as f:
        f.write(dump(data))