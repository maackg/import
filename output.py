
import json
import requests


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

def PlexDelta (New, Old) :
    if New.ownerID == Old.ownerID :
        return (New.Plexes() - Old.Plexes())
    else : # prevents 150+ plexes being reported every time a system flips
        return 0

# TODO: redesign this method
def TotalPlexDelta (wzNew, wzOld, idFriendly, idHostile) :
    Friendly = [0, 0, 0] # schema: [oplex, dplex, sum]
    Hostile = [0, 0, 0]
    Total = [0, 0, 0]
    for name, sys in wzNew.systems.items() :
        if sys.ownerID == idFriendly :
            delta = PlexDelta(sys, wzOld.systems[name])
            if delta > 0 :
                Hostile[1] += delta
            else :
                Friendly[0] -= delta
        elif sys.ownerID == idHostile :
            delta = PlexDelta(sys, wzOld.systems[name])
            if delta > 0 :
                Friendly[1] += delta
            else :
                Hostile[0] -= delta
    Friendly[2] = Friendly[0] + Friendly[1]
    Hostile[2] = Hostile[0] + Hostile[1]
    for i in range(3) :
        Total[i] = Friendly[i] + Hostile[i]
    return [Friendly, Hostile, Total]

# TODO: redesign this entire method, including better naming
def FWintel (wzNew, wzOld, militia, wl=[], limit=4) :
    message = ""
    alerts  = []
    watchlist = {}
    _us = FacIDs[militia]
    _them   = FacRev[_us]
    m_basic = "{}-{:12} {:.1f}% ({:+})"
    m_vuln  = "{} is vulnerable! ({:+}, {} buffer)"

    for name, sys in wzNew.systems.items() :
        if (sys.ownerID not in [_us, _them]) and (name not in wl) :
            continue
        OwnerID = sys.ownerID
        Contest = sys.Contest() * 100
        Owner = FacNames[sys.ownerID]
        Delta = PlexDelta(sys, wzOld.systems[name])
        if (name in wl) :
            watchlist[name] = m_basic.format(Owner[0], name, Contest, Delta)
        else :
            if Contest >= 100 :
                alerts.append([Contest, m_vuln.format(name, Delta, sys.Buffer()), Delta])
            else :
                alerts.append([Contest, m_basic.format(Owner[0], name, Contest, Delta), Delta])

    high_contest = sorted(alerts, key=lambda a: a[0], reverse=True)
    message += ("Highly contested systems:```\n" +
                '\n'.join(list(map(lambda x:x[1], high_contest[:limit]))) +
                "```\n")
    high_delta = sorted(high_contest, key=lambda a: a[2], reverse=True)
    message += ("High-activity systems:```\n" +
                '\n'.join(list(map(lambda x:x[1], high_delta[:limit]))) +
                "```")
    #for i in high_contest[:limit] :
    #    message += i[1] + '\n'
    #high_delta = sorted(high_contest, key)
    if wl :
        message += '\nWatchlisted systems:```\n'
        for i in wl :
            message += watchlist[i] + '\n'
        message += '```'

    # TODO: replace this
    TPD = TotalPlexDelta(wzNew, wzOld, _us, _them)
    plexesUs = [TPD[0][0], TPD[0][1], TPD[0][2]]
    plexesThem = [TPD[1][0], TPD[1][1], TPD[1][2]]
    syscount = wzNew.CountSystems([_us, _them])[0]
    message += (
        "\nSince last run: _(d-plexes, o-plexes, total)_\n"
        "{3[0]} ({2[0]}) : {0[0]} / {0[1]} / {0[2]}\n"
        "{3[1]} ({2[1]}): {1[0]} / {1[1]} / {1[2]}\n"
        ).format(
            plexesUs,
            plexesThem,
            [syscount[_us], syscount[_them]],
            [FacNames[_us], FacNames[_them]])

    # Pi-OLED output message
    # TODO: design pi-oled schema
    HomeSys = "Pynekastoh"
    HomeStats = [
        HomeSys,
        wzNew.systems[HomeSys].owner[0],
        wzNew.systems[HomeSys].Contest() * 100,
        (wzNew.systems[HomeSys].vpNow - wzOld.systems[HomeSys].vpNow) // 20]
    oled_message = (
        "{3[0]} ({2[0]}): {0[0]};{0[1]}\n"
        "{3[1]} ({2[1]}): {1[0]};{1[1]}\n"
        "{4[0]}: {4[2]:.3}% {4[3]:+}\n"
        ).format(
        plexesUs,
        plexesThem,
        [syscount[_us], syscount[_them]],
        [FacNames[_us], FacNames[_them]],
        HomeStats)
    return message, oled_message


def PostSlack (Tokens, message) :
    for token in Tokens :
        s_url = "https://slack.com/api/chat.postMessage?"
        args = {
            "channel"   : token['channel'],
            "icon_url"  : token['icon'],
            "token"     : token['token'],
            "username"  : token['username'],
            "link_names": "1",
            "parse"     : "full",
            "text"      : message,
        }
        rs = requests.post(
            url=(s_url + '&'.join(map(lambda key:key+'='+args[key]), args))
        )
        status = rs.status_code

def PostDiscord (Webhooks, message) :
    for Webhook in Webhooks :
        rs = requests.post(
            url     = Webhook['url'],
            data    = json.dumps({
                    "content"   : message,
                    "avatar_url": Webhook['avatar_url'],
                    "username"  : Webhook['username']
                    }),
            headers = {'Content-Type': 'application/json'}
            )
        status = rs.status_code
        if status != 204 : # TODO
            print(status)
