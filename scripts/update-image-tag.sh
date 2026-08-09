#!/usr/bin/env bash
set -euo pipefail

if [[ $# -ne 2 ]]; then
  echo "Usage: $0 <values-file> <image-tag>"
  exit 1
fi

VALUES_FILE="$1"
IMAGE_TAG="$2"

if [[ ! -f "$VALUES_FILE" ]]; then
  echo "Values file not found: $VALUES_FILE"
  exit 1
fi

python3 - "$VALUES_FILE" "$IMAGE_TAG" <<'PY'
from pathlib import Path
import re
import sys

values_file = Path(sys.argv[1])
image_tag = sys.argv[2]

content = values_file.read_text(encoding="utf-8")

pattern = r'(^image:\s*\n(?:^[ \t]+.*\n)*?^[ \t]+tag:\s*)[^\n]+'
replacement = rf'\g<1>{image_tag}'

updated, count = re.subn(
    pattern,
    replacement,
    content,
    count=1,
    flags=re.MULTILINE,
)

if count != 1:
    raise SystemExit("Could not update image.tag in values file")

values_file.write_text(updated, encoding="utf-8")
print(f"Updated {values_file} image.tag to {image_tag}")
PY