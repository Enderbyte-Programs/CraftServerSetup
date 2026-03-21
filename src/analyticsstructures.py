"""Structures and utility functions for analytics"""

import datetime
import logutils
import enum

def get_minute_id_from_datetime(d:datetime.datetime) -> int:
    return int(d.timestamp()/60//1)

def get_datetime_from_minute_id(t:int) -> datetime.datetime:
    return datetime.datetime.fromtimestamp(t*60)

class JLLogFrame:
    data:str
    ext:datetime.datetime
    def __init__(self,lowerdata:logutils.LogEntry):
        rtime = lowerdata.data.split(" ")[0].strip()
        rdate = lowerdata.logdate
        
        self.ext = datetime.datetime.strptime(f"{rdate.year}-{rdate.month}-{rdate.day} {rtime[1:-1]}","%Y-%m-%d %H:%M:%S")
        self.data = lowerdata.data

class ServerMinuteFrame:
    minuteid:int
    onlineplayers:list[str] = []
    playerminutes:int = None#type: ignore
    
    def __init__(self,minuteid):
        self.minuteid = minuteid
    def wasonline(self,name) -> bool:
        return name in self.onlineplayers
    def todatetime(self) -> datetime.datetime:
        return datetime.datetime.fromtimestamp(self.minuteid*60)
    def howmanyonline(self) -> int:
        return len(self.onlineplayers)
    def getplayerminutes(self) -> int:
        if self.playerminutes is None:
            return self.howmanyonline()
        else:
            return self.playerminutes
    def get_data(self,setting):
        if setting == AnalyticsExplorerDataTypes.PLAYERCOUNT:
            return self.howmanyonline()
        else:
            return self.getplayerminutes()

def serverminuteframe_uf(smf:ServerMinuteFrame):
    return f"{smf.minuteid} ({smf.todatetime()}) - {smf.onlineplayers}"

def serialize_smf(s:ServerMinuteFrame) -> dict:
    return {
        "id" : s.minuteid,
        "playerminutes" : s.playerminutes,
        "onlineplayers" : s.onlineplayers
    }

def deserialize_smf(s:dict) -> ServerMinuteFrame:
    d = ServerMinuteFrame(s["id"])
    d.onlineplayers = s["onlineplayers"]
    d.playerminutes = s["playerminutes"]
    return d

class AnalyticsExplorerZoomLevels(enum.Enum):
    MINUTE = 1
    HOUR = 60
    DAY = 1440
    WEEK = 1440*7
    
class AnalyticsExplorerDataTypes(enum.Enum):
    TOTALPLAYERMINUTES = 0
    PLAYERCOUNT = 1