#!/usr/bin/env bash
# Quick force push script
git add -A
git commit -m "Quick commit $(date '+%Y-%m-%d %H:%M:%S')" --no-verify
git push --force-with-lease
