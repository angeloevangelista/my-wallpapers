#!/bin/zsh


# find ./wallpapers/ -type f -print0 | xargs -0 realpath > out
FILE="out"
BATCH_SIZE=50
COUNT=0
FILES_TO_ADD=()

while IFS= read -r line || [[ -n "$line" ]]; do
  FILES_TO_ADD+=("$line")
  (( COUNT++ ))

  if (( COUNT % BATCH_SIZE == 0 )); then
    echo "Adding batch of $BATCH_SIZE files..."
    git add "${FILES_TO_ADD[@]}"
    git commit -m "chore: add stuff"
    git push origin main
    FILES_TO_ADD=() # Reset batch
  fi
done < "$FILE"

if (( ${#FILES_TO_ADD[@]} > 0 )); then
  echo "Adding final batch of ${#FILES_TO_ADD[@]} files..."
  git add "${FILES_TO_ADD[@]}"
  git commit -m "chore: add stuff"
  git push origin main
fi
