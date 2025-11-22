#!/bin/zsh

BATCH_SIZE=10
COUNT=0
FILES_TO_ADD=()

# Find all files in ./wallpapers/ and iterate over them
find ./wallpapers/ -type f -print0 | while IFS= read -r -d '' line; do
  FILES_TO_ADD+=("$line")
  (( COUNT++ ))

  if (( COUNT % BATCH_SIZE == 0 )); then
    echo "Adding batch of $BATCH_SIZE files..."
    git add "${FILES_TO_ADD[@]}"
    git commit -m "chore: add stuff"
    git push origin main
    FILES_TO_ADD=()
  fi
done

if (( ${#FILES_TO_ADD[@]} > 0 )); then
  echo "Adding final batch of ${#FILES_TO_ADD[@]} files..."
  git add "${FILES_TO_ADD[@]}"
  git commit -m "chore: add stuff"
  git push origin main
fi
