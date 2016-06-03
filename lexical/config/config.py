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
ttgpath = ""

chosenfilespath = os.path.join(configdir, "sort_filenames.txt")

# DATA
datapath = os.path.join(os.path.join(configdir, os.pardir), "data")
datakeys = {
    "ADJ": {"fn": "adjectives.txt", "tag": "J.*", "runon": "ttg"},
    "ADV": {"fn": "adverbs.txt", "tag": "R.*",  "runon": "ttg"},
    "AGR": {"fn": "agreement.txt", "tag": None, "runon": "txt"},
    "CNF": {"fn": "confidence.txt", "tag": None, "runon": "txt"},
    "EVI": {"fn": "evidence.txt", "tag": None, "runon": "txt"},
    "LXV": {"fn": "lexverbs.txt", "tag": "V.*", "runon": "ttg"},
    "LKL": {"fn": "likelihood.txt", "tag": None, "runon": "txt"},
    "MDL": {"fn": "modal.txt", "tag": "MD", "runon": "ttg"},
    "PHR": {"fn": "phrases.txt", "tag": None, "runon": "txt"},
    "PRP": {"fn": "prepositions.txt", "tag": "J.*", "runon": "ttg"}
}

