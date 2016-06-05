"""Config for lexical extraction based on GSB's data"""

__author__ = 'Pablo Ruiz'
__date__ = '03/06/16'
__email__ = 'pabloruizfabo@gmail.com'


import inspect
import os
import sys


configdir = os.path.dirname(os.path.abspath(
    inspect.getfile(inspect.currentframe())))
sys.path.append(configdir)


# CORPUS
corpuspath = "/home/pablo/projects/clm/ipcc_norm_wk/CSV_06032016"
ttgpath = "/home/pablo/projects/clm/ipcc_norm_wk/results_06032016/CSV_06032016_ttg"
# chosen files as is in ttgpath, but need to find recursively under corpuspath
chosenfilespath = os.path.join(configdir, "sort_filenames.txt")
for mypath in (corpuspath, ttgpath, chosenfilespath):
    assert os.path.exists(mypath)


# DATA
datapath = os.path.join(os.path.join(configdir, os.pardir), "data")
datakeys = {
    "ADJ": {"fn": "adjectives.txt", "ltype": "inf", "tag": "J.*", "runon": "ttg"},
    "ADV": {"fn": "adverbs.txt", "ltype": "inf", "tag": "R.*",  "runon": "ttg"},
    "AGR": {"fn": "agreement.txt", "ltype": "fml", "tag": None, "runon": "txt"},
    "CNF": {"fn": "confidence.txt", "ltype": "fml", "tag": None, "runon": "txt"},
    "EVI": {"fn": "evidence.txt", "ltype": "fml", "tag": None, "runon": "txt"},
    "LXV": {"fn": "lexverbs.txt", "ltype": "inf", "tag": "V.*", "runon": "ttg"},
    "LKL": {"fn": "likelihood.txt", "ltype": "fml", "tag": None, "runon": "txt"},
    "MDL": {"fn": "modal.txt", "ltype": "inf", "tag": "MD", "runon": "ttg"},
    "PHR": {"fn": "phrases.txt", "ltype": "inf", "tag": None, "runon": "txt"},
    "PRP": {"fn": "prepositions.txt", "ltype": "inf", "tag": "IN", "runon": "ttg"}
}

for ke in datakeys:
    assert not (datakeys[ke]["tag"] is not None and
                datakeys[ke]["runon"] != "ttg")

# apply vocab lists in this order
vocorder = ["LKL", "CNF", "EVI", "AGR", "MDL", "LXV", "ADV", "ADJ", "PRP", "PHR"]
assert (set(vocorder)) == set(datakeys)

# terms that are a substring of other terms (as full words)
dupterms = os.path.join(datapath, "substring_terms.txt")