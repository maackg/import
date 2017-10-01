
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
