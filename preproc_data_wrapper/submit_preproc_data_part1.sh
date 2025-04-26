#!/bin/bash -l

array=$1
dataset=$2

if [ -z "$array" ]

then
      echo ""
      echo "No job array specified! Please enter jobs to run as argument:"
      echo ""
      echo "    EXAMPLE 1:  submit_ALL.sh 0-99"
      echo "    EXAMPLE 2:  submit_ALL.sh 1-3,6,9"
      echo ""

else
      echo ""
      echo "Submitting the following jobs for move_subjects processing now: $array"
      echo ""

      preproc=$(sbatch --parsable -a ${array} resources_preproc_data_part1.sh ${dataset})

      echo "data preproc JOB ID: $preproc"

      echo ""
      echo "Output logs will appear in output_logs folder. Use 'squeue -al --me' to monitor jobs."
      echo ""
fi

