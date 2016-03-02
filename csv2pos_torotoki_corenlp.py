"""Working on CSV provided by mlb, pos tag them, output distribs"""


__author__ = 'Pablo Ruiz'
__date__ = '02/03/16'
__email__ = 'pabloruizfabo@gmail.com'


import codecs
import re
import sys
import unicodecsv

import jsonrpclib
import json


def read_csv(inf):
    with open(inf, "r") as data:
        reader = unicodecsv.reader(data, encoding="utf8")
        for row in reader:
            alltxt = "\n".join((row[0], row[1]))
            yield alltxt


def tag_txt_simple(svr, txt):
    ptxt = svr.parse(txt)
    return ptxt


def extract_pos_tags(tagged):
    global lits
    js = json.loads(tagged)
    for sen in js["sentences"]:
        print "==" + sen["text"] + "=="
        lits = re.findall(r"\[[^]]+\]", sen["parsetree"])
        for li in lits:
            wf = re.search("Text=(\w+)", li).group(1)
            start = int(re.search("CharacterOffsetBegin=(\w+)", li).group(1))
            end = int(re.search("CharacterOffsetEnd=(\w+)", li).group(1))
            pos = re.search("PartOfSpeech=(\w+)", li).group(1)
            print wf, start, end, pos



def tag_txt_batch(svr, dir):
    pass


def main(fni):
    global tags
    global jstags
    server = jsonrpclib.Server("http://localhost:8080")
    dones = 0
    for ll in read_csv(fni):
        tags = tag_txt_simple(server, ll)
        jstags = json.loads(tags)
        extract_pos_tags(tags)
        dones += 1
        if dones == 1:
            break


if __name__ == "__main__":
    try:
        infi = sys.argv[1]
    except IndexError:
        infi = "/home/pablo/Insync/Text IPCC/Corpus/CSV/AR4/AR4-WGI/AR4-WGI.csv"
    try:
        outdir = sys.argv[2]
    except IndexError:
        outdir = ""
    main(infi)