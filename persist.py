import os
import xml.etree.ElementTree as XML
import urllib.request
import urllib.parse
import shutil
import json

# version 1.2.b

# Explanation: lazy-ish way of saving/loading files
#
# Yes, I know, this entire library is bad form, and should be thrown in a fire.
# https://xkcd.com/1513/

#
#     General commands:
#

cwd = os.path.dirname(os.path.abspath(__file__)) + '/'

def AbsPath (fname) : # fname = "keys.txt", "xml/data.xml" etc
    return cwd + fname;

#
#     XML files:
#         XML_get(URL, savename) returns an XML tree root object, gotten from the internet
#         XML_load(fname) reads a file and returns the XML tree root object
#     Todo:
#         XML_save(XMLtree, fname)
#

def XML_get (URL, savename, headers={}) :
    root = XML.TreeBuilder().start('root',{})
    try :
        #URL_parsed = urllib.parse.quote(URL)
        urllib.request.urlretrieve(URL, savename)
        tree = XML.parse(savename)
        root = tree.getroot()
        if (len(root)>1) and (root[1].tag == 'error') :
            print(root[1].text)
    except :
        print("Error loading API!")
        print("URL:",URL)
        print("Savename:",savename)
    finally :
        return root

def XML_load (fname) :
    try :
        tree = XML.parse(fname).getroot()
    except :
        print('File not found!')
        tree = XML.TreeBuilder().start('root',{})
    return tree

def XML_save (XMLtree, fname) :
    pass

#
#     TXT files:
#         txt_load(fname, [splitlines]) returns [] of lines
#         txt_table(fname, [parser], [splitlines]) returns [] of lines split by parser
#         txt_simpletable(fname) returns a [] of split lines
#         txt_dict(fname, [parser], [splitlines]) returns {} of splitted lines
#     Todo:
#         txt_save(text, fname)
#

def TXT_load (fname, splitlines = True) :
    lines = []
    try :
        with open(fname) as file:
            f = file.readlines()
            for l in f :
                if (len(l) > 1) and (l[0] != '#') :
                    if splitlines :
                        lines.append(l.splitlines()[0])
                    else :
                        lines.append(l)
    finally :
        return lines

def TXT_table (fname, parser = ':', splitlines = True) :
    lines = TXT_load(fname, splitlines)
    parsed = []
    for l in lines :
        parsed.append(l.split(parser))
    return parsed

def TXT_simpletable (fname) :
    lines = TXT_load(fname, True)
    parsed = []
    for l in lines:
        parsed.append(l.splitlines()[0])
    return parsed

def TXT_dict (fname, parser = ':', splitlines = True) :
    lines = TXT_load(fname, splitlines)
    parsed = {}
    for l in lines :
        p = l.split(parser)
        parsed[p[0]] = p[1:]
    return parsed

def TXT_save (text, fname) :
    pass

#
#     JSON files:
#         None finished yet
#     Todo:
#         js_load(fname) returns a JS dictionary
#         js_save(obj, fname)
#

def JS_load (fname) :
    JS = {}
    try :
        with open(fname) as f :
            JS = json.load(f)
    finally :
        return JS

def JS_save (obj, fname) :
    with open(fname, 'w') as f :
        json.dump(obj, f)

#
#     Eve ID-Name Conversion Tools
#
#
#
#

# Asks CCP what a TypeID is
def Convert_IDs (IDs, url, savename, key, value, headers={}) :
    root = XML_get(url, savename, headers)
    names = {}
    try :
        if len(root) > 2 and root[1].tag != 'error' :
            for row in root[1][0] :
                k, v = row.get(key), row.get(value)
                names[k] = v
        else :
            for i in IDs :
                err = '(Error loading ID #{})'.format(i)
                names[i] = err
                print(err)
    finally :
        return names

# Returns a dictionary of {id: name} (for players, corps, alliances, moons, systems)
def GetNames (IDs, headers={}) :
    url = "https://api.eveonline.com/eve/CharacterName.xml.aspx?IDs=" + ','.join(IDs)
    savename = cwd + "xml/CharacterName.xml"
    return Convert_IDs(IDs, url, savename, 'characterID', 'name', headers)

# Returns a dictionary of {typeID: typeName} (for item types, not players etc)
def GetTypes (IDs, headers={}) :
    url = "https://api.eveonline.com/eve/TypeName.xml.aspx?IDs=" + ','.join(IDs)
    savename = cwd + "xml/TypeName.xml"
    return Convert_IDs(IDs, url, savename, 'typeID', 'typeName', headers)
