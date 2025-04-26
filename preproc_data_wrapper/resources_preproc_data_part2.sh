#!/bin/bash -l

#SBATCH -J preproc_data
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=2
#SBATCH --cpus-per-task=1
#SBATCH --mem=2gb
#SBATCH --tmp=20gb
#SBATCH -t 10:00
#SBATCH --mail-type=ALL
#SBATCH --mail-user=lundq163@umn.edu
#SBATCH -p aglarge,agsmall,ag2tb,preempt,amdsmall,amdlarge,amd512,amd2tb
#SBATCH -o fragileX_output_logs_part2/data_preproc_%A_%a.out
#SBATCH -e fragileX_output_logs_part2/data_preproc_%A_%a.err
#SBATCH -A csandova

cd run_files_${1}.preproc_data_part2

module load singularity

file=run${SLURM_ARRAY_TASK_ID}

bash ${file}

# mesabi partitions for -p are amdsmall,amd512,amd2tb,ram256g,ram1t
