"""A second version of the algorithm to load log files. This is a replacement for much of logutils."""
import typing
import logutils
import cursesplus
import os
import dirstack
import zlib
import datetime
import logfilters
import re
import gzip

def load_logs(stdscr,serverdir:str,filter_function:typing.Callable[[logutils.LogEntry],bool] = logfilters.permit_all,min_datetime = datetime.datetime(2000,1,1,0,0,0),max_datetime = datetime.datetime(2099,12,31,23,59,59)) -> list[logutils.LogEntry]:#I will be surprised if Minecraft is still operating and this program works in 2100. I'll most likely be long dead...
    """Load the logs of the server from `serverdir`, applying the check filter function. Returned logs will be between min date and max date."""
    cursesplus.displaymsg(stdscr,["Loading Logs, Please wait...","0 processed","0 accepted","0 filtered"],False)
    min_date = min_datetime.date()
    max_date = max_datetime.date()
    logdir = serverdir + "/logs"
    if not os.path.isdir(logdir):
        cursesplus.messagebox.showerror(stdscr,["No logs could be found."])
        return []
    dirstack.pushd(logdir)
    logs:list[str] = []
    plogs:list[str] = [l for l in os.listdir(logdir) if l.endswith(".gz") or l.endswith(".log")]
    for lf in plogs:
        if "latest" in lf:
            ld = datetime.datetime.now().date()
        else:
            ld = datetime.date(
                int(lf.split("-")[0]),
                int(lf.split("-")[1]),
                int(lf.split("-")[2])
            )
        if ld >= min_date and ld <= max_date:
            logs.append(lf)#Accept
        
    logs = list(sorted(logs))#Sort the data by sorting the files
    #cursesplus.messagebox.showinfo(stdscr,[f"F {len(logs)}"])
    p = cursesplus.ProgressBar(stdscr,len(logs),cursesplus.ProgressBarTypes.SmallProgressBar,cursesplus.ProgressBarLocations.TOP,message="Loading logs")
    allentries:list[logutils.LogEntry] = []
    
    total_entries_processed = 0
    total_entries_accepted = 0
    total_entries_rejected = 0
    for logfile in logs:
        if logfile.endswith("log"):
            with open(logfile) as f:
                for line in f:

                    #While we are not at EOF
                    line = line.replace("\n","").replace("\r","")

                    le = create_log_entry(line,logfile)

                    total_entries_processed += 1
                    if not filter_function(le):
                        total_entries_rejected += 1
                        continue

                    total_entries_accepted += 1
                    allentries.append(le)

        else:
            #Gzip will be a bit more complex because it is a compressed file
            with open(logfile,'rb') as f:
                buffer:bytes = b""
                compressionobj = zlib.decompressobj(16+zlib.MAX_WBITS)
                keepreading = True
                while keepreading:

                    nextbytes = f.read(100)#Load 100 compressed bytes at a time.
                    if len(nextbytes) < 100:
                        keepreading = False#End of file
                    buffer += compressionobj.decompress(nextbytes).replace(b"\r",b"")#No damn windows newlines
                    while b"\n" in buffer:
                        splb = buffer.split(b"\n",1)
                        line = splb[0].decode()
                        buffer = splb[1]
                        le = create_log_entry(line,logfile)

                        letime = le.get_full_log_time()
                        if letime < min_datetime or letime > max_datetime:
                            continue#Reject for being out of range. Like the date this does not contribute to the reject count

                        total_entries_processed += 1
                        if not filter_function(le):
                            total_entries_rejected += 1
                            continue

                        total_entries_accepted += 1
                        allentries.append(le)

        cursesplus.displaymsg(stdscr,["Loading Logs, Please wait...",f"{total_entries_processed} processed",f"{total_entries_accepted} accepted",f"{total_entries_rejected} filtered"],False)
        p.step(logfile)

    return allentries

def create_log_entry(data:str,fromfilename:str) -> logutils.LogEntry:
    if "latest" in fromfilename:
        ld = datetime.datetime.now().date()
    else:
        ld = datetime.date(
            int(fromfilename.split("-")[0]),
            int(fromfilename.split("-")[1]),
            int(fromfilename.split("-")[2])
        )
    return logutils.LogEntry(fromfilename,ld,data)

def load_server_logs_and_find(stdscr,serverdir:str,tofind:str) -> list[str]:
    """Find specific matches of regex, removing the rest of the log entry"""
    cursesplus.displaymsg(stdscr,["Loading Logs, Please wait..."],False)
    logfile = serverdir + "/logs"
    if not os.path.isdir(logfile):
        return []
    dirstack.pushd(logfile)
    logs:list[str] = [l for l in os.listdir(logfile) if l.endswith(".gz") or l.endswith(".log")]
    p = cursesplus.ProgressBar(stdscr,len(logs),cursesplus.ProgressBarTypes.SmallProgressBar,cursesplus.ProgressBarLocations.TOP,message="Loading logs")
    final:list[str] = []
    for lf in logs:
        p.step(lf)
        if lf.endswith(".gz"):
            with open(lf,'rb') as f:
                final.extend(re.findall(tofind,gzip.decompress(f.read()).decode()))
        else:
            with open(lf) as f:
                final.extend(re.findall(tofind,f.read()))
    return final
