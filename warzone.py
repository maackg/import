
from datetime import datetime as dt
import xml.etree.ElementTree as XML
import json

import system

# Summary: Class object for the current state of all FW
# Mostly, it's a container for all the systems

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
        self.expires = Data['expires']
        self.systems = {}
        with open("names.json", 'r') as f :
            names = json.load(f)
        for sysdata in self.data['body'] :
            name = names[str(sysdata['solar_system_id'])]
            self.systems[name] = system.System(sysdata)

    def Save (self, folder="history/") :
        savename = folder + self.timestamp + '.json'
        with open(savename, 'w') as f :
            json.dump(self.data, f, indent='\t')

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

class WarzoneDiff :
    # aggregates two warzones, then stores in a single container
    def __init__ (self, wzNew, wzOld) :
        self.TimeOld = wzOld.timestamp
        self.TimeNew = wzNew.timestamp
        self.NextExpiry = wzNew.expires
        self.FacDeltas = {  # facID : [dplex, oplex, total]
            500001  : [0,0,0], # Caldari
            500002  : [0,0,0], # Minmatar
            500003  : [0,0,0], # Amarr
            500004  : [0,0,0]  # Gallente
        }
        self.FacSysCounts = {
            500001 : 0,
            500002 : 0,
            500003 : 0,
            500004 : 0
        }
        self.systems = wzNew.systems # reuse dictionary
        for name, sys in self.systems.items() :
            sys.old = wzOld.systems[name]
            facID = sys.ownerID
            enemyID = abs((facID%500000)-5)+500000
            sys.delta = sys.Plexes() - sys.old.Plexes()
            if facID != sys.old.ownerID :
                sys.delta = 0
            if (sys.delta > 0) : # oplexing happened; credit the enemy
                self.FacDeltas[enemyID][1] += sys.delta
                self.FacDeltas[enemyID][2] += sys.delta
            else : # either deplexing or nothing happened; credit the owner
                self.FacDeltas[facID][0] -= sys.delta
                self.FacDeltas[facID][2] -= sys.delta
            self.FacSysCounts[facID] += 1

# quick WZD generator
def GetWZD (new_ESI_data, old_ESI_data) :
    wzNew = Warzone(new_ESI_data)
    wzOld = Warzone(old_ESI_data)
    return WarzoneDiff(wzNew, wzOld)
