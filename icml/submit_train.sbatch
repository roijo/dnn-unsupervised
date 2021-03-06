#!/bin/bash

#SBATCH
#SBATCH --mail-type=end
#SBATCH --mail-user=ali39@jhu.edu
#SBATCH --output=_out/%A.out 
#SBATCH --error=_out/%A.err
#SBATCH -p gpu # or -p parallel
#SBATCH --gres=gpu:1
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=6

# Author: Adam Li (ali39@jhu.edu).
# Created on 2017-10-31. 
#---------------------------------------------------------------------
# SLURM job script to run serial Python
# on TNG Cluster
#---------------------------------------------------------------------
############################# LOAD IN MODULES AND UNLOAD #############
module unload git
ml anaconda-python/3.6
ml python/3.6.0
ml cuda/9.0
ml singularity 

source activate dnn

# cd /scratch/groups/ssarma2/dnn-unsupervised/
# mkdir -p /scratch/users/$USER/dnn-unsupervised
cd /scratch/users/$USER/dnn-unsupervised/

########################## DEBUG OUTPUT  ###########################
# grep for SLURM_EXPORT_ENV
echo "Temp data dir is : ${tempdatadir}"
echo "Output data dir is: ${outputdatadir}"
echo "Train data dir is: ${traindatadir}"
echo ${CUDA_VISIBLE_DEVICES}

################### SETUP SINGULARITY CONTAINER  ####################
# redefine SINGULARITY_HOME to mount current working directory to base $HOME
export SINGULARITY_HOME=$PWD:/home/$USER

echo $PWD
printf "Running training model"
# docker://python:latest
# singularity options: 
# -vvv -d = very verbose / debugging mode
# -B = bind path /scratch /work /data
singularity  exec -B /scratch/ --nv ./tensorflow.simg python main.py ${outputdatadir} ${tempdatadir} ${traindatadir}
# python test_v1.py ${outputdatadir} ${tempdatadir}

exit