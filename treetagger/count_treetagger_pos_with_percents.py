"""#"""
__author__ = 'Pablo Ruiz'
__date__ = '04/03/16'
__email__ = 'pabloruizfabo@gmail.com'


import codecs
from collections import Counter
import inspect
from numpy.testing import assert_almost_equal
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
                tagcount.setdefault(sl[1], {"count": 0,
                                            "percent": 0})
                tagcount[sl[1]]["count"] += 1
                if not sl[1]:
                    import pdb;pdb.set_trace()
                summary.setdefault(tm[sl[1]]["short"], {"count": 0,
                                                        "percent": 0})
                summary[tm[sl[1]]["short"]]["count"] += 1
            except KeyError:
                # must be cases where there's no normalized tag
                # (e.g. punctuation, where the tag is the character)
                summary.setdefault(sl[1], {"count": 0,
                                           "percent": 0})
                summary[sl[1]]["count"] += 1
            except IndexError:
                print u"ERROR\n{}\n".format(line)
                line = fdi.readline()
                continue
            line = fdi.readline()
    # percentages
    ttlcount = sum([va["count"] for va in tagcount.values()])
    ttlsummary = sum([va["count"] for va in summary.values()])
    ttltagcpc = 0
    ttlsummpc = 0
    for ke, va in tagcount.items():
        assert not tagcount[ke]["percent"]
        tagcount[ke]["percent"] = 100 * float(va["count"]) / ttlcount
        ttltagcpc += tagcount[ke]["percent"]
    assert_almost_equal(ttltagcpc, 100)
    tagcount["total_count"] = {"count": ttlcount, "percent": 100}
    for ke, va in summary.items():
        assert not summary[ke]["percent"]
        summary[ke]["percent"] = 100 * float(va["count"]) / ttlsummary
        ttlsummpc += summary[ke]["percent"]
    assert_almost_equal(ttlsummpc, 100)
    summary["total_count"] = {"count": ttlsummary, "percent": 100}
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
            co[ke] = [[k, v] for (k, v) in sorted(
                Counter(va).items(), key=lambda kv: -kv[1])][0:TOPTERMS]
    # add percentages
    totspercat = {}
    for ke2, va2 in co.items():
        totspercat[ke2] = sum([vl[-1] for vl in va2])
    for ke3, valist in co.items():
        totpcnt = 0
        for val in valist:
            # val[1] is freq
            val.append(100 * float(val[1]) / totspercat[ke3])
            totpcnt += 100 * float(val[1]) / totspercat[ke3]
        assert_almost_equal(totpcnt, 100)
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
            for ke, va in sorted(fcounts.items(),
                                 key=lambda tu: -tu[1]["count"]):
                if ke == "total_count":
                    continue
                try:
                    ol1 = "\t".join((tgmap[ke]["short"], ke))
                    ol2 = tgmap[ke]["long"]
                except KeyError:
                    # tags that equal the word-form (punctuation)
                    ol1 = "\t".join((ke, ke))
                    ol2 = ke
                ofd.write(u"{}\t{}\t{}\t{}\n".format(ol1, va["count"],
                                                     va["percent"], ol2))
            ofd.write(u"{}\t{}\t{}\t{}\n".format(
                "total_count\ttotal_count", fcounts["total_count"]["count"],
                100, "total_count"))
        # summarized output infos
        with codecs.open(os.path.join(osu, fn), "w", "utf8") as osfd:
            for ke2, va2 in sorted(scounts.items(),
                                   key=lambda tu: -tu[1]["count"]):
                if ke2 == "total_count":
                    continue
                osfd.write(u"{}\t{}\t{}\n".format(ke2, va2["count"],
                                                  va2["percent"]))
            osfd.write(u"{}\t{}\t{}\n".format(
                "total_count", scounts["total_count"]["count"], 100))
        # top-N infos
        with codecs.open(os.path.join(td, fn), "w", "utf8") as tfd:
            for pos in POS4TOPS:
                #tcounts: 0 is wf, 1 is count, 2 is percent
                for wf, frq, pcnt in tcounts[pos]:
                    tfd.write(u"{}\t{}\t{}\t{}\n".format(pos, wf, frq, pcnt))


if __name__ == "__main__":
    tmap = create_tagset_map()
    try:
        indir = sys.argv[1]
    except IndexError:
        #indir = "/home/pablo/projects/clm/ipcc_norm_wk/out_treetagger_orig"
        #indir = "/home/pablo/projects/clm/ipcc_norm_wk/out_treetagger/final/out_treetagger_new"
        indir = "/home/pablo/projects/clm/ipcc_norm_wk/CSV_04152016_ttg"
    if not os.path.exists(indir):
        print "Input path not found: {}".format(indir)
        sys.exit(2)
    outdir = indir + "_counts_04152016"
    summaries = indir + "_summaries_04152016"
    tops = indir + "_tops_0415206"
    for dr in (outdir, summaries, tops):
        if not os.path.exists(dr):
            os.makedirs(dr)
    run_dir(indir, tmap, outdir, summaries, tops)
