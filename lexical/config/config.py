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
ttgpath = "/home/pablo/projects/clm/ipcc_norm_wk/results_06032016/CSV_06032016_ttg"
chosenfilespath = os.path.join(configdir, "sort_filenames.txt")
for mypath in (ttgpath, chosenfilespath):
    assert os.path.exists(mypath)


# DATA
datapath = os.path.join(os.path.join(configdir, os.pardir), "data")
datakeys = {
    "ADJ": {"fn": "adjectives.txt", "ltype": "inf", "tag": r"J.*"},
    "ADV": {"fn": "adverbs.txt", "ltype": "inf", "tag": r"[RJ].*"},
    "AGR": {"fn": "agreement.txt", "ltype": "fml", "tag": None},
    "CNF": {"fn": "confidence.txt", "ltype": "fml", "tag": None},
    "EVI": {"fn": "evidence.txt", "ltype": "fml", "tag": None},
    "LXV": {"fn": "lexverbs.txt", "ltype": "inf", "tag": r"V.*"},
    "LKL": {"fn": "likelihood.txt", "ltype": "fml", "tag": None},
    "MDL": {"fn": "modal.txt", "ltype": "inf", "tag": r"MD"},
    "PHR": {"fn": "phrases.txt", "ltype": "inf", "tag": None},
    "PRP": {"fn": "prepositions.txt", "ltype": "inf", "tag": r"IN"}
}

# apply vocab lists in this order
vocorder = ["LKL", "CNF", "EVI", "AGR", "MDL", "LXV", "ADV", "ADJ", "PRP", "PHR"]
assert (set(vocorder)) == set(datakeys)

# terms that are a substring of other terms (as full words)
dupterms = os.path.join(datapath, "substring_terms.txt")