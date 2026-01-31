import datetime
import os
import cursesplus
import gzip
import dirstack
import re

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


def load_server_logs(stdscr,serverdir:str,dosort=True,load_no_earlier_than:datetime.datetime=None,regex_filter="") -> list[LogEntry]:#type: ignore
    cursesplus.displaymsg(stdscr,["Loading Logs, Please wait..."],False)
    logfile = serverdir + "/logs"
    if not os.path.isdir(logfile):
        cursesplus.messagebox.showerror(stdscr,["No logs could be found."])
        return []
    dirstack.pushd(logfile)
    logs:list[str] = [l for l in os.listdir(logfile) if l.endswith(".gz") or l.endswith(".log")]
    if dosort:
        logs = list(sorted(logs))#Sort the data by sorting the files
    #cursesplus.messagebox.showinfo(stdscr,[f"F {len(logs)}"])
    p = cursesplus.ProgressBar(stdscr,len(logs),cursesplus.ProgressBarTypes.SmallProgressBar,cursesplus.ProgressBarLocations.TOP,message="Loading logs")
    allentries:list[LogEntry] = []
    for lf in logs:
        log_lastwrite_dates = lf.replace("\\","/").split("/")[-1]
        if "latest" in lf:
            loglastwrite = datetime.datetime.now().date()
        else:
            loglastwrite = datetime.date(int(log_lastwrite_dates.split("-")[0]),int(log_lastwrite_dates.split("-")[1]),int(log_lastwrite_dates.split("-")[2]))
        if load_no_earlier_than is not None and load_no_earlier_than.date() > loglastwrite:
            continue
        p.step(lf)
        if lf.endswith(".gz"):
            with open(lf,'rb') as f:
                dx = load_log_entries_from_raw_data(gzip.decompress(f.read()).decode(),lf)
                if regex_filter != "":
                    dx = [d2 for d2 in dx if bool(re.search(regex_filter,d2.data))]
                allentries.extend(dx)
        else:
            with open(lf) as f:
                dx = load_log_entries_from_raw_data(f.read(),lf)
                if regex_filter != "":
                    dx = [d2 for d2 in dx if bool(re.search(regex_filter,d2.data))]
                allentries.extend(dx)
    return allentries

def load_log_entries_from_raw_data(data:str,fromfilename:str) -> list[LogEntry]:
    if "latest" in fromfilename:
        ld = datetime.datetime.now().date()
    else:
        ld = datetime.date(
            int(fromfilename.split("-")[0]),
            int(fromfilename.split("-")[1]),
            int(fromfilename.split("-")[2])
        )
    final = []
    for le in data.splitlines():
        final.append(LogEntry(fromfilename,ld,le))
    return final

