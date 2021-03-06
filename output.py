
from datetime import datetime as dt
import json
import requests
import urllib.parse

limit = 4

FacIDs = { # name -> id
    "Caldari State" : 500001,
    "Minmatar Republic" : 500002,
    "Amarr Empire" : 500003,
    "Gallente Federation" : 500004
    }
FacRev = { # our ID -> enemy ID
    500003: 500002,
    500002: 500003,
    500001: 500004,
    500004: 500001
    }
FacNames = { # shorthand names
    500001: "Caldari",
    500002: "Minmatar",
    500003: "Amarr",
    500004: "Gallente"
    }
esi_dt = "%a, %d %b %Y %H:%M:%S GMT"
esi_dt_noGMT = "%a, %d %b %Y %H:%M:%S"

oled_frame = """\
{names[0]} ({count[0]}): {p_us[0]}-{p_us[1]}
{names[1]} ({count[1]}): {p_them[0]}-{p_them[1]}
{home[name]}: {home[contest]:.3}% {home[delta]:+}
{expiry}
"""

def FWintel (settings, WZD, WZD_Hourly) :
    if settings['_DISCORD'] :
        for config in settings['Discord'] :
            #try : # lazy way of
            PostDiscord(config, WZD, WZD_Hourly)
            #except Exception as e :
            #    pass
    if settings['_OLED'] : # OLED support is being phasing out
        for config in settings['OLED'] :
            PostOLED(config, WZD, WZD_Hourly)

def GetAlerts(WZD, Militia, Watchlist) :
    _us = FacIDs[Militia]
    _them = FacRev[_us]
    alerts = {
        'main' : filter(
            lambda s: s.ownerID in [_us,_them] and (s.name not in Watchlist),
            WZD.systems.values()),
        'watchlist' : list(map(
            lambda s: WZD.systems[s],
            Watchlist
        ))
        }
    alerts['contest'] = sorted(
        alerts['main'],
        key=lambda a: a.Contest(),
        reverse=True)
    alerts['activity'] = sorted(
        alerts['contest'][limit:],
        key=lambda a: abs(a.delta),
        reverse=True)
    return alerts

def SysToText (sys) :
    return {
        True: "{o}-{n} is vulnerable! ({d:+}, {b} buffer)",
        False: "{o}-{n:15} {c:.1f}% ({d:+})"
    }[sys.Vuln()].format(
        o=sys.owner[0],
        n=sys.name,
        c=sys.Contest(),
        d=sys.delta,
        b=sys.Buffer()
    )

frame = """\
Highly contested systems *(hourly)*:```
{contest}```
High-activity systems *(hourly)*:```
{activity}```
Watchlisted systems *(hourly)*:```
{watchlist}```
Just in the past {timeSince} minutes: _(d-plexes, o-plexes, total)_
{names[0]} ({count[0]}) : {p_us[0]} / {p_us[1]} / {p_us[2]}
{names[1]} ({count[1]}): {p_them[0]} / {p_them[1]} / {p_them[2]}

*{timeNow}*
*Next update in {mins} minutes*
\~\~\~\~\~"""
def MessageFactory (config, WZD, WZD_Hourly) :
    _us = FacIDs[config['militia']]
    _them = FacRev[_us]

    # NOTE: Alerts now show hourly figures
    alerts = GetAlerts(WZD_Hourly, config['militia'], config['watchlist'])
    timeNow = dt.utcnow()
    watchlist = "Watchlisted systems *(hourly)*:```{}```"
    return frame.format(
        contest = '\n'.join(list(map(SysToText, alerts['contest'][:limit]))),
        activity = '\n'.join(list(map(SysToText, alerts['activity'][:limit]))),
        watchlist = '\n'.join(list(map(SysToText, alerts['watchlist']))),
        p_us = WZD.FacDeltas[_us],
        p_them = WZD.FacDeltas[_them],
        count = [WZD.FacSysCounts[_us], WZD.FacSysCounts[_them]],
        names = [FacNames[_us], FacNames[_them]],
        timeSince = (timeNow-dt.strptime(WZD.TimeOld, esi_dt)).seconds//60,
        timeHour = ((timeNow-dt.strptime(WZD_Hourly.TimeOld, esi_dt)).seconds//60),
        timeNow = dt.strftime(timeNow, esi_dt_noGMT),
        mins = (dt.strptime(WZD.NextExpiry, esi_dt)-timeNow).seconds//60
    )

def PostDiscord (config, WZD, WZD_Hourly) :
    message = MessageFactory(config, WZD, WZD_Hourly)
    payload = {"content":message}
    for c in ["avatar_url", "username"] :
        if c in config:
            payload[c] = config[c]

    rs = requests.post(
        url     = config['url'],
        data    = json.dumps(payload),
        headers = {'Content-Type': 'application/json'}
        )
    status = rs.status_code
    if status == 204 : # TODO
        print("discord: " + config['note'])
    else :
        print("failed to send. error code: " + status)


# Coming soon: removing this entirely
def PostOLED (config, WZD, WZD_Hourly) :
    HomeSys = config['home']
    _us = FacIDs[config['militia']]
    _them = FacRev[_us]
    HomeStats = {
        'name'      : HomeSys,
        'contest'   : WZD.systems[HomeSys].Contest(),
        'delta'     : WZD.systems[HomeSys].delta
    }
    message = oled_frame.format(
        names = [FacNames[_us], FacNames[_them]],
        count = [WZD.FacSysCounts[_us], WZD.FacSysCounts[_them]],
        p_us = WZD.FacDeltas[_us],
        p_them = WZD.FacDeltas[_them],
        home = HomeStats,
        expiry = WZD.NextExpiry
    )
    with open(config['file'], 'w') as f :
        f.write(message)
