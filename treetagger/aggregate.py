"""Aggregate percentages of part--of-speech tags in IPCC"""

__author__ = 'Pablo Ruiz'
__date__ = '27/03/16'
__email__ = 'pabloruizfabo@gmail.com'


import codecs
import inspect
from numpy.testing import assert_almost_equal
import os
import sys


here = os.path.dirname(os.path.abspath(
    inspect.getfile(inspect.currentframe())))
sys.path.append(here)


# I/O
# to sort filenames and pos tags
fsorter = [ll.strip() for ll in codecs.open(
    os.path.join(os.path.join(here, "data"), "sort_filenames.txt"),
    "r", "utf8").readlines() if not ll.startswith("#")]
psorter = [ll.strip() for ll in codecs.open(
    os.path.join(os.path.join(here, "data"), "sort_pos.txt"),
    "r", "utf8").readlines() if not ll.startswith("#")]
# percentages of pos per file
try:
    pcdir = sys.argv[1]
except IndexError:
    #pcdir = "/home/pablo/projects/clm/ipcc_norm_wk/out_treetagger/final/out_treetagger_new_summaries6"
    pcdir = "/home/pablo/projects/clm/ipcc_norm_wk/CSV_03302016_ttg_summaries_03302016"
ofile = os.path.join(os.path.join(pcdir, os.pardir), "pos2fn_03302016.tsv")
ofile2 = os.path.join(os.path.join(pcdir, os.pardir), "fn2pos_03302016.tsv")


def aggregate(idir, fsort, psort):
    """Get the infos into a hash by fn and pos"""
    out = {}
    for fn in os.listdir(idir):
        if fn not in fsort:
            continue
        print "Reading {}".format(fn)
        out.setdefault(fn, {})
        for pos in psort:
            out[fn].setdefault(pos, (0, 0))
        with codecs.open(os.path.join(idir, fn), "r", "utf8") as ifd:
            line = ifd.readline()
            while line:
                sl = line.strip().split("\t")
                tag, count, pc = sl[0], sl[1], sl[2]
                if tag in psort:
                    assert tag in out[fn]
                    out[fn][tag] = (count, pc)
                line = ifd.readline()
    return out


def write(di, fsort, psort, ofn):
    """Columns are filenames, rows are pos"""
    headers = sorted(di, key=lambda ke:fsort.index(ke))
    hd2 = "\t".join(["\t".join((h + "_%", h + "_PC")) for h in headers])
    with codecs.open(ofn, "w", "utf8") as ofd:
        # header
        ofd.write("\t" + hd2 + "\n")
        for pos in psort:
            ofd.write(pos + "\t" + "\t".join(
                ["\t".join((unicode(di[fn][pos][-1]), unicode(di[fn][pos][0])))
                 for fn in fsort]) + "\n")


def write2(di, fsort, psort, ofn):
    """Columns are pos, rows are filenames"""
    headers = "\t".join(["\t".join((ps + "_%", ps + "_FQ")) for ps in psort])
    with codecs.open(ofn, "w", "utf8") as ofd:
        ofd.write("\t" + headers + "\n")
        for fn in fsort:
            infos = "\t".join(
                ["\t".join((unicode(di[fn][pos][-1]), unicode(di[fn][pos][0])))
                 for pos in psort])
            ofd.write("".join((fn, "\t", infos, "\n")))


if __name__ == "__main__":
    infos = aggregate(pcdir, fsorter, psorter)
    write(infos, fsorter, psorter, ofile)
    write2(infos, fsorter, psorter, ofile2)