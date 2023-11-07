#!/usr/bin/fish

echo "Script for the analysis of tracks/*/ (IE ramp, sine, etc)"
echo "Jordan Dehmel, 2023"

echo "Stage 1 / 4"

~/Programs/physicsScripts/filterer.py ~/data/tracks/Ramp\ Wave/5V
~/Programs/physicsScripts/filterer.py ~/data/tracks/Ramp\ Wave/10V
~/Programs/physicsScripts/filterer.py ~/data/tracks/Ramp\ Wave/15V
~/Programs/physicsScripts/filterer.py ~/data/tracks/Ramp\ Wave/20V

echo "Stage 2 / 4"

~/Programs/physicsScripts/filterer.py ~/data/tracks/Sine\ Wave/5V
~/Programs/physicsScripts/filterer.py ~/data/tracks/Sine\ Wave/10V
~/Programs/physicsScripts/filterer.py ~/data/tracks/Sine\ Wave/15V
~/Programs/physicsScripts/filterer.py ~/data/tracks/Sine\ Wave/20V

echo "Stage 3 / 4"

~/Programs/physicsScripts/filterer.py ~/data/tracks/Square\ Wave/5V
~/Programs/physicsScripts/filterer.py ~/data/tracks/Square\ Wave/10V
~/Programs/physicsScripts/filterer.py ~/data/tracks/Square\ Wave/15V
~/Programs/physicsScripts/filterer.py ~/data/tracks/Square\ Wave/20V

echo "Stage 4 / 4 : Meta"

~/Programs/physicsScripts/legacy/tracks_meta.py