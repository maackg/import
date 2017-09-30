
# These fields should probably never need to change, but can be changed for SISI etc
server = "https://api.eveonline.com"
dtformat = '%Y-%m-%d %H:%M:%S'

# v1.2.0

def u(n) :
    return (server+n+".xml.aspx")

def FormatURL (API, Dict) :
    URL = API + "?"
    for k, v in Dict.items() :
        URL += "{}={}&".format(k,v)
    return URL


# This, however, needs to get updated every so often...
xml = {
    "account_APIKeyInfo" : server + "/account/APIKeyInfo.xml.aspx",
    "account_Characters" : server + "/account/Characters.xml.aspx",

    "char_CharacterSheet" : server + "/char/CharacterSheet.xml.aspx",
    "char_Notifications" : server + "/char/Notifications.xml.aspx",
    "char_NotificationTexts" : server + "/char/NotificationTexts.xml.aspx",

    "eve_CharacterID" : server + "/eve/CharacterID.xml.aspx",
    "eve_CharacterName" : server + "/eve/CharacterName.xml.aspx",
    "eve_TypeName" : server + "/eve/TypeName.xml.aspx",

    "map_FacWarSystems" : server + "/map/FacWarSystems.xml.aspx",

    "corp_AssetList" : u("/corp/AssetList"),
    "corp_StarbaseDetail" : u("/corp/StarbaseDetail"),
    "corp_StarbaseList" : u("/corp/StarbaseList"),
    "corp_MemberTracking" : u("/corp/MemberTracking"),
    "corp_Contracts" : u("/corp/Contracts"),

}

# Classifications for wallet activities (outdated)
refIDs = {
    "Trading" : [1],
    "Markets" : [2, 42, 44, 46, 54],
    "GMs" : [3],
    "Transfers" : [10, 11, 37, 38, 76, 99],
    "Fees" : [12, 13, 51, 52, 53, 55, 90, 113, 114, 116,
             117],
    "Repairs" : [15],
    "Bounties" : [16, 17, 85, 101, 115],
    "Missions" : [18, 20, 21, 23, 24, 25, 28, 29, 30, 31,
                  32, 33, 34],
    "Shares" : [22],
    "LP Store" : [26],
    "CSPA" : [35, 36],
    "Corp Mgt." : [39, 40, 41, 45, 47, 48, 49, 50, 86, 87,
                   88, 91, 105, 122],
    "Unknown" : [0, 43, 95, 100, 104, 109, 110],
    "Industry" : [14, 56, 57, 58, 59, 60, 61, 62, 112, 118,
                 119, 120],
    "Contracts" : [63, 64, 65, 66, 67, 68, 69, 70, 71, 72,
                   73, 74, 75, 77, 78, 79, 80, 81, 82, 83,
                   84, 102],
    "Other" : [89, 124],
    "Taxes" : [92, 93, 94, 103],
    "PI" : [96, 97, 98],
    "Store" : [106, 107, 108],
}
