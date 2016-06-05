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
    # iterate over sentences
    for idx, sent in enumerate(sents):
        dsent = " ".join([wf[0] for wf in sent])
        # iterate over vocab terms
        for vb in svb:
            vbinfos = vbs[vb]
            for stg, rg in vbinfos["items"]:
                # search multi-token terms against sentence
                if " " in stg:
                    if re.search(rg, dsent):
                        update_counts(lemtags, stg)
                        update_counts(typetags, vb)
                        update_counts(sents4term, stg, ke2=sfn, sent=dsent)
                # match single-token terms against each lemma (check pos too)
                else:
                    for wf, pos, lemma in sent:
                        if re.match(rg, lemma):
                            if ((vbinfos["tag"] is None) or
                                    (vbinfos["tag"] is not None and
                                        re.match(vbinfos["tag"], pos))):
                                update_counts(lemtags, stg)
                                update_counts(typetags, vb)
                                update_counts(sents4term, stg, ke2=sfn,
                                              sent=dsent)
        if idx and not idx % 100:
            print "    - Done {} of {} sentences, {}".format(
                idx, len(sents), time.strftime("%H:%M:%S", time.localtime()))
    # post-process counts for terms contained in other terms
    dupdi = ut.load_dups(cfg)
    ut.dedup_counts(sfn, lemtags, typetags, dupdi, it2type)
    # update dicts with percentages
    for lem, ct in lemtags.items():
        total4type = typetags[it2type[lem]["type"]]["count"]
        lemtags[lem].update({"percent": 100 * float(ct["count"]) / total4type})
    # remove sentence matches for a term if a superstring also matches
    nsents4term = ut.dedup_sentence_dict(sents4term, dupdi)
    return lemtags, typetags, sents4term, nsents4term


def update_counts(di, ke1, ke2=None, sent=None):
    """
    Update counts dictionary (or sentence dictionary if ke2 is given)
    @param di: dictionary to update
    @param ke1: key to update on (a lemma or a tag (type))
    for lemma and type counts
    @param ke2: key (filename) to update on for term-to-sentence dict
    @param sent: sentence for term-to-sentence dict
    """
    if ke2 is None:
        di.setdefault(ke1, {"count": 0})
        di[ke1]["count"] += 1
    else:
        assert sent is not None
        di.setdefault(ke1, {ke2: []})
        if sent not in di[ke1][ke2]:
            di[ke1][ke2].append(sent)
    #return di


def write_fn2item(di, vcb, cfg, idir, ofn=None):
    """
    Write out di infos, filenames on rows, items (% and fq) on columns
    @di: dict with lexical extraction results
    @vcb: vocabulary that was applied
    @cfg: config module in use
    @ofn: full file path to output file
    """
    if ofn is None:
        ofn = idir + "_fn2term_lexana_{}.tsv".format(SUFFIX)
    print "- Writing fn2item to [{}]".format(ofn)
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


def write_sentences(sdi, vcb, cfg, idir, ofn=None):
    """
    @param sdi: Dict of {key: {fn1: [sents], ...fnn: [sents]}}
    @param vcb: domain vocab
    @param cfg: config
    @param idir: directory with ttg results
    @param ofn: filename for output
    """
    if ofn is None:
        ofn = idir + "_sents_lexana_{}.tsv".format(SUFFIX)
    print "- Writing item2sentence to [{}]".format(ofn)
    # figure out order for write-out
    # tagtype for each vocab item
    it2type = ut.lxitem2type(vcb)
    # filename order
    forder = ut.find_filename_sort_order(cfg)
    # tag order
    tagorder = sorted(vcb, key=lambda vn: cfg.vocorder.index(vn))
    # final order
    sorter = sorted(it2type, key=lambda item: (tagorder.index(
        it2type[item]["type"]), item))
    myorder = sorted(sdi, key=lambda ke: sorter.index(ke))
    ols = []
    for ke, perfile in sorted(sdi.items(),
                              key=lambda its: myorder.index(its[0])):
        for fn, infos in sorted(perfile.items()):
            for sen in infos:
                ols.append(u"{}\t{}\t{}\n".format(ke, fn, sen))
    with codecs.open(ofn, "w", "utf8") as fd:
        fd.write("".join(ols))


def tag_vocab_dir(vbs, cfg, idir):
    """
    Run L{tag_vocab_file} for each file on a dir and aggregate
    results over the directory
    @return: dict with aggregated results
    """
    lemtags = {}
    typetags = {}
    sents4term = {}
    nsents4term = {}
    for idx, fn in enumerate(sorted(os.listdir(idir))):
        if "SPM" not in fn:
            print "- Skip [{}]".format(fn)
            continue
        ffn = os.path.join(idir, fn)
        # lemma counts, type counts, sentences, dedup sentences
        flc, ftc, fs, fns = tag_vocab_file(vbs, cfg, ffn)
        if idx == 50:  # debug
            break
        # check that won't overwrite
        assert fn not in lemtags
        assert fn not in typetags
        # update lemma counts and type counts
        lemtags.update({fn: flc})
        typetags.update({fn: ftc})
        # update sentence dict
        for ke, val in fs.items():
            sents4term.setdefault(ke, {})
            assert len(val.keys()) == 1
            assert val.keys()[0] not in sents4term[ke]
            sents4term[ke].update(val)
        for ke, val in fns.items():
            nsents4term.setdefault(ke, {})
            assert len(val.keys()) == 1
            assert val.keys()[0] not in nsents4term[ke]
            nsents4term[ke].update(val)
    print "Done {} files".format(idx + 1)
    return lemtags, typetags, sents4term, nsents4term


def main(cfg, indir, ofn=None):
    """Run"""
    vocab = ut.load_vocabs(cfg)
    lcs, tcs, scs, nscs = tag_vocab_dir(vocab, cfg, indir)
    write_fn2item(lcs, vocab, cfg, indir, ofn)
    write_sentences(nscs, vocab, cfg, indir, ofn)


if __name__ == "__main__":
    SUFFIX = 23
    main(cf, cf.ttgpath)
    # vocab = ut.load_vocabs(cf)
    # lcs, tcs, scs, nscs = tag_vocab_dir(vocab, cf, cf.ttgpath)
    # #outfn = cf.ttgpath + "_{}_lexana.tsv".format("fn2term")
    # write_fn2item(lcs, vocab, cf, cf.ttgpath)
    # write_sentences(nscs, vocab, cf, cf.ttgpath)