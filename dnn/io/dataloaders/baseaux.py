import numpy as np
import pandas as pd
import json
import os

from dnn.base.constants.config import Config
from dnn.base.utils.log_error import initialize_logger
import dnn.base.constants.model_constants as constants
from sklearn.utils import compute_class_weight

# preprocessing data
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import scale

class TrainDataset(object):
    X_aux = None
    X_chan = None
    ylabels = None
    class_weight = None

    def __len__(self):
        return len(self.X_chan)

    @property
    def width_imsize(self):
        if isinstance(self.X_aux, list):
            return self.X_aux[0].shape[2]
        return self.X_aux.shape[2]

    @property
    def n_colors(self):
        if isinstance(self.X_aux, list):
            return self.X_aux[0].shape[3]
        return self.X_aux.shape[3]

    @property
    def length_imsize(self):
        if isinstance(self.X_aux, list):
            return self.X_aux[0].shape[1]
        return self.X_aux.shape[1]


class TestDataset(object):
    X_aux = None
    X_chan = None
    ylabels = None
    class_weight = None

    def __len__(self):
        return len(self.X_chan)

    @property
    def width_imsize(self):
        if isinstance(self.X_aux, list):
            return self.X_aux[0].shape[2]
        return self.X_aux.shape[2]

    @property
    def n_colors(self):
        if isinstance(self.X_aux, list):
            return self.X_aux[0].shape[3]
        return self.X_aux.shape[3]

    @property
    def length_imsize(self):
        if isinstance(self.X_aux, list):
            return self.X_aux[0].shape[1]
        return self.X_aux.shape[1]
        
class BaseAuxLoader(object):
    root_dir = None
    patients = None
    testfilepaths = None
    trainfilepaths = None
    filelist = None

    train_dataset = TrainDataset()
    test_dataset = TestDataset()

    def __init__(self, config=None):
        self.config = config or Config()
        self.logger = initialize_logger(
            self.__class__.__name__,
            self.config.out.FOLDER_LOGS)

    def __len__(self):
        return len(self.filelist)

    def loadbydir(self, traindir, testdir, procedure='loo', testname=None):
        raise NotImplementedError("Need to implement function to load filepaths\
                for all datasets into list.")

    def loadfiles(self, filelist=[], mode=constants.TRAIN):
        raise NotImplementedError("Need to implement function to load files into memory.")

    def _formatdata(self, images):
        images = images.swapaxes(1, 3)
        # lower sample by casting to 32 bits
        images = images.astype("float32")
        return images

    def getchanstats(self, images, numchans, chanaxis=3):
        '''
        Chan axis = 3 if using keras/tensorflow
        Chan axis = 1 if using pytorch
        '''
        chanmeans = []
        chanstd = []
        for ichan in range(numchans):
            chandata = images[...,ichan].ravel()
            chanmeans.append(np.mean(chandata))
            chanstd.append(np.std(chandata))
        self.chanmeans = np.array(chanmeans)
        self.chanstd = np.array(chanstd)

