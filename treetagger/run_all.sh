#!/usr/bin/env bash

basedir="$1"
suffix="$2" # to name directories


if [ -z "$2" ]; then
  echo "Usage: $0 out_dir suffix"
  exit
fi

# outdir
odir="$1_ttg"
echo -e "== Writing to [${odir}] ==\n"

# treetagger
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

# counts and overall table
    #https://stackoverflow.com/questions/59895/
SCRDIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
COUNTER="${SCRDIR}/count_treetagger_pos.py"
AGG="${SCRDIR}/aggregate.py"
echo -e "\n\n== POS-Tag counts [${COUNTER}] ==\n"
python "$COUNTER" "$odir" "$suffix"
echo -e "\n\n== Create OVERALL TABLES [${AGG}] ==\n"
python "$AGG" "${odir}_summaries_${suffix}" "$suffix"
