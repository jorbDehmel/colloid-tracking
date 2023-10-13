#!/usr/bin/fish

set SCRIPT ~/Programs/physicsScripts/filterer.py
set ROOT /home/jorb/data/Glycerol\ Exports\ 7.24.23\ 6/Glycerol\ Exports\ 7.24.23

echo "Jordan Dehmel, 2023"
echo "jdehmel@outlook.com"

rm -rf scatters/* special/*

echo "Doing filtering..."

$SCRIPT $ROOT/120\ um/Bottom\ Up/16\ V/9240umexports &
$SCRIPT $ROOT/120\ um/Bottom\ Up/16\ V/9290umexports &
$SCRIPT $ROOT/120\ um/Bottom\ Up/16\ V/9340umexports &
$SCRIPT $ROOT/120\ um/Bottom\ Up/16\ V/9265umexports &
$SCRIPT $ROOT/120\ um/Bottom\ Up/16\ V/9315umexports &
wait

$SCRIPT $ROOT/120\ um/Top\ Down/16\ V/8960umexports &
$SCRIPT $ROOT/120\ um/Top\ Down/16\ V/8985umexports &
$SCRIPT $ROOT/120\ um/Top\ Down/16\ V/9010umexports &
$SCRIPT $ROOT/120\ um/Top\ Down/16\ V/9035umexports &
$SCRIPT $ROOT/120\ um/Top\ Down/16\ V/9060umexports &
wait

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
