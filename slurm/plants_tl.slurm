#!/bin/bash

#SBATCH --job-name=plantas-tl
#SBATCH --partition=general
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=2
#SBATCH --time=3:00:00

# No usamos module load gcc
source ~/miniconda3/bin/activate ambiente_ch

python leafs_plants.py
