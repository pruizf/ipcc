#!/usr/bin/env bash

#./run_treetagger.sh
# /home/pablo/projects/clm/ipcc_norm_wk/CSV_orig/AR5/AR5-WGIII
# /home/pablo/projects/clm/ipcc_norm_wk/out_treetagger_orig/

basedir="$1"
odir="$2"

#for vol in 1 2 3; do
#  dn="$basedir/AR${vol}"
#  echo "== Processing $dn =="
#  ./run_treetagger.sh "$dn" "$odir"
#done

for vol in 4 5; do
  for wg in I II III; do
    dn="$basedir/AR${vol}/AR${vol}-WG${wg}"
    echo "== Processing $dn =="
    ./run_treetagger.sh "$dn" "$odir"
  done
done