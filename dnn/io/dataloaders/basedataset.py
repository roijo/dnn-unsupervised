import numpy as np 
from sklearn.model_selection import train_test_split

class Dataset(object):
    def __len__(self):
        return len(self.X)

    def split_data(self, train_size=.7):
        X_train, X_test, y_train, y_test = train_test_split(self.X, self.y, 
                                            test_size=1.-train_size)
        return X_train, X_test, y_train, y_test
        
    @property
    def imsize(self):
        if isinstance(self.X, list):
            return self.X[0].shape[2]
        return self.X.shape[2]

    @property
    def length_imsize(self):
        if self.X_aux is not None:
            if isinstance(self.X_aux, list):
                return self.X_aux[0].shape[1]
            return self.X_aux.shape[1]

        if isinstance(self.X, list):
            return self.X[0].shape[1]
        return self.X.shape[1]

    @property
    def width_imsize(self):
        if self.X_aux is not None:
            if isinstance(self.X_aux, list):
                return self.X_aux[0].shape[2]
            return self.X_aux.shape[2]

        if isinstance(self.X, list):
            return self.X[0].shape[2]
        return self.X.shape[2]

    @property
    def n_colors(self):
        if self.X_aux is not None:
            if isinstance(self.X_aux, list):
                return self.X_aux[0].shape[3]
            return self.X_aux.shape[3]

        if isinstance(self.X, list):
            return self.X[0].shape[3]
        return self.X.shape[3]

    def empty(self):
        self.X = None
        self.y = None
        self.X_aux = None
        self.class_weight = None

class TrainDataset(Dataset):
    X = None
    y = None
    class_weight = None
    def __init__(self, X, y, X_aux=None):
        if X.ndim==2:
            X = X[...,np.newaxis]
        self.X  = X 
        self.y = y 

        self.X_aux = X_aux

    def empty(self):
        self.X = None
        self.y = None
        self.class_weight = None

class TestDataset(Dataset):
    X = None
    y = None
    class_weight = None
    def __init__(self, X, y, X_aux=None):
        if X.ndim==2:
            X = X[...,np.newaxis]
        self.X  = X 
        self.y = y 

        self.X_aux = X_aux

    def empty(self):
        self.X = None
        self.y = None
        self.class_weight = None
        