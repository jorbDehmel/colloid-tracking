#!/usr/bin/bash

# Does meta-analysis and filtering on the manually cleaned 240um
# data from Sandeep

# Start from ~/data/240um/
# The data we want is in .xlsx files
# We can convert these to .csv via `libreoffice --headless --convert-to csv ./*.xlsx`
# Then, we find these and move them to the correct location

# DIR=~/data/240um/

# Turn to .csv files
# for f in $DIR/*/* ; do cd "$f" && libreoffice --headless --convert-to csv ./*.xlsx ; done

# Move to proper place
# for f in $DIR/*/* ; do cd "$f" && result=${PWD##*/} && echo $result && cp filt*csv "../filtered_$result.csv" ; done

# THEN, we can run the filtering and meta scripts

DIR="/home/jorb/data/240um_clean"
COM="python3 /home/jorb/Programs/physicsScripts/filterer.py"

echo "Processing files..."

echo "1/7"
$COM $DIR/bot

echo "2/7"
$COM $DIR/bot+25

echo "3/7"
$COM $DIR/bot+50

echo "4/7"
$COM $DIR/bot+70

echo "5/7"
$COM $DIR/bot+100

echo "6/7"
$COM $DIR/bot+190

echo "7/7"
$COM $DIR/bot+210

echo "Done with filtering."

echo "Making unified graphs..."
python3 /home/jorb/Programs/physicsScripts/comparisons.py '240um'
