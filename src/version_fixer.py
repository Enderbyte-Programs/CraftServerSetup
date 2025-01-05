#This program takes a "x.y[.z]" and converts it into a PYI safe version (like 1,45,1,0)
import sys

d = sys.argv[1].split(".")
rps = sys.argv[1].replace(".",",")
vsets = len(d)

if vsets == 1:
    print(rps+",0,0,0")
elif vsets == 2:
    print(rps+",0,0")
elif vsets == 3:
    print(rps+",0")
else:
    print(rps)