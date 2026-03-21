"""The analytics explorer, a subset of server analytics that was taken out because the file was still too big"""

import curses
import cursesplus
import tempdir
import jsongz
import uicomponents
import analyticsstructures
import utils
import enum
import datetime

def server_analytics_explorer(stdscr,data:dict[int,analyticsstructures.ServerMinuteFrame]):
    cursesplus.displaymsg(stdscr,["Analytics Explorer","Initializing..."],False)
    #This function allows users to explore their analytics
    offset = 0
    datasize = len(data)-1
    currentzoomlevel = analyticsstructures.AnalyticsExplorerZoomLevels.MINUTE#Also passively the list chunk size
    currentdatatype = analyticsstructures.AnalyticsExplorerDataTypes.PLAYERCOUNT
    zoomlevels = {
        analyticsstructures.AnalyticsExplorerZoomLevels.MINUTE: "Minute (default)",
        analyticsstructures.AnalyticsExplorerZoomLevels.HOUR: "Hour",
        analyticsstructures.AnalyticsExplorerZoomLevels.DAY: "Day",
        analyticsstructures.AnalyticsExplorerZoomLevels.WEEK: "Week"
    }
    datatypes = {
        analyticsstructures.AnalyticsExplorerDataTypes.TOTALPLAYERMINUTES: "Player Minutes Spent",
        analyticsstructures.AnalyticsExplorerDataTypes.PLAYERCOUNT: "Online Players (default)"
    }
    ldata = list(data.values())#List representation of data to prevent performance issues?

    td = tempdir.generate_temp_dir()

    #ogdata = copy.deepcopy(data)
    #ogldata = copy.deepcopy(ldata)#For use later
    jsongz.write(td+"/data.json.gz",{k:analyticsstructures.serialize_smf(v) for k,v in list(data.items())})
    maxval = max([len(p.onlineplayers) for p in ldata])
    while True:
        my,mx = stdscr.getmaxyx()
        xspace = mx-1
        yspace = my-4#Top Bottom, and weird bug
        stdscr.erase()
        cursesplus.utils.fill_line(stdscr,0,cursesplus.set_colour(cursesplus.BLUE,cursesplus.BLUE))
        stdscr.addstr(0,0,"Analytics Explorer - Press Q to quit and H for help",cursesplus.set_colour(cursesplus.BLUE,cursesplus.WHITE))
        
        
        ti = 0
        for i in range(offset-xspace//2,offset+xspace//2):
            if i < 0 or i > datasize:
                #Write red bar
                #print("w")
                for dy in range(1,yspace+1):
                    stdscr.addstr(dy,ti,"█",cursesplus.set_colour(cursesplus.RED,cursesplus.RED))
            else:
                seldata = ldata[i]
                if currentdatatype == analyticsstructures.AnalyticsExplorerDataTypes.PLAYERCOUNT:
                    scale = int(seldata.howmanyonline()/maxval*yspace)
                else:
                    scale = int(seldata.getplayerminutes()/maxval*yspace)
                
                if i == offset:
                    for p in range(1,yspace+2):
                        stdscr.addstr(p,ti,"█",cursesplus.set_colour(cursesplus.GREEN,cursesplus.GREEN))#Central marker
                    for p in range(yspace+1,yspace+1-scale,-1):
                        stdscr.addstr(p,ti,"█",cursesplus.set_colour(cursesplus.CYAN,cursesplus.CYAN))
                else:
                    for p in range(yspace+1,yspace+1-scale,-1):
                        stdscr.addstr(p,ti,"█",cursesplus.set_colour(cursesplus.WHITE,cursesplus.WHITE))
            
            ti += 1
            
        seldata = ldata[offset]
        if currentdatatype == analyticsstructures.AnalyticsExplorerDataTypes.TOTALPLAYERMINUTES:
            stdscr.addstr(my-2,0,f"{utils.strip_datetime(analyticsstructures.get_datetime_from_minute_id(seldata.minuteid))} || {seldata.getplayerminutes()} player-minutes")
        else:
            try:
                stdscr.addstr(my-2,0,f"{utils.strip_datetime(analyticsstructures.get_datetime_from_minute_id(seldata.minuteid))} || {seldata.howmanyonline()} players online - {seldata.onlineplayers}")
            except:
                stdscr.addstr(my-2,0,f"{utils.strip_datetime(analyticsstructures.get_datetime_from_minute_id(seldata.minuteid))} || {seldata.howmanyonline()} players online")#Too long for list
        
        ch = curses.keyname(stdscr.getch()).decode()
        if ch == "q":
            break
        elif ch == "h":
            cursesplus.displaymsg(stdscr,["KEYBINDS","q - Quit","h - Help","<- -> Scroll","END - Go to end","HOME - Go to beginning","j - Jump to time","SHIFT <-- --> - Jump hour","Ctrl <-- --> - Jump day","T - Select time unit","D - Select data type"])
        elif ch == "KEY_LEFT":
            if offset > 0:
                offset -= 1
        elif ch == "KEY_RIGHT":
            offset += 1
        elif ch == "KEY_SLEFT":
            if offset > 60:
                offset -= 60
            else:
                offset = 0
        elif ch == "KEY_SRIGHT":#Jump around by an hour
            offset += 60 
        elif ch == "kRIT5":#ctrl left
            offset += 1440
        elif ch == "kLFT5":#ctrl right
            if offset > 1440:
                offset -= 1440
            else:
                offset = 0
        elif ch == "KEY_END":
            offset = datasize - 1
        elif ch == "KEY_HOME":
            offset = 0
        elif ch == "j":
            stdscr.clear()
            ndate:datetime.datetime = cursesplus.date_time_selector(stdscr,cursesplus.DateTimeSelectorTypes.DATEANDTIME,"Choose a date and time to jump to",True,False,analyticsstructures.get_datetime_from_minute_id(ldata[offset].minuteid)) # type: ignore
            if currentzoomlevel == analyticsstructures.AnalyticsExplorerZoomLevels.HOUR:
                ndate = ndate.replace(second=0,minute=0)
            if currentzoomlevel == analyticsstructures.AnalyticsExplorerZoomLevels.DAY or currentzoomlevel == analyticsstructures.AnalyticsExplorerZoomLevels.WEEK:
                ndate = ndate.replace(hour=0)
            nmid = analyticsstructures.get_minute_id_from_datetime(ndate)
            if not nmid in data:
                cursesplus.messagebox.showerror(stdscr,["Records do not exist for the selected date."])
            else:
                offset = list(data.keys()).index(nmid)
        elif ch == "t":
            currentzoomlevel = list(zoomlevels.keys())[uicomponents.menu(stdscr,list(zoomlevels.values()),"Choose a zoom level")]
            cursesplus.displaymsg(stdscr,["Generating Data"],False)
            #This will use ogdat because data may have been used for hour or day, which will screw it up
            offset = 0
            if currentzoomlevel == analyticsstructures.AnalyticsExplorerZoomLevels.MINUTE:
                data = {k:analyticsstructures.deserialize_smf(v) for k,v in list(jsongz.read(td+"/data.json.gz").items())}
                ldata = list(data.values())
            else:
                chunked_data:list[list[analyticsstructures.ServerMinuteFrame]] = list(utils.split_list_into_chunks(list({k:analyticsstructures.deserialize_smf(v) for k,v in list(jsongz.read(td+"/data.json.gz").items())}.values()),get_chunk_size_from_aezl(currentzoomlevel)))
                final_data:dict[int,analyticsstructures.ServerMinuteFrame] = {}
                for chunk in chunked_data:
                    s:analyticsstructures.ServerMinuteFrame = analyticsstructures.ServerMinuteFrame(chunk[0].minuteid)
                    #Append all unique players, and set playerminutes
                    total_playerminutes = 0
                    unique_players = []
                    for minute in chunk:
                        total_playerminutes += minute.howmanyonline()
                        for onlineplayer in minute.onlineplayers:
                            if onlineplayer not in unique_players:
                                unique_players.append(onlineplayer)
                    s.playerminutes = total_playerminutes
                    s.onlineplayers = unique_players
                    final_data[s.minuteid] = s
                data = final_data
                del chunked_data
                del final_data
                ldata = list(data.values())
            maxval = max([p.get_data(currentdatatype) for p in list(data.values())])
            #if currentdatatype == analyticsstructures.AnalyticsExplorerDataTypes.TOTALPLAYERMINUTES:
            #    maxval = maxval*get_chunk_size_from_aezl(currentzoomlevel)
            datasize = len(data)-1
                
        elif ch == "d":
            currentdatatype = list(datatypes.keys())[uicomponents.menu(stdscr,list(datatypes.values()),"Choose a data type")]
            maxval = max([p.get_data(currentdatatype) for p in ldata])
            #if currentdatatype == analyticsstructures.AnalyticsExplorerDataTypes.TOTALPLAYERMINUTES:
            #    maxval = maxval*get_chunk_size_from_aezl(currentzoomlevel)
        if offset > datasize:
            offset = datasize - 1



def get_chunk_size_from_aezl(s:analyticsstructures.AnalyticsExplorerZoomLevels):
    return {
        analyticsstructures.AnalyticsExplorerZoomLevels.MINUTE:1,
        analyticsstructures.AnalyticsExplorerZoomLevels.HOUR:60,
        analyticsstructures.AnalyticsExplorerZoomLevels.DAY:1440,
        analyticsstructures.AnalyticsExplorerZoomLevels.WEEK:1440*7
        }[s]