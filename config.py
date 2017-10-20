import json
import sys

# Dummy script to facilitate safe editing of the settings.json
# currently, only discord additions are supported

fn = "settings.json"
args = sys.argv
if len(args) < 2 :
    exit(1)
else :
    command = args[1]

with open(fn, 'r+') as f:
    js = json.load(f)
    if (command == "add") :
        protocol    = input("Discord or Slack: ")
        new_data = {}
        for a in ["militia", "webhook", "note", "watchlist", "avatar_url", "username"] :
            b = input(a + ": ")
            if b :
                new_data[a] = b

        js[protocol].append(new_data)
    json.dump(js, f)
