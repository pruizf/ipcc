"""Working on CSV provided by mlb, pos tag them, output distribs"""


__author__ = 'Pablo Ruiz'
__date__ = '02/03/16'
__email__ = 'pabloruizfabo@gmail.com'


import codecs
import inspect
import os
import re
import requests
import sys
import time
import unicodecsv

from pycorenlp import StanfordCoreNLP


here = os.path.dirname(os.path.abspath(
    inspect.getfile(inspect.currentframe())))
sys.path.append(here)

# increase csv reader max field size
unicodecsv.field_size_limit(sys.maxsize)


def create_tagset_map():
    with codecs.open(here + os.sep + "data" + os.sep + "ptb_tagset.txt",
                     "r", "utf8") as infi:
        tagmap = {}
        line = infi.readline()
        while line:
            sl = line.split("\t")
            label, llabel, slabel = (
                sl[0], sl[1].strip().lower(),
                sl[1].split(",")[0].strip().lower())
            tagmap[label] = {"short": slabel, "long": llabel}
            line = infi.readline()
    return tagmap


def read_csv(inf):
    with open(inf, "r") as data:
        reader = unicodecsv.reader(data, encoding="utf8")
        #reader = csv.reader(data)
        for idx, row in enumerate(reader):
            # looks like server wants strings
            alltxt = u".\n".join((row[0], row[1])).encode("utf8")
            # server has a request size limit
            splits = []
            if len(alltxt) > 100000:
                start = 0
                final = 100000
                while final < len(alltxt):
                #while len(alltxt[final:]) > 100000:
                    splits.append(alltxt[start:final])
                    start = final
                    final += 100000
                #splits.append(alltxt[final:])
                splits.append(alltxt[start:])
                yield splits
            else:
                yield [alltxt]
            if idx and not idx % 100:
                print "Done {} lines, {}".format(idx, time.strftime(
                    "%H:%M:%S", time.localtime()))


def read_pipe_separated(inf):
    with codecs.open(inf, "r", "utf8") as data:
        line = data.readline()
        dones = 0
        while line:
            bits = line.split("|")
            try:
                alltxt = u"\n.".join((bits[0], bits[1])).encode("utf8")
            except IndexError:
                alltxt = line.encode("utf8")
            if dones and not dones % 100:
                 print "Done {} lines, {}".format(dones, time.strftime(
                     "%H:%M:%S", time.localtime()))
            # server request size limit at 100000
            splits = []
            if len(alltxt) > 100000:
                start = 0
                final = 100000
                while final < len(alltxt):
                #while len(alltxt[final:]) > 100000:
                    splits.append(alltxt[start:final])
                    start = final
                    final += 100000
                #splits.append(alltxt[final:])
                splits.append(alltxt[start:])
                yield splits
            else:
                yield [alltxt]
            dones += 1
            line = data.readline()


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


def process_file(fni, outdir, tgmap, fmt="pipes"):
    server = StanfordCoreNLP("http://localhost:9000")
    fnpos = os.path.join(outdir, os.path.splitext(os.path.basename(fni))[0]
                         + "_pos.txt")
    fnfrq = os.path.join(outdir, os.path.splitext(os.path.basename(fni))[0]
                         + "_frq.txt")
    if os.path.exists(fnpos):
        print "= Removing old copy of [{}]".format(fnpos)
        os.remove(fnpos)
    if os.path.exists(fnfrq):
        print "= Removing old copy of [{}]".format(fnfrq)
        os.remove(fnfrq)
    pos_dict = {}
    with codecs.open(fnpos, "w", "utf8") as fdpos, \
         codecs.open(fnfrq, "w", "utf8") as fdfrq:
        print "  - Writing POS to {}".format(fnpos)
        print "  - Writing Frq to {}".format(fnfrq)
        if fmt == "pipes":
            reader = read_pipe_separated
        else:
            reader = read_csv
        for ll in reader(fni):
            for bit in ll:
                try:
                    assert len(bit) <= 100000
                except AssertionError:
                    import pdb;pdb.set_trace()
                try:
                    tags = tag_txt(server, bit)
                except requests.ConnectionError:
                    print u"\n\nCONNECTION_ERROR: [PART={}||LINE={}]\n\n".format(
                        repr(bit), "")
                if tags == "Could not handle incoming annotation":
                    print u"\n\nSERVER_ERROR: [PART={}||LINE={}]\n\n".format(
                        repr(bit), "")
                    continue
                elif isinstance(tags, unicode) and tags.startswith("<head>\n"):
                    print u"\n\nRESPONSE_ERROR\n\n"
                    continue
                linetoks = extract_pos_tags(tags)
                for tok in linetoks:
                    if len(tok) > 0:
                        pos_dict.setdefault(tok[1], 0)
                        pos_dict[tok[1]] += 1
                    ol = "\t".join([unicode(it) for it in tok])
                    fdpos.write(u"{}\n".format(ol))
        for ke, va in sorted(pos_dict.items(), key=lambda tu: -tu[1]):
            try:
                ol1 = "\t".join((tgmap[ke]["short"], ke))
                ol2 = tgmap[ke]["long"]
            except KeyError:
                # tags that equal the word-form (punctuation)
                ol1 = "\t".join((ke, ke))
                ol2 = ke
            fdfrq.write(u"{}\t{}\t{}\n".format(ol1, va, ol2))


if __name__ == "__main__":
    try:
        infi = sys.argv[1]
    except IndexError:
        #infi = "/home/pablo/Insync/Text IPCC/Corpus/CSV/AR4/AR4-WGI/AR4-WGI.csv"
        infi = "/home/pablo/projects/clm/ipcc_norm_wk/CSV/AR2/AR2_WG1_Rap.csv"
    try:
        outd = sys.argv[2]
    except IndexError:
        outd = "/home/pablo/projects/clm/ipcc_norm_wk/out"
    try:
        iformat = sys.argv[3]
    except IndexError:
        iformat = "pipes"
    tmap = create_tagset_map()
    process_file(infi, outd, tmap, fmt=iformat)
