
from datetime import datetime as dt
import json
import os
import requests
import sys

import output
from warzone import GetWZD

_cwd = os.path.dirname(os.path.abspath(__file__))
_url = "https://esi.tech.ccp.is/latest/fw/systems"
_lastdata = "temp/old.json"
_1hrdata = "temp/1hr.json"
_oled_file = "temp/oled.txt"

esi_dt = "%a, %d %b %Y %H:%M:%S GMT"
esi_dt_noGMT = "%a, %d %b %Y %H:%M:%S"
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
        TimeNow = dt.utcnow()
        if (os.path.isfile(_lastdata)) :
            # check cached data to see if it's expired
            with open(_lastdata, 'r') as f :
                old_data = json.load(f)
                cache_expiry = dt.strptime(old_data['expires'], esi_dt)
            if (cache_expiry > TimeNow) and (not debugging):
                return
            else : # cache should've expired, let's get the new data
                new_data = GetAPI(_url)
            if (dt.strptime(new_data['expires'], esi_dt) < TimeNow) and (not debugging) :
                return # checks to make sure CCP didn't return old cache
            if (os.path.isfile(_1hrdata)) :
                with open(_1hrdata, 'r') as f :
                    hr_data = json.load(f)
            else :
                hr_data = old_data.copy()
        else : # no old data present; init with new data
            new_data = GetAPI(_url)
            old_data = new_data.copy()
            hr_data  = old_data.copy()

        WZD = GetWZD(new_data, old_data)
        WZ_Hourly = GetWZD(new_data, hr_data)

        output.FWintel(settings, WZD, WZ_Hourly)

        #if settings['_OLED'] :
        #    with open(_oled_file, 'w') as f :
        #        f.write(oled_message + new_data['expires']+'\n')

        if (not debugging) :
            with open(_lastdata, 'w') as f :
                json.dump(new_data, f, indent='\t')
            new_data.Save(_cwd + '/history/')

    except Exception as e:
        print(e)


# TODO: command-line arguments
if __name__ == "__main__" :
    debug = len(sys.argv) - 1 # lazy way of enabling debug mode
    run(debug)
