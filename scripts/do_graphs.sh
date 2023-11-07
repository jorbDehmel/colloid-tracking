#!/bin/fish

mkdir -p ~/data_graphs

~/Programs/physicsScripts/filterer.py /run/media/jorb/Music/data/KCL\ Final/KCL\ 1\ X\ 10-4\ M/5\ Micron/5\ V/Analysis\ 1/
~/Programs/physicsScripts/filterer.py /run/media/jorb/Music/data/KCL\ Final/KCL\ 1\ X\ 10-4\ M/5\ Micron/10\ V/Analysis\ 1/
~/Programs/physicsScripts/filterer.py /run/media/jorb/Music/data/KCL\ Final/KCL\ 1\ X\ 10-4\ M/5\ Micron/15\ V/Analysis\ 1/

echo 'Stage 1 / 5 done.'

~/Programs/physicsScripts/filterer.py /run/media/jorb/Music/data/KCL\ Final/KCL\ 1\ X\ 10-4\ M/10\ Microns/5\ V/Analysis\ 1/
~/Programs/physicsScripts/filterer.py /run/media/jorb/Music/data/KCL\ Final/KCL\ 1\ X\ 10-4\ M/10\ Microns/10\ V/Analyse/
~/Programs/physicsScripts/filterer.py /run/media/jorb/Music/data/KCL\ Final/KCL\ 1\ X\ 10-4\ M/10\ Microns/15\ V/Analyse/

echo 'Stage 2 / 5 done.'

~/Programs/physicsScripts/filterer.py /run/media/jorb/Music/data/KCL\ Final/KCL\ 5\ X\ 10-5\ M/5\ Micron/5\ V/Analysis/
~/Programs/physicsScripts/filterer.py /run/media/jorb/Music/data/KCL\ Final/KCL\ 5\ X\ 10-5\ M/5\ Micron/10\ V/Analysis/
~/Programs/physicsScripts/filterer.py /run/media/jorb/Music/data/KCL\ Final/KCL\ 5\ X\ 10-5\ M/5\ Micron/15\ V/Analysis/

echo 'Stage 3 / 5 done.'

~/Programs/physicsScripts/filterer.py /run/media/jorb/Music/data/KCL\ Final/KCL\ 5\ X\ 10-5\ M/10\ Microns/10\ Microns\ 5\ X\ 10-5/5\ V/Analysis/
~/Programs/physicsScripts/filterer.py /run/media/jorb/Music/data/KCL\ Final/KCL\ 5\ X\ 10-5\ M/10\ Microns/10\ Microns\ 5\ X\ 10-5/10\ V/Analysis/
~/Programs/physicsScripts/filterer.py /run/media/jorb/Music/data/KCL\ Final/KCL\ 5\ X\ 10-5\ M/10\ Microns/10\ Microns\ 5\ X\ 10-5/15\ V/Analysis/

echo 'Stage 4 / 5 done.'

~/Programs/physicsScripts/legacy/meta.py
~/Programs/physicsScripts/legacy/meta_2.py

echo 'Stage 5 / 5 done.'
