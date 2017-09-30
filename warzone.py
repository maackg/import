
from datetime import datetime as dt
import xml.etree.ElementTree as XML
import json

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
    def __init__ (self, Data) :
        self.data = Data
        self.timestamp = Data['timestamp']
        self.systems = {}
        with open("names.json", 'r') as f :
            names = json.load(f)
        for sysdata in self.data['body'] :
            name = names[str(sysdata['solar_system_id'])]
            self.systems[name] = system.System(sysdata)

    def Save (self, folder="history/") :
        savename = folder + self.timestamp + '.json'
        with open(savename, 'w') as f :
            json.dump(self.data)

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
