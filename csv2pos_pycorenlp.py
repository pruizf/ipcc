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


def process_file(fni, outdir, pos_dict=None):
    global tags
    global jstags
    server = StanfordCoreNLP("http://localhost:9000")
    dones = 0
    fnpos = os.path.join(outdir, os.path.splitext(os.path.basename(fni))[0]
                         + "_pos3.txt")
    fnfrq = os.path.join(outdir, os.path.splitext(os.path.basename(fni))[0]
                         + "_frq.txt")
    if os.path.exists(fnpos):
        print "= Removing old copy of [{}]".format(fnpos)
        os.remove(fnpos)
    if os.path.exists(fnfrq):
        print "= Removing old copy of [{}]".format(fnfrq)
        os.remove(fnfrq)
    if pos_dict is None:
        pos_dict = {}
    with codecs.open(fnpos, "w", "utf8") as fdpos, \
         codecs.open(fnfrq, "w", "utf8") as fdfrq:
        for ll in read_csv(fni):
            tags = tag_txt(server, ll)
            linetoks = extract_pos_tags(tags)
            for tok in linetoks:
                if len(tok) > 0:
                    pos_dict.setdefault(tok[1], 0)
                    pos_dict[tok[1]] += 1
                ol = "\t".join([unicode(it) for it in tok])
                fdpos.write(u"{}\n".format(ol))
            #dones += 1
            #if dones == 1:
            #    break
        for ke, va in sorted(pos_dict.items(), key=lambda tu: -tu[1]):
            fdfrq.write(u"{}\t{}\n".format(ke, va))
    return pos_dict


def process_dir(dr, out4dir):
    for idx, fn in enumerate(sorted(os.listdir(dr))):
        if idx == 0:
            counts = process_file(os.path.join(dr, fn), {})
        else:
            counts = process_file(os.path.join(dr, fn), counts)


if __name__ == "__main__":
    try:
        infi = sys.argv[1]
        #indir = sys.argv[1]
    except IndexError:
        infi = "/home/pablo/Insync/Text IPCC/Corpus/CSV/AR4/AR4-WGI/AR4-WGI.csv"
        #indir = ""
        #infi = "/home/pablo/projects/clm/ipcc_norm_wk/tests/accents.txt"
    try:
        outd = sys.argv[2]
    except IndexError:
        outd = "/home/pablo/projects/clm/ipcc_norm_wk/out"
        #allout = os.path.join(outdir, os.path.basename(indir))
    counts = process_file(infi, outd)
    #process_dir(indir)