import urllib.request
import urllib.parse
import json

import persist

_historyfile = "temp/slack_history.json"


# Towards when I retired, support for multiple slacks was hacked together
_tokens = [
	'xoxb-slack-key-here',
	'xoxb-another-slack-key',
]
_token = _tokens[0]

slack_Post = "https://slack.com/api/chat.postMessage?token={}&channel={}&text={}&username={}&icon_url={}&link_names=1&parse=full"
slack_Del = "https://slack.com/api/chat.delete?token={}&channel={}&ts={}"
slack_ChannelList = "https://slack.com/api/channels.list?token={}&exclude_archived={}"
slack_UserList = "https://slack.com/api/users.list?token={}&presence={}"

API = {
    "Post" : "https://slack.com/api/chat.postMessage?token={}&channel={}&text={}&username={}&icon_url={}&link_names=1&parse=full",
    "Del" : "https://slack.com/api/chat.delete?token={}&channel={}&ts={}",
    "ChannelList" : "https://slack.com/api/channels.list?token={}&exclude_archived={}",
    "ChannelInfo" : "https://slack.com/api/channels.info?token={}&channel={}",
    "GroupList" : "https://slack.com/api/groups.list?token={}&exclude_archived={}",
    "GroupInfo" : "https://slack.com/api/groups.info?token={}&channel={}",
    "IMList" : "https://slack.com/api/im.list?token={}",
    "UserList" : "https://slack.com/api/users.list?token={}&presence={}",
    "UserInfo" : "https://slack.com/api/users.info?token={}&user={}",
}

#last = {}
last = persist.JS_load(persist.AbsPath(_historyfile))

def GetData (url) :
    try :
        r = urllib.request.urlopen(url)
        rs = json.loads(str(r.read(), "utf-8"))
        return rs
    except :
        print("Couldn't reach the URL!")
        print(url)
        return {}

def PostMessage ( channel, text, username, iconurl, PostOnce = False) :
    try :
        channel2 = urllib.parse.quote(channel)
        text2 = urllib.parse.quote(text)
        username2 = urllib.parse.quote(username)
        iconurl2 = urllib.parse.quote(iconurl)

        if (PostOnce) and (channel in last) :
            rm = slack_Del.format(_token, last[channel][0], last[channel][1])
            rmr = urllib.request.urlopen(rm)
            #print(rmr.read())

        #s = slack_Post.format(_token, "@nikolai", text2, username2, iconurl2)
        for t in _tokens :
            s = slack_Post.format(t, channel2, text2, username2, iconurl2)
            r = urllib.request.urlopen(s)

    except Exception as e :
        print(e)

def SaveHistory () :
    try :
        with open(persist.AbsPath(_historyfile), 'w') as f :
            json.dump(last, f)
    finally :
        pass

def ErrReport (e) :
    try :
        error = "Error!\n"+e
        PostMessage("@nikolai", error, "pibot", "", False)
    finally :
        pass

class Object :
    nametypes = ["name", "user"]

    def __init__ (self, data) :
        self.ID = data['id']
        self.Data = data

    def Get (self, thing) :
        try :
            return self.Data[thing]
        except :
            print("Error: Can't get", thing)
            return ""
    def __str__ (self) :
        for i in Object.nametypes :
            if i in self.Data :
                return self.Data[i]
        return self.ID

IDtype = {
    'C' : 'channel',
    'D' : 'im',
    'G' : 'group',
    'U' : 'user',
}


def GetList (List, Key, extra=1) :
    try :
        url = API[List].format(_token, extra)
        rs = GetData(url)
        data = {}
        if (rs['ok']) :
            for d in rs[Key] :
                ID = d['id']
                data[ID] = Object(d)
        else : print("Nothing?!")
        return data
    except Exception as e :
        print("Whoops!", e)
        return {}

def GetObject (ID, apiKey, Type) :
    url = API[apiKey].format(_token, ID)
    rs = GetData(url)
    print(rs)
    return Object(rs[Type])
