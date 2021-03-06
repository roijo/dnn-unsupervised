#!/bin/bash

#SBATCH
#SBATCH --mail-type=end
#SBATCH --mail-user=ali39@jhu.edu
#SBATCH --output=_out/%A.out 
#SBATCH --error=_out/%A.err

# Author: Adam Li (ali39@jhu.edu).
# Created on 2017-10-31. 
#---------------------------------------------------------------------
# SLURM job script to run if access to CUDA is allowed
#---------------------------------------------------------------------
############################# LOAD IN MODULES AND UNLOAD #############
# activate our conda environment
. /soft/miniconda3/activate
source activate dnn

# cd to the scratch location 
cd /scratch/users/$USER/dnn-unsupervised/bin/

########################## DEBUG OUTPUT  ###########################
# grep for SLURM_EXPORT_ENV
echo "Temp data dir is : ${tempdatadir}"
echo "Output data dir is: ${outputdatadir}"
echo "Train data dir is: ${traindatadir}"
echo "Raw data dir is: ${rawdatadir}"
echo ${CUDA_VISIBLE_DEVICES}

################### SETUP SINGULARITY CONTAINER  ####################
# redefine SINGULARITY_HOME to mount current working directory to base $HOME
# export SINGULARITY_HOME=$PWD:/home/$USER

echo $PWD
printf "Running training model"
# docker://python:latest
# singularity options: 
# -vvv -d = very verbose / debugging mode
# -B = bind path /scratch /work /data

# for cnn
python ../trainbasecnn/main_refactored.py ${outputdatadir} ${tempdatadir} ${traindatadir} ${testdatadir}

# for training cnn-lstm
# python ./traincnnlstm/main.py ${outputdatadir} ${tempdatadir} ${traindatadir} ${rawdatadir}

# for training fragnet
# python ./trainfragaux/main_refactored.py ${outputdatadir} ${tempdatadir} ${traindatadir} ${rawdatadir}

exit