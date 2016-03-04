#!/usr/bin/env bash

outdir="$1"
fmt="$2"

basedir="/home/pablo/projects/clm/ipcc_norm_wk/CSV"
tagger="/home/pablo/projects/clm/ipcc_norm/csv2pos_pycorenlp.py"


for vol in 1 2 3; do
  for wg in 1 2 3; do
    for dtype in Rap SPM TS; do
      fn="$basedir/AR${vol}/AR${vol}_WG${wg}_${dtype}.csv"
      if [ ! -f "$fn" ]; then
        echo "- Skipping $fn"
        continue
      fi
      echo "- Processing $fn"
      python "$tagger" "$fn" "$outdir" "$fmt"
    done
  done
done
