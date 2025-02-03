#!/bin/fish

# Writen for POSIX systems (not Windows)
# Uses Fish (Friendly Interactive Shell) instead of Bash,
# so make sure that's installed.
# Debian: sudo apt-get install fish
# Arch: sudo pacman -S fish

# Multithreading is hardcoded into this
# Runs ~2 threads at a time

set SCRIPT ~/Programs/physicsScripts/filterer.py
set ROOT /home/jorb/data/Glycerol\ Exports\ 7.24.23\ 6/Glycerol\ Exports\ 7.24.23

echo "Glycerol Density-Matching Analysis Script"
echo "Jordan Dehmel, 2023"
echo "jdehmel@outlook.com"

rm -rf scatters/*

date

echo "Processing 120 um Data..."
echo "Processing Bottom Up Data..."

$SCRIPT $ROOT/120\ um/Bottom\ Up/8\ V/8V\ 8940 &
$SCRIPT $ROOT/120\ um/Bottom\ Up/8\ V/8V\ 8965 &
wait
$SCRIPT $ROOT/120\ um/Bottom\ Up/8\ V/8V\ 8990 &
$SCRIPT $ROOT/120\ um/Bottom\ Up/8\ V/8V\ 9015 &
wait
$SCRIPT $ROOT/120\ um/Bottom\ Up/8\ V/8V\ 9040 

$SCRIPT $ROOT/120\ um/Bottom\ Up/12\ V/8980botumexports &
$SCRIPT $ROOT/120\ um/Bottom\ Up/12\ V/8985umexports &
wait
$SCRIPT $ROOT/120\ um/Bottom\ Up/12\ V/9010umexports &
$SCRIPT $ROOT/120\ um/Bottom\ Up/12\ V/9035umexports &
wait
$SCRIPT $ROOT/120\ um/Bottom\ Up/12\ V/9080topumexports

$SCRIPT $ROOT/120\ um/Bottom\ Up/16\ V/9240umexports &
$SCRIPT $ROOT/120\ um/Bottom\ Up/16\ V/9290umexports &
wait
$SCRIPT $ROOT/120\ um/Bottom\ Up/16\ V/9340umexports &
$SCRIPT $ROOT/120\ um/Bottom\ Up/16\ V/9265umexports &
wait
$SCRIPT $ROOT/120\ um/Bottom\ Up/16\ V/9315umexports 

$SCRIPT $ROOT/120\ um/Bottom\ Up/20\ V/20V\ 9180 &
$SCRIPT $ROOT/120\ um/Bottom\ Up/20\ V/20V\ 9205\ exports &
wait
$SCRIPT $ROOT/120\ um/Bottom\ Up/20\ V/20V\ 9230\ exports &
$SCRIPT $ROOT/120\ um/Bottom\ Up/20\ V/20V\ 9255\ exports &
wait
$SCRIPT $ROOT/120\ um/Bottom\ Up/20\ V/20V\ 9280\ exports 

echo "Processing Top Down Data..."

$SCRIPT $ROOT/120\ um/Top\ Down/8\ V/top\ exports &
$SCRIPT $ROOT/120\ um/Top\ Down/8\ V/top-25\ exports &
wait
$SCRIPT $ROOT/120\ um/Top\ Down/8\ V/top-50\ exports &
$SCRIPT $ROOT/120\ um/Top\ Down/8\ V/top-75\ exports &
wait
$SCRIPT $ROOT/120\ um/Top\ Down/8\ V/top-100\ exports 

$SCRIPT $ROOT/120\ um/Top\ Down/16\ V/8960umexports &
$SCRIPT $ROOT/120\ um/Top\ Down/16\ V/8985umexports &
wait
$SCRIPT $ROOT/120\ um/Top\ Down/16\ V/9010umexports &
$SCRIPT $ROOT/120\ um/Top\ Down/16\ V/9035umexports &
wait
$SCRIPT $ROOT/120\ um/Top\ Down/16\ V/9060umexports 

$SCRIPT $ROOT/120\ um/Top\ Down/20\ V/top\ exports &
$SCRIPT $ROOT/120\ um/Top\ Down/20\ V/top-25\ exports &
wait
$SCRIPT $ROOT/120\ um/Top\ Down/20\ V/top-50\ exports &
$SCRIPT $ROOT/120\ um/Top\ Down/20\ V/top-75\ exports &
wait
$SCRIPT $ROOT/120\ um/Top\ Down/20\ V/top-100\ exports 

echo "Processing 240 um Data..."

echo "Processing Bottom Up Data..."

$SCRIPT $ROOT/240\ um/Bottom\ Up\ 16\ V/9090um\ exports &
$SCRIPT $ROOT/240\ um/Bottom\ Up\ 16\ V/9140um\ exports &
wait
$SCRIPT $ROOT/240\ um/Bottom\ Up\ 16\ V/9255um\ exports &
$SCRIPT $ROOT/240\ um/Bottom\ Up\ 16\ V/9305um\ exports &
wait
$SCRIPT $ROOT/240\ um/Bottom\ Up\ 16\ V/9115um\ exports &
$SCRIPT $ROOT/240\ um/Bottom\ Up\ 16\ V/9197um\ exports &
wait
$SCRIPT $ROOT/240\ um/Bottom\ Up\ 16\ V/9280um\ exports 

echo "Processing Top Down Data..."

$SCRIPT $ROOT/240\ um/Top\ Down\ 16\ V/bot\ exports &
$SCRIPT $ROOT/240\ um/Top\ Down\ 16\ V/bot+25\ exports &
wait
$SCRIPT $ROOT/240\ um/Top\ Down\ 16\ V/bot+50\ exports &
$SCRIPT $ROOT/240\ um/Top\ Down\ 16\ V/top-97\ exports &
wait
$SCRIPT $ROOT/240\ um/Top\ Down\ 16\ V/top-50\ exports &
$SCRIPT $ROOT/240\ um/Top\ Down\ 16\ V/top-25\ exports &
wait
$SCRIPT $ROOT/240\ um/Top\ Down\ 16\ V/top\ exports 

echo "Transferring scatterplots for 120um 16V data"

mkdir -p special/top_down/0khz
mkdir -p special/top_down/1khz
mkdir -p special/top_down/100khz

mkdir -p special/bottom_up/0khz
mkdir -p special/bottom_up/1khz
mkdir -p special/bottom_up/100khz

ls scatters | grep 120 | grep 16 | grep "Top" | grep _0khz > matches.txt
for name in $(cat matches.txt); cp scatters/$name special/top_down/0khz ; end
ls scatters | grep 120 | grep 16 | grep "Top"  | grep 1khz > matches.txt
for name in $(cat matches.txt); cp scatters/$name special/top_down/1khz ; end
ls scatters | grep 120 | grep 16 | grep "Top"  | grep 100khz > matches.txt
for name in $(cat matches.txt); cp scatters/$name special/top_down/100khz ; end

ls scatters | grep 120 | grep 16 | grep "Bottom" | grep _0khz > matches.txt
for name in $(cat matches.txt); cp scatters/$name special/bottom_up/0khz ; end
ls scatters | grep 120 | grep 16 | grep "Bottom"  | grep 1khz > matches.txt
for name in $(cat matches.txt); cp scatters/$name special/bottom_up/1khz ; end
ls scatters | grep 120 | grep 16 | grep "Bottom"  | grep 100khz > matches.txt
for name in $(cat matches.txt); cp scatters/$name special/bottom_up/100khz ; end

rm matches.txt

echo "Done with layer 1 analysis."
echo "Doing meta analysis..."

~/Programs/physicsScripts/legacy/meta_glycerol.py

echo "Done."

date
