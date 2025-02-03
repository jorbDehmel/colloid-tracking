#!/usr/bin/fish

echo "Script for the analysis of tracks (waveforms) (IE ramp, sine, etc)"
echo "Jordan Dehmel, 2023"

echo "Stage 1 / 4"

python3 ~/Programs/physicsScripts/filterer.py ~/data/tracks\ \(waveforms\)/Ramp\ Wave/5V
python3 ~/Programs/physicsScripts/filterer.py ~/data/tracks\ \(waveforms\)/Ramp\ Wave/10V
python3 ~/Programs/physicsScripts/filterer.py ~/data/tracks\ \(waveforms\)/Ramp\ Wave/15V
python3 ~/Programs/physicsScripts/filterer.py ~/data/tracks\ \(waveforms\)/Ramp\ Wave/20V

echo "Stage 2 / 4"

python3 ~/Programs/physicsScripts/filterer.py ~/data/tracks\ \(waveforms\)/Sine\ Wave/5V
python3 ~/Programs/physicsScripts/filterer.py ~/data/tracks\ \(waveforms\)/Sine\ Wave/10V
python3 ~/Programs/physicsScripts/filterer.py ~/data/tracks\ \(waveforms\)/Sine\ Wave/15V
python3 ~/Programs/physicsScripts/filterer.py ~/data/tracks\ \(waveforms\)/Sine\ Wave/20V

echo "Stage 3 / 4"

python3 ~/Programs/physicsScripts/filterer.py ~/data/tracks\ \(waveforms\)/Square\ Wave/5V
python3 ~/Programs/physicsScripts/filterer.py ~/data/tracks\ \(waveforms\)/Square\ Wave/10V
python3 ~/Programs/physicsScripts/filterer.py ~/data/tracks\ \(waveforms\)/Square\ Wave/15V
python3 ~/Programs/physicsScripts/filterer.py ~/data/tracks\ \(waveforms\)/Square\ Wave/20V

echo "Stage 4 / 4: Reorganization"

rm -rf waveforms

mkdir -p waveforms/ramp/5v
mkdir -p waveforms/ramp/10v
mkdir -p waveforms/ramp/15v
mkdir -p waveforms/ramp/20v

mkdir -p waveforms/sine/5v
mkdir -p waveforms/sine/10v
mkdir -p waveforms/sine/15v
mkdir -p waveforms/sine/20v

mkdir -p waveforms/square/5v
mkdir -p waveforms/square/10v
mkdir -p waveforms/square/15v
mkdir -p waveforms/square/20v

mv *Ramp* waveforms/ramp
mv *Sine* waveforms/sine
mv *Square* waveforms/square

mv waveforms/ramp/*20V* waveforms/ramp/20v
mv waveforms/ramp/*15V* waveforms/ramp/15v
mv waveforms/ramp/*10V* waveforms/ramp/10v
mv waveforms/ramp/*5V* waveforms/ramp/5v

mv waveforms/sine/*20V* waveforms/sine/20v
mv waveforms/sine/*15V* waveforms/sine/15v
mv waveforms/sine/*10V* waveforms/sine/10v
mv waveforms/sine/*5V* waveforms/sine/5v

mv waveforms/square/*20V* waveforms/square/20v
mv waveforms/square/*15V* waveforms/square/15v
mv waveforms/square/*10V* waveforms/square/10v
mv waveforms/square/*5V* waveforms/square/5v