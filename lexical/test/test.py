"""Tests lexical extraction"""

__author__ = 'Pablo Ruiz'
__date__ = '07/06/16'
__email__ = 'pabloruizfabo@gmail.com'

import codecs
import inspect
from numpy.testing import assert_almost_equal
import os
import sys


here = os.path.dirname(os.path.abspath(
    inspect.getfile(inspect.currentframe())))
sys.path.append(os.path.join(here, os.pardir))
sys.path.append(os.path.join(os.path.join(here, os.pardir), "config"))

# unused for now cos just comparing written results
import lexana as la
import utils as ut
from config import config as cf


def parse_results(rf):
    """
    Read results off L{lexana.write_fn2item} format into a dict
    with term/fn keys
    """
    with codecs.open(rf, "r", "utf8") as fd:
        lines = fd.readlines()
        sls = [ll.strip().split("\t") for ll in lines]
        headers = sls[0]
        fns = [col[0] for col in sls]
    res = {}
    for hidx, term in enumerate(headers):
        for fnidx, fn in enumerate(fns):
            if fnidx == 0:
                continue
            res.setdefault(term, {})
            res[term].setdefault(fn, float(sls[fnidx][hidx+1]))
    return res


def check(gol, stm):
    """Print errors with their keys"""
    allok = True
    noheader = True
    for tk, fninfos in gol.items():
        for fn in fninfos:
            try:
                assert_almost_equal(stm[tk][fn],
                                    gol[tk][fn])
            except AssertionError:
                allok = False
                if noheader:
                    print "Term\tFilename\tGold\tSys"
                    noheader = False
                print u"{}\t{}\t{}\t{}".format(tk, fn,
                                               gol[tk][fn], stm[tk][fn])
    if allok:
        print "OK"


if __name__ == "__main__":
    goldfn = os.path.join(here, "gold.tsv")
    try:
        sysfn = sys.argv[1]
    except IndexError:
        # sysfn = "/home/pablo/projects/clm/ipcc_norm_wk/results_06032016/CSV_06032016_ttg_fn2term_lexana_39.tsv"
        sysfn = "/home/pablo/projects/clm/ipcc_norm_wk/test_results.tsv"
    gr = parse_results(goldfn)
    sr = parse_results(sysfn)
    check(gr, sr)
