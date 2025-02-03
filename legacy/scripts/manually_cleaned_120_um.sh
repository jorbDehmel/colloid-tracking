#!/bin/bash

# Does meta-analysis and filtering on the manually cleaned 120um
# data from Sandeep

DIR="/home/jorb/data/120um_clean"
COM="python3 /home/jorb/Programs/physicsScripts/filterer.py"

echo "Processing 8v files..."

$COM $DIR/8v/bot
$COM $DIR/8v/bot+25
$COM $DIR/8v/bot+50
$COM $DIR/8v/bot+75
$COM $DIR/8v/bot+100

echo "Processing 12v files..."

$COM $DIR/12v/bot
$COM $DIR/12v/bot+25
$COM $DIR/12v/bot+50
$COM $DIR/12v/bot+75
$COM $DIR/12v/bot+100

echo "Processing 16v files..."

$COM $DIR/16v/bot
$COM $DIR/16v/bot+25
$COM $DIR/16v/bot+50
$COM $DIR/16v/bot+75
$COM $DIR/16v/bot+100

echo "Done with filtering."

echo "Making unified graphs..."
python3 /home/jorb/Programs/physicsScripts/comparisons.py '120um'
