
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
_oled_file = "temp/oled.txt"

esi_dt = "%a, %d %b %Y %H:%M:%S GMT"
old_dt = "%Y-%m-%d %H:%M:%S"

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
        with open("settings.json", 'r') as f :
            settings = json.load(f)
        militia = settings["Militia"]
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

        slack_message, oled_message  = output.FWintel(wzNew, wzOld, militia, ["Pynekastoh", "Tama", "Old Man Star"])

        if settings['_SLACK'] :
            output.PostSlack(settings["Slack"], slack_message + sig)
        if settings['_DISCORD'] :
            output.PostDiscord(settings["Discord"], slack_message + sig)
        if settings['_OLED'] :
            with open(_oled_file, 'w') as f :
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
