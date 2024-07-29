#!/usr/bin/env bash
cd "$(dirname "$0")"
echo "Preparing template..."
xgettext --output=po/tauno-monitor.pot --files-from=po/POTFILES
echo "Updating Estonian..."
msgmerge --no-fuzzy-matching -U po/et.po po/tauno-monitor.pot
