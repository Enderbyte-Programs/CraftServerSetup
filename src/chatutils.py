"""Who said what? and other chat utilities"""

import renaminghandler
import logloader
import uicomponents
import cursesplus
import itertools
import logfilters
import datetime
import logutils
import dirstack
import utils

def who_said_what(stdscr,serverdir):
    if uicomponents.resource_warning(stdscr):
        return
    renaminghandler.autoupdate_cache(stdscr,serverdir)
    #allentries = logutils.load_server_logs(stdscr,serverdir)
    allentriesr = logloader.load_logs(stdscr,serverdir,logfilters.is_log_entry_a_chat_line)#chat only
    allentries:list[ChatEntry] = [ChatEntry.from_logentry(a) for a in allentriesr]
    #allentries:list[ChatEntry] = [ChatEntry.from_logentry(a) for a in allentries if logutils.is_log_line_a_chat_line(a.data)]
    #allentries.sort(key=lambda x: x.logdate,reverse=False)
    #Not needed after LSL does sorting
    #allentries.reverse()
    while True:
        wtd = uicomponents.menu(stdscr,["Back","Find by what was said","Find by player","View chat history of server","View Chat Bar Graph"])
        if wtd == 0:
            break
        elif wtd == 1:
            wws = uicomponents.crssinput(stdscr,"What message would you like to search for?")
            strict = cursesplus.messagebox.askyesno(stdscr,["Do you want to search strictly?","(Full words only)"])
            cassen = cursesplus.messagebox.askyesno(stdscr,["Do you want to be case sensitive?"])
            ft = ""
            if not strict and cassen:
                ft = "\n".join([f"{a.get_parsed_date()} {a.playername}: {a.message}" for a in allentries if wws in a.message])
            elif not strict and not cassen:
                ft = "\n".join([f"{a.get_parsed_date()} {a.playername}: {a.message}" for a in allentries if wws.lower() in a.message.lower()])
            elif strict and cassen:
                ft = "\n".join([f"{a.get_parsed_date()} {a.playername}: {a.message}" for a in allentries if utils.strict_word_search(a.message,wws)])
            elif strict and not cassen:
                ft = "\n".join([f"{a.get_parsed_date()} {a.playername}: {a.message}" for a in allentries if utils.strict_word_search(a.message.lower(),wws.lower())])
            cursesplus.textview(stdscr,text=ft,message="Search Results")
        elif wtd == 2:
            wws = uicomponents.crssinput(stdscr,"What player would you like to search for?").lower()
            cursesplus.textview(stdscr,text=
                                "\n".join(
                                list(
                                    itertools.chain.from_iterable([
                                            [
                                            f"{a.get_parsed_date()} {a.playername}: {a.message}" for a in allentries if wws_indiv in a.playername
                                            ] for wws_indiv in renaminghandler.get_aliases_of(wws)
                                        ]
                                            
                                        )
                                    )
                                ),message="Search Results")
        elif wtd == 3:
            cursesplus.textview(stdscr,text=
                                "\n".join(
                                [
                                    f"{a.get_parsed_date()} {a.playername}: {a.message}" for a in allentries
                                ]),message="Search Results")
        elif wtd == 4:
            sdata = {}
            for entry in allentries:
                if entry.playername in sdata:
                    sdata[entry.playername] += 1
                else:
                    sdata[entry.playername] = 1
            cursesplus.bargraph(stdscr,sdata,"Most Talkative Players","Messages")
    dirstack.popd()


class ChatEntry:
    logtime:datetime.datetime
    playername:str
    destination:str|None = None#Only used if targetted message
    message:str

    def __init__(self):
        pass

    @staticmethod
    def from_logentry(l:logutils.LogEntry):
        r = ChatEntry()
        r.logtime = l.get_full_log_time()
        r.playername = l.playername.lower()
        rawmessage:str = l.data

        is_targetted = "issued server command" in rawmessage.lower()#Spigot/paper servers only
        if not is_targetted:
            r.message = rawmessage.split(l.playername)[1][1:]
        else:
            try:
                cmdsection = rawmessage.split("issued server command: ")[1]
                target = cmdsection.split(" ")[1]
                r.destination = target
                r.message = f"--> {r.destination}  "+" ".join(cmdsection.split(" ")[2:])
                pass
            except:
                r.message = rawmessage#If it fails, use the raw data
                
        return r
    
    def get_parsed_date(self) -> str:
        #Return a friendly date
        return self.logtime.strftime("%Y-%m-%d %H:%M:%S")