"""Working on CSV provided by mlb, pos tag them, output distribs"""


__author__ = 'Pablo Ruiz'
__date__ = '02/03/16'
__email__ = 'pabloruizfabo@gmail.com'


import codecs
import json
import os
import re
import sys
import unicodecsv
import csv

from pprint import pprint
from pycorenlp import StanfordCoreNLP


def normalize_text(txt):
    txt = txt.replace(u"\ufeff", " ")
    txt = re.sub(r"[ ]{2,}", " ", txt)
    #txt = re.sub(u'\xb1', "+/-", txt)
    return txt


def read_csv(inf):
    with open(inf, "r") as data:
        reader = unicodecsv.reader(data, encoding="utf8")
        #reader = csv.reader(data)
        for row in reader:
            # looks like server wants strings
            alltxt = u".\n".join((row[0], row[1])).encode("utf8")
            yield alltxt


def tag_txt(svr, txt):
    ptxt = svr.annotate(txt, properties={
        "annotators": "ssplit,tokenize,pos",
        "outputFormat": "json"})
    return ptxt


def extract_pos_tags(tagged):
    alltoks = []
    for sen in tagged["sentences"]:
        for tok in sen["tokens"]:
            # workaround for encoding pbs
            wf = tok["word"].encode("latin1").decode("utf8")
            pos = tok["pos"]
            start = int(tok["characterOffsetBegin"])
            end = int(tok["characterOffsetEnd"])
            alltoks.append((wf, pos, start, end))
        alltoks.append(())
    return alltoks


def tag_txt_batch(svr, dir):
    pass


def main(fni):
    global tags
    global jstags
    server = StanfordCoreNLP("http://localhost:9000")
    dones = 0
    fno = os.path.join(outdir, os.path.splitext(os.path.basename(fni))[0]
                       + "_pos2.txt")
    if os.path.exists(fno):
        print "= Removing old copy of [{}]".format(fno)
        os.remove(fno)
    with codecs.open(fno, "w", "utf8") as fdo:
        for ll in read_csv(fni):
            tags = tag_txt(server, ll)
            ltoks = extract_pos_tags(tags)
            for tok in ltoks:
                ol = "\t".join([unicode(it) for it in tok])
                fdo.write(u"{}\n".format(ol))
            #dones += 1
            #if dones == 1:
            #    break


if __name__ == "__main__":
    try:
        infi = sys.argv[1]
    except IndexError:
        infi = "/home/pablo/Insync/Text IPCC/Corpus/CSV/AR4/AR4-WGI/AR4-WGI.csv"
        #infi = "/home/pablo/projects/clm/ipcc_norm_wk/tests/accents.txt"
    try:
        outdir = sys.argv[2]
    except IndexError:
        outdir = "/home/pablo/projects/clm/ipcc_norm_wk/out"
    main(infi)