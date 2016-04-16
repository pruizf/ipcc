#!/usr/bin/env bash

basedir="$1"
odir="$2"

for vol in 1 2; do
  dn="$basedir/AR${vol}"
  echo "== Processing $dn =="
  ./run_treetagger.sh "$dn" "$odir"
done

for vol2 in 3 4 5; do
  for wg in 1 2 3 SYR ; do
    # SYR has its own dir name convention
    if [ "$wg" = SYR ]; then
      dn2="$basedir/AR${vol2}/AR${vol2}_SYR"
      [ ! -d "$dn2" ] && dn2="$basedir/AR${vol2}/AR${vol2}-SYR"
    # dir names sometimes dash sometimes underscore
    else
      dn2="$basedir/AR${vol2}/AR${vol2}_WG${wg}"
      [ ! -d "$dn2" ] && dn2="$basedir/AR${vol2}/AR${vol2}-WG${wg}"
    fi
    if [ ! -d "$dn2" ];then
      echo "###Directory does not exist ${dn2}"
      else
        ./run_treetagger.sh "$dn2" "$odir"
    fi
  done
done