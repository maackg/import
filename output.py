
_green = 40
_yellow = 60
_red = 80

limit = 6

def PlexDelta (New, Old) :
    if New.ownerID == Old.ownerID :
        return (New.Plexes() - Old.Plexes())
    else :
        return 0

# TODO: scrap this method
def TotalPlexDelta (wzNew, wzOld, idFriendly, idHostile) :
    Friendly = [0, 0, 0]
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
def FWintel (wzNew, wzOld, _us) :
    warning = 0
    bash = 0
    message = ""
    alerts = []
    warnings = []
    vuln = []

    # specify enemy factionID based on curent factionID
    _them = {
        500003: 500002,
        500002: 500003,
        500001: 500004,
        500004: 500001}[_us]
    FacNames = { # shorthand names
        500001: "Caldari",
        500002: "Minmatar",
        500003: "Amarr",
        500004: "Gallente"}

    m_green = "*`{}` ({}) is {:.1f}% contested. ({:+})*"
    m_yellow = "`{}` ({}) is **{:.1f}%** contested. *({:+})*"
    m_red = "**Hey!** `{}` ({}) is **{:.1f}%** contested! *({:+}; {} until vuln*)"
    m_vuln = "`{}` is vulnerable! (**{:+}**, **{}** buffer)"

    for name, sys in wzNew.systems.items() :
        OwnerID = sys.ownerID
        Contest = sys.Contest() * 100
        if (OwnerID not in [_us, _them]) or ((Contest < _green)) :
            continue
        Owner = FacNames[sys.ownerID]
        Delta = PlexDelta(sys, wzOld.systems[name])
        Buffer = sys.Buffer()
        Vuln = 0 - Buffer

        # add everything to alerts, if it's important enough to alert about
        # TODO: Fricken fix this, because it's god-awful as hell
        if Contest >= 100 :
            alerts.append([Contest, m_vuln.format(name, Delta, Buffer)])
        elif Contest >= _red :
            if (OwnerID == _us) and (warning < 2) : warning = 2
            alerts.append([Contest, m_red.format(name, Owner, Contest, Delta, Vuln)])
        elif Contest >= _yellow :
            if (OwnerID == _us) and (warning < 1) : warning = 1
            alerts.append([Contest, m_yellow.format(name, Owner, Contest, Delta)])
        elif Contest >= _green :
            alerts.append([Contest, m_green.format(name, Owner, Contest, Delta)])

    # sort by highest
    for i in reversed(list(range(len(alerts)))) :
        for j in list(range(len(alerts))) :
            if j >= i :
                break
            elif alerts[i][0] > alerts[j][0] :
                alerts[i], alerts[j] = alerts[j], alerts[i]

    for i in alerts[:limit] :
        message += i[1] + '\n'

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
