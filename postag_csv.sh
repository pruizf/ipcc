#!/usr/bin/env bash

outdir="$1"
fmt="$2"

basedir="/home/pablo/projects/clm/ipcc_norm_wk/CSV"
tagger="/home/pablo/projects/clm/ipcc_norm/csv2pos_pycorenlp.py"


for vol in 4 5; do
  for wg in I II III; do
     fn="$basedir/AR${vol}/AR${vol}-WG${wg}/AR${vol}-WG${wg}.csv"
     if [ ! -f "$fn" ]; then
       echo "- Skipping $fn"
       continue
     fi
     echo "- Processing $fn"
     python "$tagger" "$fn" "$outdir" "$fmt"
  done
done
