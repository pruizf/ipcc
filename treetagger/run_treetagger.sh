#!/usr/bin/env bash

indir="$1"
outdir="$2"
tagger=/home/pablo/usr/local/tree-tagger-lin/cmd/tree-tagger-english

if [ ! -d "$outdir" ]; then
  mkdir "$outdir"
fi

for fn in $(ls "$indir"); do
  echo -e "\n$fn\n"
  if [ ! -f "$indir/$fn" ]; then
    echo "- Skipping [$fn]"
    continue
  fi
  cat "$indir/$fn" | sed -e 's/</ /g' | "$tagger" > "$outdir/${fn}"
  #cat "$indir/$fn" | "$tagger" > "$outdir/${fn}"
done
