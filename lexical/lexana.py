"""To apply GSB's vocab lists"""

__author__ = 'Pablo Ruiz'
__date__ = '04/06/16'
__email__ = 'pabloruizfabo@gmail.com'


import codecs
import inspect
import os
import re
import sys
import time


here = os.path.dirname(os.path.abspath(
    inspect.getfile(inspect.currentframe())))
sys.path.append(here)
sys.path.append(os.path.join(here, "config"))

import utils as ut
from config import config as cf


def tag_vocab_file(vbs, cfg, ffn):
    """
    Tag vocab elements in treetagger output (tokens or detokenized sentences).
    Keep count per lemma and type
    Keep sentence occurrences for each lemma
    @param vbs: vocab to apply
    @param cfg: the config module to apply
    @param ffn: full path to file to tag
    @return: dict with counts and percentages for each tag for the file
    """
    sfn = os.path.split(ffn)[1]
    print "- File [{}], {}".format(sfn, time.strftime(
        "%H:%M:%S", time.localtime()))
    it2type = ut.lxitem2type(vbs)
    lemtags = {}
    typetags = {}
    sents4term = {}
    svb = sorted(vbs, key=lambda di: cfg.vocorder.index(di))
    sents = ut.detokenize_ttg_sentences(ffn)
    print "  - Total sentences: {}".format(len(sents))
    for idx, sent in enumerate(sents):
        dsent = " ".join([wf[0] for wf in sent])
        for wf, pos, lemma in sent:
            for vb in svb:
                vbinfos = vbs[vb]
                for stg, rg in vbinfos["items"]:
                    #TODO: fix this cos need to search this ONCE
                    #TODO: PER SENTENCE not like now, for every word
                    # multi-token term
                    if " " in stg:
                        if re.search(rg, dsent):
                            # count for lemma
                            lemtags.setdefault(stg, {"count": 0})
                            lemtags[stg]["count"] += 1
                            # count for the lex type
                            typetags.setdefault(vb, {"count": 0})
                            typetags[vb]["count"] += 1
                            # sentences for lemma
                            sents4term.setdefault(stg, {sfn: []})
                            if dsent not in sents4term[stg][sfn]:
                                sents4term[stg][sfn].append(dsent)
                    # single-token term
                    if re.match(rg, lemma):
                        if ((vbinfos["tag"] is None) or
                                (vbinfos["tag"] is not None and
                                    re.match(vbinfos["tag"], pos))):
                            # count for lemma
                            lemtags.setdefault(stg, {"count": 0})
                            lemtags[stg]["count"] += 1
                            # count for the lex type
                            typetags.setdefault(vb, {"count": 0})
                            typetags[vb]["count"] += 1
                            # sentences for lemma
                            sents4term.setdefault(stg, {sfn: []})
                            if dsent not in sents4term[stg][sfn]:
                                sents4term[stg][sfn].append(dsent)
        if idx and not idx % 100:
            print "    - Done {} of {} sentences, {}".format(
                idx, len(sents), time.strftime("%H:%M:%S", time.localtime()))
    # update dicts with percentages
    for lem, ct in lemtags.items():
        total4type = typetags[it2type[lem]["type"]]["count"]
        lemtags[lem].update({"percent": 100 * float(ct["count"]) / total4type})
    return lemtags, typetags, sents4term


def update_counts(di, ke1, ke2=None, sent=None):
    """
    Update counts dictionary (or sentence dictionary if ke2 is given)
    """
    #TODO: test this after running the above version
    if ke2 is None:
        di.setdefault(ke1, {"count": 0})
        di[ke1]["count"] += 1
    else:
        assert sent is not None
        di.setdefault(ke1, {ke2: []})
        if sent not in di[ke1][ke2]:
            di[ke1][ke2].append(sent)
    return di


def write_fn2item(di, vcb, cfg, idir, ofn=None):
    """
    Write out di infos, filenames on rows, items (% and fq) on columns
    @di: dict with lexical extraction results
    @vcb: vocabulary that was applied
    @cfg: config module in use
    @ofn: full file path to output file
    """
    if ofn is None:
        ofn = idir + "_fn2term_lexana.tsv"
    # filename order
    forder = ut.find_filename_sort_order(cfg)
    # tag order
    tagorder = sorted(vcb, key=lambda vn: cfg.vocorder.index(vn))
    # tagtype for each vocab item
    it2type = ut.lxitem2type(vcb)
    # headers
    headers = sorted(it2type, key=lambda item: (tagorder.index(
        it2type[item]["type"]), item))
    headers2 = [u"{}_{}_%\t{}_{}_fq".format(
        it2type[hd]["type"], hd, it2type[hd]["type"], hd) for hd in headers]
    # write
    with codecs.open(ofn, "w", "utf8") as ofd:
        ofd.write("\t" + "\t".join(headers2) + "\n")
        for fn in sorted(di, key=lambda fname: forder.index(fname)):
            outlist = [fn]
            for hd in headers:
                try:
                    outlist.extend((di[fn][hd]["percent"],
                                    di[fn][hd]["count"]))
                except KeyError:
                    outlist.extend((0, 0))
            ofd.write("\t".join([unicode(it) for it in outlist]) + "\n")


def tag_vocab_dir(vbs, cfg, idir):
    """
    Run L{tag_vocab_file} for each file on a dir and aggregate
    results over the directory
    @return: dict with aggregated results
    """
    lemtags = {}
    typetags = {}
    sents4term = {}
    for idx, fn in enumerate(sorted(os.listdir(idir))):
        if "SPM" not in fn:
            print "- Skip [{}]".format(fn)
            continue
        ffn = os.path.join(idir, fn)
        # lemma counts, type counts, sentences
        flc, ftc, fs = tag_vocab_file(vbs, cfg, ffn)
        if idx == 50:  # debug
            break
        # check that won't overwrite
        assert fn not in lemtags
        assert fn not in typetags
        assert fn not in sents4term
        # update
        lemtags.update({fn: flc})
        typetags.update({fn: ftc})
        sents4term.update({fn: fs})
    print "Done {} files".format(idx + 1)
    return lemtags, typetags, sents4term


def main(cfg, indir, ofn=None):
    """Run"""
    vocab = ut.load_vocabs(cfg)
    lcs, tcs, scs = tag_vocab_dir(vocab, cfg, indir)
    write_fn2item(lcs, vocab, cfg, indir, ofn)


if __name__ == "__main__":
    #main(cf, cf.ttgpath, ")
    vocab = ut.load_vocabs(cf)
    lcs, tcs, scs = tag_vocab_dir(vocab, cf, cf.ttgpath)
    #outfn = cf.ttgpath + "_{}_lexana.tsv".format("fn2term")
    write_fn2item(lcs, vocab, cf, cf.ttgpath)
