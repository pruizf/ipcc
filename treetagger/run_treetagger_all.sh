#!/usr/bin/env bash

basedir="$1"
odir="$2"

for vol in 1 2 3; do
  dn="$basedir/AR${vol}"
  echo "== Processing $dn =="
  ./run_treetagger.sh "$dn" "$odir"
done

for vol2 in 4 5; do
  for wg in I II III; do
    dn2="$basedir/AR${vol2}/AR${vol2}-WG${wg}"
    echo "== Processing $dn2 =="
    ./run_treetagger.sh "$dn2" "$odir"
  done
done