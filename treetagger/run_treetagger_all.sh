#!/usr/bin/env bash

basedir="$1"
odir="$2"

for vol in 1 2 3; do
  dn="$basedir/AR${vol}"
  echo "== Processing $dn =="
  ./run_treetagger.sh "$dn" "$odir"
done

for vol in 4 5; do
  for wg in I II III; do
    dn="$basedir/AR${vol}/AR${vol}-WG${wg}"
    echo "== Processing $dn =="
    ./run_treetagger.sh "$dn" "$odir"
  done
done