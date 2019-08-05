#!/bin/bash -l

#SBATCH -q regular
#SBATCH -N 8
#SBATCH --constraint=knl
#SBATCH --time=16:00:00
#SBATCH --job-name="run2.1i_prod201907"
#SBATCH --mail-user="avillarreal@anl.gov"
#SBATCH --mail-type=ALL

echo TEST: inside sbatch script
echo TEST: submit hostname: $(hostname)

cd /global/u2/d/descim 
source /global/u2/d/descim/load_parsl_env.sh

echo TEST: submitting driver: which python: $(which python)
srun -N 1 python /global/homes/d/descim/ALCF_1.2i/parsl-driver.py

echo TEST: driver submitted
