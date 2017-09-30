
import xml.etree.ElementTree as XML
import json

xml_facIDs = {
        "Caldari State" : 500001,
        "Minmatar Republic" : 500002,
        "Amarr Empire" : 500003,
        "Gallente Federation" : 500004,
    }

FacNames = {
    500001 : "Caldari State",
    500002 : "Minmatar Republic",
    500003 : "Amarr Empire",
    500004 : "Gallente Federation"
}

with open("names.json", 'r') as f :
    names = json.load(f)

class System :
    def __init__ (self, Data) :
        self.ID = Data['solar_system_id']
        self.name = names[str(self.ID)]
        self.ownerID = Data['owner_faction_id']
        self.owner = FacNames[self.ownerID]
        self.vpNow = Data['victory_points']
        self.vpMax = Data['victory_points_threshold']
        self.contested = Data['contested']

    def Plexes (self) :
        return (self.vpNow // 20)
    def Contest (self) :     # percent, not in VP form
        return (self.vpNow / self.vpMax)
    def Decontest (self) :     # percent, not in VP form
        return 1 - (self.vpNow / self.vpMax)
    def Buffer (self) :
        return (int((self.vpNow - self.vpMax) // 20))
    def DustMod (self) :
        return self.vpMax / 3000
