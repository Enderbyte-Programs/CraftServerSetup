import sys

monitorfile = sys.argv[1]
while True:
    iss = input(">")
    with open(monitorfile,"a+") as f:
        f.write(iss+"\n")