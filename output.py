import persist
import system
import warzone

_us = 500003    # Amarr
_them = 500002     # Minmatar

#_us = 500001 #calmil
#_them = 500004 #galmil

# for #fw-intel
_green = 40
_yellow = 60
_red = 80

limit = 10

def TotalData(wzNew, wzOld) :

    DefCon = wzNew.DefCon(_us)
    OffCon = wzNew.OffCon(_us, _them)
    TotCon = wzNew.TotCon(_us, _them)
    Control = [DefCon, OffCon, TotCon]

    #TPD = warzone.TotalPlexDelta(wzNew, wzOld, _us, _them)

    #Dplexes = [TPD[0][0], TPD[1][0], 0]
    #Oplexes = [TPD[0][1], TPD[1][1], 0]
    #Tplexes = [TPD[0][2], TPD[1][2], 0]

    #if TPD[2][0] != 0 : Dplexes[2] = TPD[0][0] / TPD[2][0] * 100
    #if TPD[2][1] != 0 : Oplexes[2] = TPD[0][1] / TPD[2][1] * 100
    #if TPD[2][2] != 0 : Tplexes[2] = TPD[0][2] / TPD[2][2] * 100

    message = (
        #"Warzone control:\n"
        "WZ Control (d/o/t): {0[0]:.2f}%/{0[1]:.2f}%/{0[2]:.2f}%"#\n\n"

        #"Amarr / Minmatar / Ratio:\n"
        #"D-plexes: {1[0]} / {1[1]} / {1[2]:.2f}%\n"
        #"O-plexes: {2[0]} / {2[1]} / {2[2]:.2f}%\n"
        #"Total Plexes: {3[0]} / {3[1]} / {3[2]:.2f}%"
        ).format(Control)#, Dplexes, Oplexes, Tplexes)

    return message

def FWintel (wzNew, wzOld) :
    warning = 0
    bash = 0
    message = ""
    alerts = []
    warnings = []
    vuln = []
    homes = persist.TXT_dict('homes.txt')
    targets = persist.TXT_simpletable('targets.txt')

    m_home = "*Warning: {}* is *{:.1f}%* contested! _(vs {}%; *{}* plex delta)_"
    m_target = "Target system *{}* is *{:.1f}%* contested. _(*{}* plex delta)_"
    m_green = "_{} ({}) is {:.1f}% contested. ({} plex delta)_"
    m_yellow = "*{}* ({}) is *{:.1f}%* contested. _(*{}* plex delta)_"
    m_red = "*Hey! {}* ({}) is *{:.1f}%* contested! (*{}* plex delta; *{}* until vuln)"
    m_vuln = "*{}* is vulnerable! (*{}* plex delta, *{}* buffer)"

    for name, sys in wzNew.systems.items() :
        OwnerID = sys.ownerID
        Contest = sys.Contest() * 100
        if (OwnerID not in [_us, _them]) or ((Contest < _green) and (name not in homes) and (name not in targets)) :
            continue
        Owner = sys.owner
        Delta = system.PlexDelta(sys, wzOld.systems[name])
        Buffer = sys.Buffer()
        Vuln = 0 - Buffer

        # add everything to alerts, if it's important enough to alert about
        # TODO: Fricken fix this, because it's god-awful as hell
        if Contest >= 100 :
            bash = 1
            alerts.append([Contest, m_vuln.format(name, Delta, Buffer)])
        elif (name in targets) and (OwnerID != _us) :
            alerts.append([Contest, m_target.format(name, Contest, Delta)])
        elif (name in homes) and (Contest > int(homes[name][0])) :
            if (OwnerID == _us) and (warning < 1) : warning = 1
            warnings.append([Contest, m_home.format(name, Contest, homes[name][0], Delta)])
            # alerts.append([Contest, m_home.format(name, Contest, homes[name][0], Delta)])
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

    # post alerts
    for i in alerts[:limit] :
        message += i[1] + '\n'
        if i[0] > 95 :     # for terminal stuff
            vuln.append(i[1])
    #for i in targets :
    #    if (i not in wzNew.systems) : break
    #    if (i not in alerts[:limit]) :
    #        so = wzOld.systems[i]
    #        sn = wzNew.systems[i]
    #        message += m_target.format(sn.name, sn.Contest()*100, system.PlexDelta(sn, so)) + '\n'
    for i in (warnings):
        message += i[1] + '\n'

    #print("[Fwintel] {} systems alerted".format(len(alerts + warnings)))
    #if vuln :
    #    print("[Fwintel] {} systems are vulnerable".format(len(vuln)))

    TPD = warzone.TotalPlexDelta(wzNew, wzOld, _us, _them)
    plexesUs = [TPD[0][0], TPD[0][1], TPD[0][2]]
    plexesThem = [TPD[1][0], TPD[1][1], TPD[1][2]]

    syscount = wzNew.CountSystems([_us, _them])[0]

    message += (
        "\nSince last run: _(d-plexes, o-plexes, total)_\n"
        "Amarr ({2[0]}) : {0[0]} / {0[1]} / {0[2]}\n"
        "Minmatar ({2[1]}): {1[0]} / {1[1]} / {1[2]}\n"
        ).format(plexesUs, plexesThem, [syscount[_us], syscount[_them]]) 

    HuolaNow = wzNew.systems['Huola'].Contest() * 100
    HuolaDelta = (wzNew.systems['Huola'].vpNow - wzOld.systems['Huola'].vpNow) // 20 
    oled_message = (
        "Amarr ({2[0]}): {0[0]};{0[1]}\n"
        "Minmatar ({2[1]}): {1[0]};{1[1]}\n"
        "Huola: {3:.3}% ({4:+})\n"
        ).format(
        plexesUs,
        plexesThem,
        [syscount[_us], syscount[_them]],
        HuolaNow,
        HuolaDelta)
    return message, warning, bash, vuln, oled_message
