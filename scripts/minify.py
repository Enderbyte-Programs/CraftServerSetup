import sys
import python_minifier
infile = sys.argv[1]
outfile = sys.argv[2]
with open(infile) as f:
    data = f.read()
o = python_minifier.minify(data,rename_locals=True,rename_globals=True)
with open(outfile,"w+") as f:
    f.write(o)