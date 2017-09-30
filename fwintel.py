
from datetime import datetime as dt
import os
import shutil
import time
import sys

import eve
import output
import persist
import slack
import system
import warzone

_cwd = os.path.dirname(os.path.abspath(__file__))
_api = "https://api.eveonline.com/map/FacWarSystems.xml.aspx"
_newXML = persist.AbsPath("xml/FacWarSystems.xml")
_LastXML = _newXML + ".old"

_facIDs = {
        "Caldari State" : 500001,
        "Minmatar Republic" : 500002,
        "Amarr Empire" : 500003,
        "Gallente Federation" : 500004,
    }
_us = 500003    # Amarr
_them = 500002     # Minmatar
#_us = 500001     # Caldari
#_them = 500004     # Gallente

# slack definitions:
username = 'Fwintel 2.3'
chans = [["#fw-intel"], ["#dirtcamp"]] # [ [all intel], [pings for officers] ]
#chans = [["@nikolai"], ["@nikolai"]]
icon_old = 'http://i.imgur.com/o1gcB6U.png'
icon_data = 'http://i.imgur.com/Snu5VA5.png'
icon_fc = 'http://i.imgur.com/hsG0mRZ.png'

icons = [     # Threat: none, some, red.  regular, bash
    [ "http://i.imgur.com/xYBA19C.png", "http://i.imgur.com/oEhXqjQ.png", "http://i.imgur.com/dMJ5kwX.png"],
    [ "http://i.imgur.com/UguaKHh.png", "http://i.imgur.com/89OC1qq.png", "http://i.imgur.com/FRsdRGI.png"]
    ]

headers = {'User-Agent': "Mozilla/5.0 (Raspberry Pi; Debian; en-us) Fwintel/2.3 (Python; Nikolai Agnon; Imperial Outlaws; Nikolai for CSM XI! FacWar | Lowsec | PVE | API)"}

def run (force=False) :
    try :
        fwOld = persist.XML_load(_LastXML)
        if (not force) and (dt.strptime(fwOld[2].text, eve.dtformat) > dt.utcnow()) : return

        #shutil.copyfile(_newXML, _LastXML)         # disable for testing
        fwNew = persist.XML_get(eve.xml['map_FacWarSystems'], _newXML, headers)
        if (len(fwNew[1][0]) < 5) :
            raise ValueError('Not long enough of an array!')

        wzNew = warzone.Warzone(fwNew, 1)
        wzOld = warzone.Warzone(fwOld, 1)

        sig = "\nCurrent eve-time is {}.\nNext update at {}.".format(dt.utcnow().strftime('%Y-%m-%d %H:%M:%S'), dt.strptime(fwNew[2].text, eve.dtformat))

        FWintelMessage, warning, bash, vuln, oled_message  = output.FWintel(wzNew, wzOld)
        for chan in chans[0] :
            slack.PostMessage(chan, FWintelMessage + sig, username, icons[bash][warning], False)
            #slack.PostMessage('@nikolai', FWintelMessage + sig, username, icons[bash][warning])
        if vuln :
            vulnMessage = "@channel \n" + '\n'.join(vuln)
            for chan in chans[1] :
                slack.PostMessage(chan, vulnMessage, username, icon_fc)

        with open('temp/oled.txt', 'w') as f :
            f.write(oled_message + fwNew[2].text)

        shutil.copyfile(_newXML, _LastXML)         # disable for testing
        slack.SaveHistory()
        wzNew.Save(_cwd + '/history/')

    except Exception as e:
        print(e)


if __name__ == "__main__" :
    force = len(sys.argv) - 1
    run(force)
