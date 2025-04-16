#!/bin/bash -l
#SBATCH -J preproc_data
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=8
#SBATCH --cpus-per-task=1
#SBATCH --mem=12gb
#SBATCH --tmp=200gb
#SBATCH -t 30:00
#SBATCH --mail-type=ALL
#SBATCH --mail-user=lundq163@umn.edu
#SBATCH -p aglarge,agsmall,ag2tb,preempt,amdsmall,amdlarge,amd512,amd2tb
#SBATCH -o output_logs/test1_%A_%a.out
#SBATCH -e output_logs/test1_%A_%a.err
#SBATCH -A csandova

cd run_files_${1}.preproc_data

module load singularity

file=run${SLURM_ARRAY_TASK_ID}

bash ${file}

# mesabi partitions for -p are amdsmall,amd512,amd2tb,ram256g,ram1t
