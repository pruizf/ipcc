"""#"""
__author__ = 'Pablo Ruiz'
__date__ = '04/03/16'
__email__ = 'pabloruizfabo@gmail.com'


import codecs
import inspect
import os
import sys


here = os.path.dirname(os.path.abspath(
    inspect.getfile(inspect.currentframe())))
sys.path.append(here)


def create_tagset_map():
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


def count_tags_for_file(fi):
    tagcount = {}
    with codecs.open(fi, "r", "utf8") as fdi:
        line = fdi.readline()
        while line:
            sl = line.strip().split("\t")
            try:
                tagcount.setdefault(sl[1], 0)
                tagcount[sl[1]] += 1
            except IndexError:
                print u"ERROR\n{}\n".format(line)
                line = fdi.readline()
                continue
            line = fdi.readline()
    return tagcount


def run_dir(di, tgmap, odi):
    for fn in os.listdir(di):
        print "- Processing {}".format(fn)
        ffn = os.path.join(di, fn)
        fcounts = count_tags_for_file(ffn)
        with codecs.open(os.path.join(odi, fn), "w", "utf8") as ofd:
            # for ke, va in sorted(fcounts.items(), key=lambda tu: -tu[1]):
            #     ofd.write(u"{}\t{}\n".format(ke, va))
            for ke, va in sorted(fcounts.items(), key=lambda tu: -tu[1]):
                try:
                    ol1 = "\t".join((tgmap[ke]["short"], ke))
                    ol2 = tgmap[ke]["long"]
                except KeyError:
                    # tags that equal the word-form (punctuation)
                    ol1 = "\t".join((ke, ke))
                    ol2 = ke
                ofd.write(u"{}\t{}\t{}\n".format(ol1, va, ol2))


if __name__ == "__main__":
    tmap = create_tagset_map()
    try:
        indir = sys.argv[1]
    except IndexError:
        #indir = "/home/pablo/projects/clm/ipcc_norm_wk/out_treetagger_orig"
        indir = "/home/pablo/projects/clm/ipcc_norm_wk/out_treetagger_new"
    outdir = indir + "_counts"
    if not os.path.exists(outdir):
        os.makedirs(outdir)
    run_dir(indir, tmap, outdir)