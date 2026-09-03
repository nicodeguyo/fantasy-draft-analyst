#!/usr/bin/env bash
# Rebuild dist/fantasy-draft-analyst.zip — the file people upload to claude.ai / the desktop app.
# The zip root must be the skill folder itself (fantasy-draft-analyst/SKILL.md), not its contents.
set -euo pipefail
cd "$(dirname "$0")/.."
rm -f dist/fantasy-draft-analyst.zip
( cd skills && zip -qr ../dist/fantasy-draft-analyst.zip fantasy-draft-analyst -x '*.pyc' -x '*/__pycache__/*' -x '*/__pycache__/' -x '*.DS_Store' )
echo "wrote dist/fantasy-draft-analyst.zip ($(du -h dist/fantasy-draft-analyst.zip | cut -f1))"
