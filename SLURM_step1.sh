#!/bin/bash
#SBATCH --time=3:00:00
#SBATCH --mem=2G
#SBATCH --output=./slurm/logs/%x-%j.log
#SBATCH --cpus-per-task=16

# Set up software environment
module load StdEnv/2020   # This is already loaded, but for future compatibility...
module load gcc/9.3.0
#module load kraken2/2.1.1
#module load bbmap/38.86
module load trimmomatic/0.39
module load blast+/2.12.0
#module load diamond/2.0.13
#module load r/4.1.2
module load python/3.9
export R_LIBS=~/.local/R/$EBVERSIONR/
source ~/env/bin/activate

# Run Snakemake
snakemake -s snakefile_step1.py --configfile configs/shotgunconfig.yaml --cores all --keep-going
