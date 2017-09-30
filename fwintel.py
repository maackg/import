
from datetime import datetime as dt
import os
import shutil
import time
import sys
import requests
import json

import eve
import output
import persist
import slack
import system
import warzone

_cwd = os.path.dirname(os.path.abspath(__file__))
_url = "https://esi.tech.ccp.is/latest/fw/systems"
_lastdata = "temp/old.json"

esi_dt = "%a, %d %b %Y %H:%M:%S GMT"

_OLED = True        # What this is for: https://i.imgur.com/QHuNzEb.png
_SLACK = False      # Slack support is now deprecated
_DISCORD = True     # Viva la Discord

_facIDs = {
        "Caldari State" : 500001,
        "Minmatar Republic" : 500002,
        "Amarr Empire" : 500003,
        "Gallente Federation" : 500004
    }
_militia = "Caldari State"

# slack definitions:
s_username = 'Fwintel 3.0'
s_channels = ["#fw-intel"]
s_icon = 'http://i.imgur.com/xYBA19C.png'

# Discord definitions:
d_Webhooks = [
    ['363554064480600066','Lm9WXmGSz36-IDiVr51uOk8i73RnBwMVjGqgsURdQbjsh2QkjSEyRRgJPfDKssaTukzJ']
    ] # https://discord.gg/AKSYRb7

def GetAPI (url) :
    try :
        headers = {
            'User-Agent': "Mozilla/5.0 (Raspberry Pi; Debian; en-us) Fwintel/3.0 (Python; Nikolai Agnon; Imperial Outlaws",
            'datasource': "tranquility"}
        rs = requests.get(url, headers=headers)
        data = {
            "body" : rs.json(),
            #"headers" : rs.headers, # not serializable
            "timestamp" : rs.headers['date'],
            "expires" : rs.headers['expires']
        }
        return data
    except Exception as e :
        print("error at GetAPI")
        print(e)

def run (force=False) :
    try :
        TimeNow = dt.utcnow()
        if (os.path.isfile("temp/old.json")) :
            with open("temp/old.json", 'r') as f :
                old_data = json.load(f)
                cache_expiry = dt.strptime(old_data['expires'], esi_dt)
            if (not force) and (cache_expiry > TimeNow) :
                return
            new_data = GetAPI(_url)
            if (dt.strptime(new_data['expires'], esi_dt) < TimeNow) and (not force) :
                return # redundant, but makes sure CCP actually did update
        else :
            new_data = GetAPI(_url)
            old_data = new_data.copy()

        wzNew = warzone.Warzone(new_data, 3)
        wzOld = warzone.Warzone(old_data, 3)

        sig = "\n*Current time is {}.*\n*Next update in ~{} minutes.*".format(
        dt.strftime(dt.utcnow(),eve.dtformat),
        (dt.strptime(new_data['expires'], esi_dt)-TimeNow).seconds//60)

        slack_message, oled_message  = output.FWintel(wzNew, wzOld, _facIDs[_militia])

        if _SLACK :
            for channel in s_channels :
                slack.PostMessage(channel, slack_message + sig, s_username, s_icon, False)
        if _OLED :
            with open('temp/oled.txt', 'w') as f :
                f.write(oled_message + new_data['expires']+'\n')
        if _DISCORD :
            for Webhook in d_Webhooks :
                rs = requests.post(
                    url="https://discordapp.com/api/webhooks/{0[0]}/{0[1]}".format(Webhook),
                    data=json.dumps({
                    "content":slack_message + sig,
                    "avatar_url": "https://i.imgur.com/zT82ioc.png",
                    "username":"T-ara"}),
                    headers={'Content-Type': 'application/json'}
                    )
                status = rs.status_code
                if status != 204 : # bad code
                    print(status)

        #shutil.copyfile(_newXML, _LastXML)         # disable for testing
        #slack.SaveHistory()
        with open(_lastdata, 'w') as f :
            json.dump(new_data, f, indent='\t')
        wzNew.Save(_cwd + '/history/')

    except Exception as e:
        print(e)


if __name__ == "__main__" :
    force = len(sys.argv) - 1
    run(force)
