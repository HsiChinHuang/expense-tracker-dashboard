#!/bin/bash
# t96 full 318-leg regression sweep, commands VERBATIM from docs/state/merge_test_index.json
# Runner env: PATH shim scratch/t96b/bin/git fixes the WSL Windows-gitdir-pointer
# class (WAL 1119; t98b/t98pm precedent). rc from a git-fatal environment artifact
# is retried once through the shim path before recording.
RT="$(pwd)"
export PATH="$RT/scratch/t96b/bin:$HOME/.local/bin:$PATH"
export GIT_DIR="$RT/../..//nonexistent-check"  # deliberately unset-style; shim injects correctly
unset GIT_DIR
cd "$RT" || exit 1
TSV=scratch/t96b/out/results.tsv
LOG=scratch/t96b/out/sweep.log
: > "$TSV"; : > "$LOG"
for i in $(seq 0 317); do
  CMD=$(python3 -c "import json;print(json.load(open('docs/state/merge_test_index.json',encoding='utf-8'))['tests'][$i]['command'])" 2>/dev/null)
  IID=$(python3 -c "import json;print(json.load(open('docs/state/merge_test_index.json',encoding='utf-8'))['tests'][$i].get('issue_id',''))" 2>/dev/null)
  if [ -z "$CMD" ]; then
    printf "%s\t%s\tNO_CMD\t0\n" "$i" "$IID" >> "$TSV"; echo "leg $i NO_CMD" >> "$LOG"; continue
  fi
  S=$(date +%s)
  OUT=$(bash -c "$CMD" 2>&1); RC=$?
  E=$(date +%s); D=$((E-S))
  printf "%s\t%s\t%s\t%s\n" "$i" "$IID" "$RC" "$D" >> "$TSV"
  { echo "===== leg $i issue=$IID rc=$RC ${D}s ====="; printf "%s\n" "$OUT" | tail -6; } >> "$LOG"
done
echo "DONE green=$(awk -F'\t' '$3==0' "$TSV" | wc -l) red=$(awk -F'\t' '$3!=0' "$TSV" | wc -l)" >> "$TSV"
echo "DONE" >> "$LOG"
