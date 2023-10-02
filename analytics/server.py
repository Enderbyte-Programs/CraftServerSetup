import http.server
import json
import datetime
import sys

class MyTCPHandler(http.server.BaseHTTPRequestHandler):
    """
    The request handler class for our server.

    It is instantiated once per connection to the server, and must
    override the handle() method to implement communication to the
    client.
    """

    def handle(self):
        self.data = self.request.recv(8192).strip()
        # self.request is the TCP socket connected to the client
        if not self.data == b"":
            pass
            
        else:
            print("Empty message")
            return
        # Send back a message in html
        
        try:
            vd[str(self.client_address[0])] += 1
        except:
            vd[str(self.client_address[0])] = 1
       
        with open("users.json","w+") as f:
            f.write(json.dumps(vd))
        if len(self.data) < 10000:
            with open("data.txt","a+") as g:
                g.write(str(datetime.datetime.now()).replace(" ","_") + " ")
                g.write(self.client_address[0])
                g.write(" says ")
                g.write(str(self.data))
                g.write("\n")
        else:
            print("Server recieved packet greater than 10 KB!")
        page = self.data.decode().splitlines()[0].split(" ")[1]
        #print(page)
        if page == "/":
            self.request.sendall("HTTP/1.1 200 OK\nContent-Type: text/html\n\n<html><p>You are using a browser. This is an API server. Head over to port 10223.</p></html>".encode())
        elif "/api/amcs/" in page:
            analytics = page.split("/api/amcs/")[1].split("&")
            analyticsd = {}
            for a in analytics:
                az = a.split("=")
                analyticsd[az[0]] = az[1]
                analyticsd["time"] = str(datetime.datetime.now())
                analyticsd["ip"] = self.client_address[0]
            am["requests"].append(analyticsd)
            with open("amcs.json","w+") as f:
                f.write(json.dumps(am))
            print(f"{self.client_address[0]} : CRSS")
            
            

if __name__ == "__main__":
    HOST, PORT = "localhost", 11111
    try:
        with open("users.json") as f:
            vd = json.load(f)
    except:
        vd = {}

    try:
        with open("amcs.json") as f:
            am = json.load(f)
    except:
        am = {"requests":[]}


    # Create the server, binding to localhost on port 9999
    server = http.server.ThreadingHTTPServer((HOST, PORT), MyTCPHandler)

    # Activate the server; this will keep running until you
    # interrupt the program with Ctrl-C
    def he(type,value,traceback):
        server.shutdown()
        sys.exit(1)
    sys.excepthook = he
    print("Server is online")
    server.serve_forever()