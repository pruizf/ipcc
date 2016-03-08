"""#"""
__author__ = 'Pablo Ruiz'
__date__ = '04/03/16'
__email__ = 'pabloruizfabo@gmail.com'


import codecs
from collections import Counter
import inspect
import os
from string import punctuation
import sys


here = os.path.dirname(os.path.abspath(
    inspect.getfile(inspect.currentframe())))
sys.path.append(here)

TOPTERMS = 20
POS4TOPS = ["noun", "proper noun", "adjective", "verb", "modal", "adverb",
            "preposition/subord. conj."]

def create_tagset_map():
    """Hash acronym, coarse and fine versions of each tag"""
    with codecs.open(here + os.sep + "data" + os.sep +
                     "treetagger_ptb_tagset.txt", "r",
                     "utf8") as infi:
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


def count_tags_for_file(fi, tm):
    """Get frequencies per pos (fine and coarse grain)"""
    tagcount = {}
    summary = {}
    with codecs.open(fi, "r", "utf8") as fdi:
        line = fdi.readline()
        while line:
            sl = line.strip().split("\t")
            try:
                tagcount.setdefault(sl[1], 0)
                tagcount[sl[1]] += 1
                if not sl[1]:
                    import pdb;pdb.set_trace()
                summary.setdefault(tm[sl[1]]["short"], 0)
                summary[tm[sl[1]]["short"]] += 1
            except KeyError:
                summary.setdefault(sl[1], 0)
                summary[sl[1]] += 1
            except IndexError:
                print u"ERROR\n{}\n".format(line)
                line = fdi.readline()
                continue
            line = fdi.readline()
    #TODO: add percentages??
    return tagcount, summary


def count_word_forms_for_pos(fi, tm):
    """
    Get top x word forms for a set of coarse tags.
    Forms are lowercased.
    """
    di = {}
    co = {}
    with codecs.open(fi, "r", "utf8") as fdi:
        line = fdi.readline()
        while line:
            sl = line.strip().split()
            try:
                if sl[1].startswith("NP"):
                    form2add = sl[0]
                else:
                    form2add = sl[0].lower()
                di.setdefault(tm[sl[1]]["short"], []).append(form2add)
            except KeyError:
                if sl[1] in punctuation:
                    line = fdi.readline()
                    continue
            line = fdi.readline()
    for ke, va in di.items():
        if ke in POS4TOPS:
            co[ke] = [(k, v) for (k, v) in sorted(
                Counter(va).items(), key=lambda kv: -kv[1])][0:TOPTERMS]
    return co


def run_dir(di, tgmap, odi, osu, td):
    for fn in os.listdir(di):
        print "- Processing {}".format(fn)
        ffn = os.path.join(di, fn)
        # fine and coarse grain counts
        fcounts, scounts = count_tags_for_file(ffn, tgmap)
        # counts for top x words in each tag
        tcounts = count_word_forms_for_pos(ffn, tgmap)
        # detailed output infos
        with codecs.open(os.path.join(odi, fn), "w", "utf8") as ofd:
            for ke, va in sorted(fcounts.items(), key=lambda tu: -tu[1]):
                try:
                    ol1 = "\t".join((tgmap[ke]["short"], ke))
                    ol2 = tgmap[ke]["long"]
                except KeyError:
                    # tags that equal the word-form (punctuation)
                    ol1 = "\t".join((ke, ke))
                    ol2 = ke
                ofd.write(u"{}\t{}\t{}\n".format(ol1, va, ol2))
        # summarized output infos
        with codecs.open(os.path.join(osu, fn), "w", "utf8") as osfd:
            for ke2, va2 in sorted(scounts.items(), key=lambda tu: -tu[1]):
                osfd.write(u"{}\t{}\n".format(ke2, va2))
        # top-N infos
        with codecs.open(os.path.join(td, fn), "w", "utf8") as tfd:
            for pos in POS4TOPS:
                for ke3, va3 in tcounts[pos]:
                    tfd.write(u"{}\t{}\t{}\n".format(pos, ke3, va3))


if __name__ == "__main__":
    tmap = create_tagset_map()
    try:
        indir = sys.argv[1]
    except IndexError:
        #indir = "/home/pablo/projects/clm/ipcc_norm_wk/out_treetagger_orig"
        indir = "/home/pablo/projects/clm/ipcc_norm_wk/out_treetagger/final/out_treetagger_new"
    outdir = indir + "_counts3"
    summaries = indir + "_summaries3"
    tops = indir + "_tops3"
    for dr in (outdir, summaries, tops):
        if not os.path.exists(dr):
            os.makedirs(dr)
    run_dir(indir, tmap, outdir, summaries, tops)