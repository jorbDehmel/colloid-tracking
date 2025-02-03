#!/usr/bin/bash

echo "Script for the filtering and organiztion of KCL colloid output"
echo "Jordan Dehmel, 2023"
echo "jdehmel@outlook.com, jedehmel@mavs.coloradomesa.edu"

echo "Stage 1 / 5"

python3 ~/Programs/physicsScripts/filterer.py ~/data/kcl/kcl_1x_10-4_m/5m/5v/
python3 ~/Programs/physicsScripts/filterer.py ~/data/kcl/kcl_1x_10-4_m/5m/10v/
python3 ~/Programs/physicsScripts/filterer.py ~/data/kcl/kcl_1x_10-4_m/5m/15v/

echo "Stage 2 / 5"

python3 ~/Programs/physicsScripts/filterer.py ~/data/kcl/kcl_1x_10-4_m/10m/5v/
python3 ~/Programs/physicsScripts/filterer.py ~/data/kcl/kcl_1x_10-4_m/10m/10v/
python3 ~/Programs/physicsScripts/filterer.py ~/data/kcl/kcl_1x_10-4_m/10m/15v/

echo "Stage 3 / 5"

python3 ~/Programs/physicsScripts/filterer.py ~/data/kcl/kcl_5x_10-5_m/5m/5v/
python3 ~/Programs/physicsScripts/filterer.py ~/data/kcl/kcl_5x_10-5_m/5m/10v/
python3 ~/Programs/physicsScripts/filterer.py ~/data/kcl/kcl_5x_10-5_m/5m/15v/

echo "Stage 4 / 5"

python3 ~/Programs/physicsScripts/filterer.py ~/data/kcl/kcl_5x_10-5_m/10m/5v/
python3 ~/Programs/physicsScripts/filterer.py ~/data/kcl/kcl_5x_10-5_m/10m/10v/
python3 ~/Programs/physicsScripts/filterer.py ~/data/kcl/kcl_5x_10-5_m/10m/15v/

echo "Stage 5 / 5"

# Reorganize- The above commands just put everything in the cwd

# Ensure directory structure
rm -rf kcl

mkdir -p kcl/kcl_1x_10-4_m/5m/5v
mkdir -p kcl/kcl_1x_10-4_m/5m/10v
mkdir -p kcl/kcl_1x_10-4_m/5m/15v

mkdir -p kcl/kcl_1x_10-4_m/10m/5v
mkdir -p kcl/kcl_1x_10-4_m/10m/10v
mkdir -p kcl/kcl_1x_10-4_m/10m/15v

mkdir -p kcl/kcl_5x_10-5_m/5m/5v
mkdir -p kcl/kcl_5x_10-5_m/5m/10v
mkdir -p kcl/kcl_5x_10-5_m/5m/15v

mkdir -p kcl/kcl_5x_10-5_m/10m/5v
mkdir -p kcl/kcl_5x_10-5_m/10m/10v
mkdir -p kcl/kcl_5x_10-5_m/10m/15v

# Move everything
mv *kcl_1x_10-4_m* kcl/kcl_1x_10-4_m
mv *kcl_5x_10-5_m* kcl/kcl_5x_10-5_m

mv kcl/kcl_1x_10-4_m/*_5m* kcl/kcl_1x_10-4_m/5m
mv kcl/kcl_1x_10-4_m/*_10m* kcl/kcl_1x_10-4_m/10m

mv kcl/kcl_1x_10-4_m/5m/*_5v* kcl/kcl_1x_10-4_m/5m/5v
mv kcl/kcl_1x_10-4_m/5m/*_10v* kcl/kcl_1x_10-4_m/5m/10v
mv kcl/kcl_1x_10-4_m/5m/*_15v* kcl/kcl_1x_10-4_m/5m/15v
mv kcl/kcl_1x_10-4_m/10m/*_5v* kcl/kcl_1x_10-4_m/10m/5v
mv kcl/kcl_1x_10-4_m/10m/*_10v* kcl/kcl_1x_10-4_m/10m/10v
mv kcl/kcl_1x_10-4_m/10m/*_15v* kcl/kcl_1x_10-4_m/10m/15v

mv kcl/kcl_5x_10-5_m/*_5m* kcl/kcl_5x_10-5_m/5m
mv kcl/kcl_5x_10-5_m/*_10m* kcl/kcl_5x_10-5_m/10m

mv kcl/kcl_5x_10-5_m/5m/*_5v* kcl/kcl_5x_10-5_m/5m/5v
mv kcl/kcl_5x_10-5_m/5m/*_10v* kcl/kcl_5x_10-5_m/5m/10v
mv kcl/kcl_5x_10-5_m/5m/*_15v* kcl/kcl_5x_10-5_m/5m/15v
mv kcl/kcl_5x_10-5_m/10m/*_5v* kcl/kcl_5x_10-5_m/10m/5v
mv kcl/kcl_5x_10-5_m/10m/*_10v* kcl/kcl_5x_10-5_m/10m/10v
mv kcl/kcl_5x_10-5_m/10m/*_15v* kcl/kcl_5x_10-5_m/10m/15v
