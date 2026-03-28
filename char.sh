#!/bin/bash

# Recursively find all .html files and replace &aring; with å
find . -type f -name "*.html" -print0 | while IFS= read -r -d '' file; do
    echo "Processing $file"
    # Use sed to do the replacement in-place
    # sed -i 's/&aring;/å/g' "$file"
    tidy -mi -w 90 "$file"
done
