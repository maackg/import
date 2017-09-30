
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

class System :
    def __init__ (self, Data, Type) :
        if Type == 1 :
            self.FromXML(Data)
        elif Type == 2 :
            self.FromDict(Data)
        elif Type == 3 :
            self.FromESI(Data)

    def FromESI (self, data) :
        with open("names.json", 'r') as f :
            names = json.load(f)
        self.ID = data['solar_system_id']
        self.name = names[str(self.ID)]
        self.ownerID = data['owner_faction_id']
        self.owner = FacNames[self.ownerID]
        self.vpNow = data['victory_points']
        self.vpMax = data['victory_points_threshold']
        self.contested = data['contested']

    def FromXML (self, row) :
        self.ID = int(row.get('solarSystemID'))
        self.name = row.get('solarSystemName')
        self.owner = row.get('occupyingFactionName') or row.get('owningFactionName')
        self.ownerID = int(xml_facIDs[self.owner])

        self.vpNow = int(row.get('victoryPoints'))
        self.vpMax = int(row.get('victoryPointThreshold'))
        self.contested = (row.get('contested') == "True")

    def FromDict (self, Dict) :
        self.ID = Dict['ID']
        self.name = Dict['name']
        self.owner = Dict['owner']
        self.ownerID = Dict['ownerID']
        self.vpNow = Dict['vpNow']
        self.vpMax = Dict['vpMax']
        self.contested = Dict['contested']

    def ToDict (self) :
        Dict = {
            'ID' : self.ID,
            'name' : self.name,
            'owner' : self.owner,
            'ownerID' : self.ownerID,
            'vpNow' : self.vpNow,
            'vpMax' : self.vpMax,
            'contested' : self.contested
            }
        return Dict

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

def PlexDelta (New, Old) :
    if New.ownerID == Old.ownerID :
        return (New.Plexes() - Old.Plexes())
    else :
        return 0
