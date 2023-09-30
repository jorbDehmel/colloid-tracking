#!/bin/fish

# Writen for POSIX systems (not Windows)

set SCRIPT ~/Programs/physicsScripts/filterer.py
set ROOT /home/jorb/data/Glycerol\ Exports\ 7.24.23\ 6/Glycerol\ Exports\ 7.24.23

# The naming schemes here are especially bad

date

echo "Processing 120 um Data..."
echo "Processing Bottom Up Data..."

$SCRIPT $ROOT/120\ um/Bottom\ Up/8\ V/8V\ 8940 &
$SCRIPT $ROOT/120\ um/Bottom\ Up/8\ V/8V\ 8965 &
$SCRIPT $ROOT/120\ um/Bottom\ Up/8\ V/8V\ 8990 &
$SCRIPT $ROOT/120\ um/Bottom\ Up/8\ V/8V\ 9015 &
$SCRIPT $ROOT/120\ um/Bottom\ Up/8\ V/8V\ 9040 &
wait

$SCRIPT $ROOT/120\ um/Bottom\ Up/12\ V/8980botumexports &
$SCRIPT $ROOT/120\ um/Bottom\ Up/12\ V/8985umexports &
$SCRIPT $ROOT/120\ um/Bottom\ Up/12\ V/9010umexports &
$SCRIPT $ROOT/120\ um/Bottom\ Up/12\ V/9035umexports &
$SCRIPT $ROOT/120\ um/Bottom\ Up/12\ V/9080topumexports &
wait

$SCRIPT $ROOT/120\ um/Bottom\ Up/16\ V/9240umexports &
$SCRIPT $ROOT/120\ um/Bottom\ Up/16\ V/9290umexports &
$SCRIPT $ROOT/120\ um/Bottom\ Up/16\ V/9340umexports &
$SCRIPT $ROOT/120\ um/Bottom\ Up/16\ V/9265umexports &
$SCRIPT $ROOT/120\ um/Bottom\ Up/16\ V/9315umexports &
wait

$SCRIPT $ROOT/120\ um/Bottom\ Up/20\ V/20V\ 9180 &
$SCRIPT $ROOT/120\ um/Bottom\ Up/20\ V/20V\ 9205\ exports &
$SCRIPT $ROOT/120\ um/Bottom\ Up/20\ V/20V\ 9230\ exports &
$SCRIPT $ROOT/120\ um/Bottom\ Up/20\ V/20V\ 9255\ exports &
$SCRIPT $ROOT/120\ um/Bottom\ Up/20\ V/20V\ 9280\ exports &
wait

echo "Processing Top Down Data..."

$SCRIPT $ROOT/120\ um/Top\ Down/8\ V/top\ exports &
$SCRIPT $ROOT/120\ um/Top\ Down/8\ V/top-25\ exports &
$SCRIPT $ROOT/120\ um/Top\ Down/8\ V/top-50\ exports &
$SCRIPT $ROOT/120\ um/Top\ Down/8\ V/top-75\ exports &
$SCRIPT $ROOT/120\ um/Top\ Down/8\ V/top-100\ exports &
wait

$SCRIPT $ROOT/120\ um/Top\ Down/16\ V/8960umexports &
$SCRIPT $ROOT/120\ um/Top\ Down/16\ V/8985umexports &
$SCRIPT $ROOT/120\ um/Top\ Down/16\ V/9010umexports &
$SCRIPT $ROOT/120\ um/Top\ Down/16\ V/9035umexports &
$SCRIPT $ROOT/120\ um/Top\ Down/16\ V/9060umexports &
wait

$SCRIPT $ROOT/120\ um/Top\ Down/20\ V/top\ exports &
$SCRIPT $ROOT/120\ um/Top\ Down/20\ V/top-25\ exports &
$SCRIPT $ROOT/120\ um/Top\ Down/20\ V/top-50\ exports &
$SCRIPT $ROOT/120\ um/Top\ Down/20\ V/top-75\ exports &
$SCRIPT $ROOT/120\ um/Top\ Down/20\ V/top-100\ exports &
wait

echo "Processing 240 um Data..."

echo "Processing Bottom Up Data..."

$SCRIPT $ROOT/240\ um/Bottom\ Up\ 16\ V/9090um\ exports &
$SCRIPT $ROOT/240\ um/Bottom\ Up\ 16\ V/9140um\ exports &
$SCRIPT $ROOT/240\ um/Bottom\ Up\ 16\ V/9255um\ exports &
$SCRIPT $ROOT/240\ um/Bottom\ Up\ 16\ V/9305um\ exports &
$SCRIPT $ROOT/240\ um/Bottom\ Up\ 16\ V/9115um\ exports &
$SCRIPT $ROOT/240\ um/Bottom\ Up\ 16\ V/9197um\ exports &
$SCRIPT $ROOT/240\ um/Bottom\ Up\ 16\ V/9280um\ exports &
wait

echo "Processing Top Down Data..."

$SCRIPT $ROOT/240\ um/Top\ Down\ 16\ V/bot\ exports &
$SCRIPT $ROOT/240\ um/Top\ Down\ 16\ V/bot+25\ exports &
$SCRIPT $ROOT/240\ um/Top\ Down\ 16\ V/bot+50\ exports &
$SCRIPT $ROOT/240\ um/Top\ Down\ 16\ V/top-97\ exports &
$SCRIPT $ROOT/240\ um/Top\ Down\ 16\ V/top-50\ exports &
$SCRIPT $ROOT/240\ um/Top\ Down\ 16\ V/top-25\ exports &
$SCRIPT $ROOT/240\ um/Top\ Down\ 16\ V/top\ exports &
wait

echo "Done with layer 1 analysis."
echo "Doing meta analysis..."

~/Programs/physicsScripts/meta_glycerol.py

echo "Done."

date
