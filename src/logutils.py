"""Older utilities and objects for dealing with logs"""
import datetime

class LogEntry:
    def __init__(self,file:str,date:datetime.date,data:str,indict=None):
        if indict is not None:
            self.data = indict["rawdata"]
            self.file = indict["fromfile"]
            self.logdate = datetime.datetime.strptime(indict["date"],"%Y-%m-%d").date()
            self.playername = indict["player"]
        else:
            self.data = data
            self.file = file
            self.logdate = date
            if is_log_line_a_chat_line(data):
                if "[Server]" in data:
                    self.playername = "[Server]"
                elif "issued server command" in data:
                    #Handle targetted chat
                    self.playername = data.split(" issued server")[0].split(" ")[-1]
                else:
                    self.playername = data.split("<")[1].split(">")[0]
            else:
                self.playername = ""
            
    def __str__(self):
        return f"{self.logdate} {self.data}"
    
    def todict(self):
        return {
            "rawdata" : self.data,
            "date" : str(self.logdate),
            "fromfile" : self.file,
            "player" : self.playername
        }
        
    @staticmethod
    def fromdict(indict:dict):
        return LogEntry(None,None,None,indict)#type: ignore
    
    def get_full_log_time(self) -> datetime.datetime:
        timestr = self.data.split("]")[0].replace("[","")
        try:
            return datetime.datetime(self.logdate.year,self.logdate.month,self.logdate.day,int(timestr.split(":")[0]),int(timestr.split(":")[1]),int(timestr.split(":")[2]))
        except:
            return datetime.datetime(self.logdate.year,self.logdate.month,self.logdate.day,0,0,0)
        
def is_log_line_a_chat_line(line:str) -> bool:
    if ((("INFO" in line and "<" in line and ">" in line) or "[Server]" in line) and "chat" in line.lower()) or "issued server command: /msg" in line or "issued server command: /w " in line or "issued server command: /tell" in line:
        return True
    else:
        return False