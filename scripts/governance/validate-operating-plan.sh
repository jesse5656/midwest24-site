#!/usr/bin/env bash
set -euo pipefail

PLAN="OPERATING-PLAN.md"

if [ ! -f "$PLAN" ]; then
  echo "ERROR: Operating Plan not found at $PLAN"
  exit 1
fi

required=(
  "# Current Objective"
  "Type:"
  "Name:"
  "Status:"
  "Objective:"
  "Scope:"
  "Success Criteria:"
  "Definition of Done:"
  "# Priority Queue"
)

for item in "${required[@]}"; do
  if ! grep -q "$item" "$PLAN"; then
    echo "ERROR: OPERATING-PLAN.md missing required section: $item"
    exit 1
  fi
done
