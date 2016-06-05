#coding=utf8


"""General utils for tagging vocabulary in L{../data} """


__author__ = 'Pablo Ruiz'
__date__ = '03/06/16'
__email__ = 'pabloruizfabo@gmail.com'


import codecs
import inspect
import os
import re
import sys


here = os.path.dirname(os.path.abspath(
    inspect.getfile(inspect.currentframe())))
sys.path.append(here)
sys.path.append(os.path.join(here, "config"))

from config import config as cf


def detokenize_ttg_sentences(infi):
    """
    Recreate sentences from treetagger output, based on SENT
    tag and other separators
    @return: List of (wf, pos, lemma) tuples
    @rtype: list
    """
    sents = []
    with codecs.open(infi, "r", "utf8") as infd:
        cursent = []
        oline = infd.readline()
        while oline:
            wf, pos, lemma = oline.strip().split("\t")
            if pos == "SENT" or wf == u"•":
                sents.append(cursent)
                cursent = []
            else:
                cursent.append((wf, pos, lemma))
            oline = infd.readline()
    return sents


def load_vocabs(cfg):
    """
    Return dict with lexical items in vocabulary, as per infos
    in L{cf.config}.
    """
    vd = {}
    for vocab, infos in cfg.datakeys.items():
        ffn = os.path.join(cfg.datapath, infos["fn"])
        with codecs.open(ffn, "r", "utf8") as fd:
            its = [it.strip() for it in fd.readlines()]
        itrgs = [re.compile(ur"\b{}\b".format(it), re.U|re.I)
                 for it in its]
        vd[vocab] = {"ltype": infos["ltype"], "tag": infos["tag"],
                     "vname": infos["fn"].replace(".txt", ""),
                     "items": zip(its, itrgs)}
    return vd


def load_dups(cfg):
    """
    Load config for terms that are a substring (as full word) of other terms
    """
    dupdi = {}
    with codecs.open(cfg.dupterms, "r", "utf8") as fd:
        for line in [ll.strip() for ll in fd.readlines()
                     if not ll.startswith("#")]:
            sl = line.split("\t")
            dupdi[sl[0]] = sl[1].split(";")
    return dupdi


def lxitem2type(vcb):
    """
    Return dict with type (formal or not) and tag for each
    lexical item in vocab
    """
    it2type = {}
    for skey, infos in vcb.items():
        for it in infos["items"]:
            # take index 0, cos index 1 is a regex
            it2type[it[0]] = {"type": skey, "longtype": infos["vname"]}
    return it2type


def dedup_counts(fn, lemdi, typedi, dupdi, item2type):
    """
    Given a dictionary with counts and a config of potential duplicate counts,
    remove the duplicates.
    E.g. subtract counts for "very confident" from counts for "confident"
    @param fn: filename for file we're working on
    @param lemdi: dict with lemma counts
    @param typedi: dict with lexical type counts
    @param dupdi: dictionary substring-to-superstring
    @param item2type: dict giving lex type and other infos for each lemma
    in the vocabulary, created with L{lxitem2type} above.
    """
    for sub, superlist in dupdi.items():
        for supert in superlist:
            try:
                oldcount = lemdi[sub]["count"]
                lemdi[sub]["count"] -= lemdi[supert]["count"]
                print "{}- Updating count for [{} ({})] from {} to {}".format(
                    " " * 8, sub, supert, oldcount, lemdi[sub]["count"])
            except KeyError:
                print "{}- Key [{}|{}] not in file [{}]".format(
                    " " * 8, sub, supert, fn)
                pass
            try:
                oldtagcount = typedi[item2type[sub]["type"]]["count"]
                typedi[item2type[sub]["type"]]["count"] -= lemdi[supert]["count"]
                print "{}- Updating TAG count for [{}] from {} to {}".format(
                    " " * 8, item2type[sub]["type"], oldtagcount,
                    typedi[item2type[sub]["type"]]["count"])
            except KeyError:
                print "{}- Key [{}|{}] not in file [{}]".format(
                    " " * 8, item2type[sub]["type"], item2type[supert]["type"],
                    fn)
                pass


def find_filename_sort_order(cfg):
    return ([ll.strip() for ll in
             codecs.open(cfg.chosenfilespath, "r", "utf8").readlines()
             if not ll.startswith("#")])


# test
if __name__ == "__main__":
    # sent detokenization from ttg
    infn = "/home/pablo/projects/clm/ipcc_norm_wk/results_06032016/CSV_06032016_ttg/AR1_WG1_SPM.csv"
    sts = detokenize_ttg_sentences(infn)
    assert sts[0] == [(u'SPM|We', u'NNS', u'<unknown>'), (u'are', u'VBP', u'be'), (u'certain', u'JJ', u'certain'), (u'of', u'IN', u'of'), (u'the', u'DT', u'the'), (u'following', u'NN', u'following'), (u':', u':', u':')]
    # vocab loading
    vbs = load_vocabs(cf)

