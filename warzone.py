
from datetime import datetime as dt
import xml.etree.ElementTree as XML

import persist
import system

# Summary: Class object for the current state of all FW

# Todo: Overhaul

_facIDs = {
        "Caldari State" : 500001,
        "Minmatar Republic" : 500002,
        "Amarr Empire" : 500003,
        "Gallente Federation" : 500004,
    }
_factions = [500001, 500002, 500003, 500004]

class Warzone :
    def __init__ (self, Obj, Type) :
        if Type == 1 :     # XML
            self.FromXML(Obj)
        elif Type == 2 :   # JSON
            self.FromJS(Obj)

    def FromXML (self, tree) :     # from XML tree
        self.timestamp = tree[0].text
        self.systems = {}
        for row in tree[1][0] :
            name = row.get('solarSystemName')
            self.systems[name] = system.System(row, 1)

    def FromJS (self, Dict) :     # from js file (saved as a dictionary)
        self.timestamp = Dict['timestamp']
        self.systems = {}
        for name, data in Dict['systems'].items() :
            self.systems[name] = system.System(data, 2)

    def Save (self, folder) :
        Systems = {}
        for name, sys in self.systems.items() :
            Systems[name] = sys.ToDict()
        Dict = {
            'timestamp' : self.timestamp,
            'systems' : Systems
            }
        savename = folder + self.timestamp + '.json'
        persist.JS_save(Dict, savename)


    def CountSystems (self, facs = _factions) :     # returns [{facID : num_systems}, total]
        countFacs = {}
        countAll = 0
        for ID in facs :
            countFacs[ID] = 0
        for name, sys in self.systems.items() :
            if sys.ownerID in facs :
                countFacs[sys.ownerID] += 1
                countAll += 1
        return [countFacs, countAll]

    def TotalVP (self, facs = _factions) :     # returns [{facID : vpMax}, total]
        VPfacs = {}
        VPtotal = 0
        for ID in facs :
            VPfacs[ID] = 0
        for name, sys in self.systems.items() :
            if sys.ownerID in facs :
                VPfacs[sys.ownerID] += sys.vpMax
                VPtotal += sys.vpMax
        return [VPfacs, VPtotal]

    def DefCon (self, facID) :     # returns % defensive control
        vpMax, vpNow = 0, 0
        for name, sys in self.systems.items() :
            if sys.ownerID == facID :
                vpMax += sys.vpMax
                vpNow += sys.vpNow
        return (1 - (vpNow / vpMax )) * 100

    def OffCon (self, ownerID, hostileID) :     # returns % offensive control
        vpMaxOwned, vpNowHostile = 0, 0
        for name, sys in self.systems.items() :
            if sys.ownerID == ownerID :
                vpMaxOwned += sys.vpMax
            elif sys.ownerID == hostileID :
                vpNowHostile += sys.vpNow
        vpTotal = self.TotalVP([ownerID, hostileID])[1]
        return ((vpMaxOwned + vpNowHostile) / vpTotal) * 100

    def TotCon (self, ownerID, hostileID) :     # returns % wz control
        vpDecontest = 0
        vpContest = 0
        for name, sys in self.systems.items() :
            if sys.ownerID == ownerID :
                vpDecontest += (sys.vpMax - sys.vpNow)
            elif sys.ownerID == hostileID :
                vpContest += sys.vpNow
        vpTotal = self.TotalVP([ownerID, hostileID])[1]
        return ((vpDecontest + vpContest) / vpTotal) * 100

def TotalPlexDelta (wzNew, wzOld, idFriendly, idHostile) :
    Friendly = [0, 0, 0]
    Hostile = [0, 0, 0]
    Total = [0, 0, 0]
    for name, sys in wzNew.systems.items() :
        if sys.ownerID == idFriendly :
            delta = system.PlexDelta(sys, wzOld.systems[name])
            if delta > 0 :
                Hostile[1] += delta
            else :
                Friendly[0] -= delta
        elif sys.ownerID == idHostile :
            delta = system.PlexDelta(sys, wzOld.systems[name])
            if delta > 0 :
                Friendly[1] += delta
            else :
                Hostile[0] -= delta
    Friendly[2] = Friendly[0] + Friendly[1]
    Hostile[2] = Hostile[0] + Hostile[1]
    for i in range(3) :
        Total[i] = Friendly[i] + Hostile[i]
    return [Friendly, Hostile, Total]
