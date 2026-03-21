"""Server Analytics and related functions"""

import telemetry
import uicomponents
import cursesplus
import renaminghandler
import os
import datetime
import logloader
import re
import copy
import jsongz
import utils
import logfilters
import analyticsstructures
import analyticsexplorer

#TODO - split this file into analyticsexplorer.py and analyticsstructures.py

def analytics_loader(stdscr,serverdir):
    telemetry.telemetric_action("analytics")
    if uicomponents.resource_warning(stdscr):
        return
    renaminghandler.autoupdate_cache(stdscr,serverdir)
    analytics_file_path = serverdir + os.sep + "anacache.json.gz"
    cursesplus.displaymsg(stdscr,["Loading from cache..."],False)
    readfrom = datetime.datetime(2000,1,1,0,0,0)
    cachefile = {"end":None,"minutes":{}}
    if os.path.isfile(analytics_file_path):
        cachefile = jsongz.read(analytics_file_path)
        if cachefile["end"] is not None:
            readfrom = analyticsstructures.get_datetime_from_minute_id(cachefile["end"])#Stores the last minuteid that it successfully processed.
    
    #allentries:list[logutils.LogEntry] = logutils.load_server_logs(stdscr,serverdir,False,readfrom)
    allentries = logloader.load_logs(stdscr,serverdir,logfilters.has_joinorleave,readfrom)
    cursesplus.displaymsg(stdscr,["Parsing Data","Please Wait"],wait_for_keypress=False)
    eventslist:list[analyticsstructures.JLLogFrame] = []
    joins:dict[int,list[str]] = {}
    leavs:dict[int,list[str]] = {}
    #Both of these lists will be [minuteid] -> [list of players].
    
    earliestentrydt:datetime.date = readfrom.date()
    if len(allentries) > 0:
        earliestentrydt = allentries[0].logdate
    
    for entry in allentries:
        
        lz = re.findall(r' \S* joined the game| \S* left the game',entry.data)
        
        #print(entry.data)
        if len(lz) > 0:
            if entry.logdate < earliestentrydt:
                earliestentrydt = entry.logdate
            #print(lz)
            eventslist.append(analyticsstructures.JLLogFrame(entry))
            rs:str = lz[0].strip()
            plname = rs.split(" ")[0].lower()
            action = rs.split(" ")[1]
            #Remove special characters from plname
            plname = plname.replace("(","").replace(")","")
            plname = renaminghandler.get_current_name_of(plname)
            mid = analyticsstructures.get_minute_id_from_datetime(eventslist[-1].ext)
            if "joined" in action:
                if not mid in joins:
                    joins[mid] = [plname]
                else:
                    joins[mid].append(plname)
            if "left" in action:
                if not mid in leavs:
                    leavs[mid] = [plname]
                else:
                    leavs[mid].append(plname)
    cursesplus.displaymsg(stdscr,["Sorting Data","Please Wait"],wait_for_keypress=False)
    joins = utils.sort_dict_by_key(joins)
    leavs = utils.sort_dict_by_key(leavs)
    firstentrymid = analyticsstructures.get_minute_id_from_datetime(datetime.datetime.combine(earliestentrydt,datetime.time(0,0,0)))
    if len(cachefile["minutes"]) > 0:
        firstentrymid = int(list(cachefile["minutes"].keys())[0])+1
    cursesplus.displaymsg(stdscr,["Analyzing Data","Please Wait"],wait_for_keypress=False)
    currentmid = analyticsstructures.get_minute_id_from_datetime(datetime.datetime.now())
    #Take leavs and joins and assemble minuteframe
    final:dict[int,analyticsstructures.ServerMinuteFrame] = {
        firstentrymid-1:analyticsstructures.ServerMinuteFrame(firstentrymid-1)#Keep template incase no action in first minute
    }
    
    lastrealjoin:dict[str,int] = {}#keep track of the last registered join of a player. If they stay on for longer than 6 hours without a real join, they get removed.
    for m in range(firstentrymid,currentmid+1):
        #M is minute id
        if m not in joins and not m in leavs:
            prev = copy.deepcopy(final[m-1])
            prev.minuteid = m
            final[m] = prev
        else:
            phj = []
            phl = []
            if m in joins:
                phj = joins[m]
            if m in leavs:
                phl = leavs[m]
            
            frame = copy.deepcopy(final[m-1])#Deep copy!?!?!? THEN WHY WERENT YOU COPYING !?!??!
            #frame = ServerMinuteFrame(0)
            frame.minuteid = m 
            frame.onlineplayers = frame.onlineplayers.copy()
            for player in phj:
                lastrealjoin[player] = m
                if player in phl:
                    phl.remove(player)
                    continue#This should solve the quick joinleave problem
                frame.onlineplayers.append(player)
            for player in phl:
                try:
                    frame.onlineplayers = utils.remove_values_from_list(frame.onlineplayers,player)
                except:
                    pass
            for op in frame.onlineplayers:
                try:
                    if (m - lastrealjoin[op]) > 360:
                        #print("REM")
                        frame.onlineplayers = utils.remove_values_from_list(frame.onlineplayers,op)
                except:
                    pass#If player inspects analytics starting from when players were online, this could crash
            final[m] = frame
    for cachedentry in list(cachefile["minutes"].items()):
        final[int(cachedentry[0])] = analyticsstructures.ServerMinuteFrame(int(cachedentry[0]))
        final[int(cachedentry[0])].onlineplayers = cachedentry[1]
        #This should overwrite any nasty data.
    cursesplus.displaymsg(stdscr,["Cleaning Data","Please Wait"],wait_for_keypress=False)
    
    for k in final:
        final[k].onlineplayers = utils.remove_duplicates_from_list(final[k].onlineplayers)
        
    #Find last zeroed time to store in cache
    storeto = analyticsstructures.get_minute_id_from_datetime(readfrom)#By default, store none. Then, try to find the last zero point
    for mre in list(final.values()).__reversed__():
        if mre.howmanyonline() == 0:
            storeto = mre.minuteid
            break
    cursesplus.displaymsg(stdscr,["Saving Data","Please Wait"],False)
    newcache = {"end":int(storeto),"minutes":{}}
    for line in list(final.items()):
        if int(line[0]) <= int(storeto):
            newcache["minutes"][int(line[0])] = line[1].onlineplayers
    jsongz.write(analytics_file_path,newcache)
    #with open("/tmp/cwf.txt","w+") as f:
    #    f.write("\n".join([serverminuteframe_uf(x) for x in list(final.values())]))
    cursesplus.displaymsg(stdscr,["Done"],False)
    
    minminid = firstentrymid      
    maxminid = analyticsstructures.get_minute_id_from_datetime(datetime.datetime.now())
    while True:
        cursesplus.displaymsg(stdscr,["Applying filters..."],False)
        workingdata:dict[int,analyticsstructures.ServerMinuteFrame] = {}
        for k in list(final.keys()):
            if k >= minminid and k <= maxminid:
                workingdata[k] = final[k]
        wtd = uicomponents.menu(stdscr,["Back","Analytics Explorer","Playtime","Total Player Count","Time of Day",f"FILTER MIN: {utils.strip_datetime(analyticsstructures.get_datetime_from_minute_id(minminid))}",f"FILTER MAX: {utils.strip_datetime(analyticsstructures.get_datetime_from_minute_id(maxminid))}","RESET FILTERS","Export to CSV","Server Popularity Over Time","Last Seen","First Join","Reset Cache"],"Server Analytics Manager")
        if wtd == 0:
            return
        elif  wtd == 1:
            analyticsexplorer.server_analytics_explorer(stdscr,workingdata)
        elif wtd == 2:
            cursesplus.displaymsg(stdscr,["Analyzing Data","Please Wait"],False)
            playminutes:dict[str,int] = {}
            for entry in list(workingdata.values()):
                for p in entry.onlineplayers:
                    if not p in playminutes:
                        playminutes[p] = 0
                    playminutes[p] += 1
            while True:
                #swtd = uicomponents.menu(stdscr,["Back","VIEW GRAPH"]+list(playminutes.keys()),"Choose a player to view their playtime information")
                swtd = cursesplus.searchable_option_menu(stdscr,list(playminutes.keys()),"Choose a player to view their playtime information",["Back","View Total Graph"])
                if swtd == 0:
                    break
                elif swtd == 1:
                    
                    cursesplus.bargraph(stdscr,playminutes,"Player Minute Information","minutes")
                else:
                    plstudy = list(playminutes.keys())[swtd-2]
                    zwtd = uicomponents.menu(stdscr,["Total Playtime Minutes","Playtime History","Time of Day analyzers"])
                    match zwtd:
                        case 0:
                            cursesplus.messagebox.showinfo(stdscr,["Playtime Minutes: "+str(playminutes[list(playminutes.keys())[swtd-2]])])
                        case 1:
                            cursesplus.displaymsg(stdscr,["Analyzing Data","Please wait"],False)
                            dzl = {}#yearmonth:data
                            for entry in list(workingdata.values()):
                                if plstudy in entry.onlineplayers:
                                    nd = analyticsstructures.get_datetime_from_minute_id(entry.minuteid)
                                    nk = f"{nd.year}-{str(nd.month).zfill(2)}"
                                    if not nk in dzl:
                                        dzl[nk] = 1
                                    else:
                                        dzl[nk] += 1
                                        
                            cursesplus.bargraph(stdscr,dzl,f"How has {plstudy} played over the months?","minutes spend",False,True)
                        case 2:
                            cursesplus.displaymsg(stdscr,["Analyzing Data","Please Wait"],False)
                            dataset:list[int] = [0 for _ in range(24)]#0:00 to 23:00

                            for entry in list(workingdata.values()):
                                hr = analyticsstructures.get_datetime_from_minute_id(entry.minuteid).hour
                                if plstudy in entry.onlineplayers:
                                    dataset[hr] += 1
                                
                            dataset_ps = {}
                            i = 0
                            for ex in dataset:
                                dataset_ps[f"{i}:00 - {i}:59"] = ex
                                i += 1
                                
                            cursesplus.bargraph(stdscr,dataset_ps,"Player minutes spent per hour of day","player-minutes",False,True)
                            
        elif wtd == 3:
            cursesplus.displaymsg(stdscr,["Analyzing Data","Please Wait"],False)
            allplayers = []
            for entry in list(workingdata.values()):
                allplayers += entry.onlineplayers
            cursesplus.messagebox.showinfo(stdscr,["During the time selected,",str(utils.count_unique_values(allplayers)),"unique players have joined this server"])
            cursesplus.messagebox.showinfo(stdscr,["The maximum number of players at once was ",str(max([s.howmanyonline() for s in list(workingdata.values())]))])
        elif wtd == 4:
            cursesplus.messagebox.showinfo(stdscr,["This graph is shown in player-minutes","It is one for each minute a player spends"])
            cursesplus.displaymsg(stdscr,["Analyzing Data","Please Wait"],False)
            dataset:list[int] = [0 for _ in range(24)]#0:00 to 23:00

            for entry in list(workingdata.values()):
                hr = analyticsstructures.get_datetime_from_minute_id(entry.minuteid).hour
                dataset[hr] += entry.howmanyonline()
                
            dataset_ps = {}
            i = 0
            for ex in dataset:
                dataset_ps[f"{i}:00 - {i}:59"] = ex
                i += 1
                
            cursesplus.bargraph(stdscr,dataset_ps,"Player minutes spent per hour of day","player-minutes",False,True)
            
        elif wtd == 5:
            stdscr.clear()
            minminid = analyticsstructures.get_minute_id_from_datetime(cursesplus.date_time_selector(stdscr,cursesplus.DateTimeSelectorTypes.DATEANDTIME,"Choose a new minimum filter time",True,False,analyticsstructures.get_datetime_from_minute_id(minminid)))#type: ignore
        elif wtd == 6:
            stdscr.clear()
            maxminid = analyticsstructures.get_minute_id_from_datetime(cursesplus.date_time_selector(stdscr,cursesplus.DateTimeSelectorTypes.DATEANDTIME,"Choose a new minimum filter time",True,False,analyticsstructures.get_datetime_from_minute_id(maxminid)))#type: ignore
        elif wtd == 7:
            minminid = firstentrymid      
            maxminid = analyticsstructures.get_minute_id_from_datetime(datetime.datetime.now())
        elif wtd == 8:
            od = cursesplus.filedialog.openfolderdialog(stdscr,"Select output folder")
            if od is not None:
                cursesplus.displaymsg(stdscr,["Please wait..."],False)
                finalstr = "Minute ID,Local Time,Player Count,Online Players\n"
                for entry in list(workingdata.values()):
                    finalstr += f"{entry.minuteid},{analyticsstructures.get_datetime_from_minute_id(entry.minuteid)},{entry.howmanyonline()},{', '.join(entry.onlineplayers)}\n"
                with open(od+"/serverplayers.csv","w+") as f:
                    f.write(finalstr)
                cursesplus.messagebox.showinfo(stdscr,["Exported successfully"])
        elif wtd == 9:
            tan = uicomponents.menu(stdscr,["Total Player-minutes","Unique Players","Average Online Players","Average Online Players (active time)"],"Select Data to examine",footer="(active time) shows only data that is not zero")
            gd:dict[str,list] = {}
            out_graph_data:dict[str,int] = {}
            unit = "player-minutes"
            cursesplus.displaymsg(stdscr,["Analyzing Data","Please Wait"],False)
            match tan:
                case 0:
                    for entry in list(workingdata.values()):
                        gkey = f"{analyticsstructures.get_datetime_from_minute_id(entry.minuteid).year}-{analyticsstructures.get_datetime_from_minute_id(entry.minuteid).month.__str__().zfill(2)}"
                        if gkey in out_graph_data:
                            out_graph_data[gkey] += entry.howmanyonline()
                        else:
                            out_graph_data[gkey] = entry.howmanyonline()
                case 1:
                    for entry in list(workingdata.values()):
                        gkey = f"{analyticsstructures.get_datetime_from_minute_id(entry.minuteid).year}-{analyticsstructures.get_datetime_from_minute_id(entry.minuteid).month.__str__().zfill(2)}"
                        if gkey in gd:
                            for pl in entry.onlineplayers:
                                if pl not in gd[gkey]:
                                    gd[gkey].append(pl)
                        else:
                            gd[gkey] = entry.onlineplayers
                    for dkey in gd:
                        out_graph_data[dkey] = len(gd[dkey])#Convert lists of players into lens
                    unit = "unique players"
                case 2 | 3:
                    for entry in list(workingdata.values()):
                        gkey = f"{analyticsstructures.get_datetime_from_minute_id(entry.minuteid).year}-{analyticsstructures.get_datetime_from_minute_id(entry.minuteid).month.__str__().zfill(2)}"
                        if gkey in gd:
                            if entry.howmanyonline() > 0 or tan == 2:
                                gd[gkey].append(entry.howmanyonline())
                            
                        else:
                            gd[gkey] = [entry.howmanyonline()]
                    for dkey in gd:
                        out_graph_data[dkey] = round(utils.average_list(gd[dkey]))
                    unit = "online players"
                
            cursesplus.bargraph(stdscr,out_graph_data,"Popularity Results",unit,False,False)
        elif wtd == 10:
            plf = 0
            cursesplus.displaymsg(stdscr,["Analyzing data",f"{plf} players found"],False)
            sortop = uicomponents.menu(stdscr,["Alphabetically","Recent -> Old"],"Choose search option")
            fjblock:dict[str,datetime.datetime] = {}
            for line in reversed(list(workingdata.values())):
                for pl in line.onlineplayers:
                    if not pl in fjblock.keys():
                        fjblock[pl] = analyticsstructures.get_datetime_from_minute_id(line.minuteid)
                        plf += 1
                        cursesplus.displaymsg(stdscr,["Analyzing data",f"{plf} players found"],False)

            if sortop == 0:
                fjblock = dict(sorted(fjblock.items()))#Sort A-Z

            #Assemble text
            finals = "PLAYER NAME".ljust(16)+" "+"LAST SEEN"+"\n"
            for blk in fjblock.items():
                finals += blk[0].ljust(16) + " " + utils.strip_datetime(blk[1]) + "\n"

            cursesplus.textview(stdscr,text=finals,message="Results")
        elif wtd == 11:
            plf = 0
            cursesplus.displaymsg(stdscr,["Analyzing data",f"{plf} players found"],False)
            sortop = uicomponents.menu(stdscr,["Alphabetically","Oldest to newest"],"Choose search option")
            fjblock:dict[str,datetime.datetime] = {}
            for line in list(workingdata.values()):
                for pl in line.onlineplayers:
                    if not pl in fjblock.keys():
                        fjblock[pl] = analyticsstructures.get_datetime_from_minute_id(line.minuteid)
                        plf += 1
                        cursesplus.displaymsg(stdscr,["Analyzing data",f"{plf} players found"],False)

            if sortop == 0:
                fjblock = dict(sorted(fjblock.items()))#Sort A-Z

            #Assemble text
            finals = "PLAYER NAME".ljust(16)+" "+"JOIN DATE"+"\n"
            for blk in fjblock.items():
                finals += blk[0].ljust(16) + " " + utils.strip_datetime(blk[1]) + "\n"

            cursesplus.textview(stdscr,text=finals,message="Results")
            
        elif wtd == 12:
            os.remove(analytics_file_path)
            cursesplus.messagebox.showinfo(stdscr,["The analytics cache has been reset."])
            return
        

