
from datetime import datetime as dt
import json
import os
import requests
import sys

import output
from warzone import Warzone

_cwd = os.path.dirname(os.path.abspath(__file__))
_url = "https://esi.tech.ccp.is/latest/fw/systems"
_lastdata = "temp/old.json"

esi_dt = "%a, %d %b %Y %H:%M:%S GMT"
old_dt = "%Y-%m-%d %H:%M:%S"

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
s_tokens = [
	#['xoxb-slack-key-here', "#fw-intel"],
	#['xoxb-another-slack-key', "#some-channel"],
]
s_icon = 'http://i.imgur.com/xYBA19C.png'

# Discord definitions:
d_Webhooks = [
    ['363554064480600066','Lm9WXmGSz36-IDiVr51uOk8i73RnBwMVjGqgsURdQbjsh2QkjSEyRRgJPfDKssaTukzJ']
    ] # https://discord.gg/AKSYRb7

# OLED definitions:
oled_file = "temp/oled.txt"

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

def run (debugging=False) :
    try :
        TimeNow = dt.utcnow()
        if (os.path.isfile("temp/old.json")) :
            with open("temp/old.json", 'r') as f :
                old_data = json.load(f)
                cache_expiry = dt.strptime(old_data['expires'], esi_dt)
            if (cache_expiry > TimeNow) and (not debugging):
                return
            new_data = GetAPI(_url)
            if (dt.strptime(new_data['expires'], esi_dt) < TimeNow) and (not debugging) :
                return # redundant, but makes sure CCP actually did update
        else :
            new_data = GetAPI(_url)
            old_data = new_data.copy()

        wzNew = Warzone(new_data)
        wzOld = Warzone(old_data)

        sig = "\n*{}*\n*Next update in ~{} minutes*\n\~\~\~\~\~".format(
        dt.strftime(dt.utcnow(), esi_dt),
        (dt.strptime(new_data['expires'], esi_dt)-TimeNow).seconds//60)

        slack_message, oled_message  = output.FWintel(wzNew, wzOld, _facIDs[_militia], ["Pynekastoh", "Tama", "Old Man Star"])

        if _SLACK :
            output.PostSlack(s_tokens, slack_message + sig)
        if _DISCORD :
            output.PostDiscord(d_Webhooks, slack_message + sig)
        if _OLED :
            with open(oled_file, 'w') as f :
                f.write(oled_message + new_data['expires']+'\n')

        if (not debugging) :
            with open(_lastdata, 'w') as f :
                json.dump(new_data, f, indent='\t')
            wzNew.Save(_cwd + '/history/')

    except Exception as e:
        print(e)


if __name__ == "__main__" :
    debug = len(sys.argv) - 1
    run(debug)
