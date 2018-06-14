import os
import numpy as np
import keras
from keras.optimizers import Adam
from keras.callbacks import ModelCheckpoint, ReduceLROnPlateau
from keras.preprocessing.image import ImageDataGenerator

import dnn
import dnn.base.constants.model_constants as MODEL_CONSTANTS
from dnn.keras_models.trainers.base import BaseTrainer
from dnn.keras_models.trainers.callbacks.testingcallback import MetricsCallback
from dnn.util.keras.augmentations import Augmentations 
from dnn.util.generators.imgseq.generator import ImageSeqDataGenerator

from dnn.keras_models.metrics.classifier import BinaryClassifierMetric
from dnn.base.constants.config import Config, OutputConfig
from dnn.keras_models.regularizer.post_class_regularizer import Postalarm
# import tensorboardX  # import SummaryWriter
# from tqdm import trange

# set the random seed
from numpy.random import seed
seed(1)
from tensorflow import set_random_seed
set_random_seed(2)

class RCNNTrainer(BaseTrainer):
    metric_comp = BinaryClassifierMetric()
    post_regularizer = None
    HH = None

    def __init__(self, model, num_epochs=MODEL_CONSTANTS.NUM_EPOCHS, 
                 batch_size=MODEL_CONSTANTS.BATCH_SIZE,
                 testpatdir=None,
                 learning_rate=MODEL_CONSTANTS.LEARNING_RATE,
                 shuffle=MODEL_CONSTANTS.SHUFFLE,
                 augment=MODEL_CONSTANTS.AUGMENT,
                 config=None):
        '''         SET LOGGING DIRECTORIES: MODEL, TENSORBOARD         '''
        self.testpatdir = testpatdir
        super(CNNTrainer, self).__init__(model=model,
                                         config=config)

        # Hyper parameters - training
        self.learning_rate = learning_rate
        self.num_epochs = num_epochs
        self.batch_size = batch_size
        # hyper parameters - dataset
        self.shuffle = shuffle
        self.AUGMENT = augment

        self.save_summary_steps = 10
        self.gradclip_value = 0.25

        # set tensorboard writer
        self._setdirs()  # set directories for all logging
        # self.writer = tensorboardX.SummaryWriter(self.tboardlogdir)

        self.logger.info(
            "Logging output data to: {}".format(
                self.outputdatadir))
        self.logger.info(
            "Logging experimental data at: {}".format(
                self.explogdir))
        self.logger.info(
            "Logging tensorboard data at: {}".format(
                self.tboardlogdir))

    def _setdirs(self):
        # set where to log outputs of explog
        if self.testpatdir is None:
            self.explogdir = os.path.join(
                self.config.tboard.FOLDER_LOGS, 'traininglogs')
            self.tboardlogdir = os.path.join(
                self.config.tboard.FOLDER_LOGS, 'tensorboard')
            self.outputdatadir = os.path.join(
                self.config.tboard.FOLDER_LOGS, 'output')
        else:
            self.explogdir = os.path.join(self.testpatdir, 'traininglogs')
            self.tboardlogdir = os.path.join(self.testpatdir, 'tensorboard')
            self.outputdatadir = os.path.join(self.testpatdir, 'output')

        if not os.path.exists(self.explogdir):
            os.makedirs(self.explogdir)
        if not os.path.exists(self.tboardlogdir):
            os.makedirs(self.tboardlogdir)
        if not os.path.exists(self.outputdatadir):
            os.makedirs(self.outputdatadir)

    def composedatasets(self, train_dataset, test_dataset):
        self.train_dataset = train_dataset
        self.test_dataset = test_dataset

        # get input characteristics
        self.imsize = train_dataset.imsize
        self.n_colors = train_dataset.n_colors
        # size of training/testing set
        self.train_size = len(train_dataset)
        self.val_size = len(test_dataset)

        self.steps_per_epoch = self.train_size // self.batch_size

        self.logger.info(
            "Each training epoch is {} steps and each validation is {} steps.".format(
                self.train_size, self.val_size))
        self.logger.info(
            "Setting the datasets for training/testing in trainer object!")
        self.logger.info(
            "Image size is {} with {} colors".format(
                self.imsize, self.n_colors))

    def compose_sequence(self):
        pass

    def configure(self):
        """
        Configuration function that can change:
        - sets optimizer
        - sets loss function
        - sets scheduler
        - sets post-prediction-regularizer
        """
        # initialize loss function, SGD optimizer and metrics
        clipnorm = 1.
        model_params = {
            'loss': 'binary_crossentropy',
            'optimizer': Adam(lr=1e-5,
                         beta_1=0.9, beta_2=0.99,
                         epsilon=1e-08, decay=0.0,
                         amsgrad=True, clipnorm=clipnorm),
            'metrics': ['accuracy']
        }
        self.modelconfig = self.model.compile(**model_params)

        tempfilepath = os.path.join(self.explogdir, "weights-improvement-{epoch:02d}-{val_acc:.2f}.hdf5")

        '''                         CREATE CALLBACKS                        '''
        # callbacks availabble
        checkpoint = ModelCheckpoint(tempfilepath,
                                     monitor='val_acc',
                                     verbose=1,
                                     save_best_only=True,
                                     mode='max')
        reduce_lr = ReduceLROnPlateau(monitor='val_loss', 
                                    factor=0.5,
                                    patience=10, 
                                    min_lr=1e-8)
        tboard = keras.callbacks.TensorBoard(log_dir=self.tboardlogdir, 
                                    histogram_freq=self.num_epochs/10, 
                                    batch_size=self.batch_size, write_graph=True, 
                                    write_grads=True, write_images=True, 
                                    embeddings_freq=0, 
                                    embeddings_layer_names=None, 
                                    embeddings_metadata=None, 
                                    embeddings_data=None)
        metrichistory = MetricsCallback()
        self.callbacks = [checkpoint,
                        reduce_lr,
                        tboard,
                        metrichistory]

    def train(self):
        self._loadgenerator()

        print("Training data: ", self.train_dataset.X_train[0].shape,  len(self.train_dataset[0].y_train))
        print("Testing data: ",  self.test_dataset.X_test[0].shape,  len(self.test_dataset.y_test[0]))
        print("Class weights are: ",  self.train_dataset.class_weight)
        test = np.argmax( self.train_dataset.y_train, axis=1)
        print("class imbalance: ", np.sum(test), len(test))

        # augment data, or not and then trian the model!
        if not self.AUGMENT:
            print('Not using data augmentation. Implement Solution still!')
            HH = self.model.fit( self.train_dataset.X_train,  self.train_dataset.y_train,
                              steps_per_epoch=self.steps_per_epoch,
                              batch_size = self.batch_size,
                              epochs=self.num_epochs,
                              validation_data=(self.test_dataset.X_test, self.test_dataset.y_test),
                              shuffle=self.shuffle,
                              class_weight= self.train_dataset.class_weight,
                              callbacks=self.callbacks)
        else:
            print('Using real-time data augmentation.')
            self.generator.fit(np.array(self.train_dataset.X_train).reshape(-1,self.imsize,self.imsize,self.n_colors))
            HH = self.model.fit_generator(self.generator.flow(self.train_dataset.X_train, 
                                                            self.train_dataset.y_train, 
                                                            batch_size=self.batch_size),
                                        steps_per_epoch=self.steps_per_epoch,
                                        epochs=self.num_epochs,
                                        validation_data=(self.test_dataset.X_test, self.test_dataset.y_test),
                                        shuffle=self.shuffle,
                                        class_weight= self.train_dataset.class_weight,
                                        callbacks=self.callbacks, verbose=2)

        self.HH = HH
        self.metrichistory = self.callbacks[3] 

    def _loadgenerator(self):
        imagedatagen_args = {
            'featurewise_center':True,  # set input mean to 0 over the dataset
            'samplewise_center':True,  # set each sample mean to 0
            'featurewise_std_normalization':True,  # divide inputs by std of the dataset
            'samplewise_std_normalization':True,  # divide each input by its std
            'zca_whitening':False,      # apply ZCA whitening
            # randomly rotate images in the range (degrees, 0 to 180)
            'rotation_range':5,
            # randomly shift images horizontally (fraction of total width)
            'width_shift_range':0.2,
            # randomly shift images vertically (fraction of total height)
            'height_shift_range':0.2,
            'horizontal_flip':True,    # randomly flip images
            'vertical_flip':True,      # randomly flip images
            'channel_shift_range':4,
            'fill_mode':'nearest',
            'preprocessing_function': Augmentations.preprocess_imgwithnoise
        }

        # This will do preprocessing and realtime data augmentation:
        self.generator = ImageSeqDataGenerator(**imagedatagen_args)

if __name__ == '__main__':
    from dnn.keras_models.nets.cnn import iEEGCNN
    from dnn.io.readerimgdataset import ReaderImgDataset 
    import dnn.base.constants.model_constants as constants

    data_procedure = 'loo'
    testpat = 'id001_bt'
    traindir = os.path.expanduser('~/Downloads/tngpipeline/freq/fft_img/')
    testdir = traindir
    # initialize reader to get the training/testing data
    reader = ReaderImgDataset()
    reader.loadbydir(traindir, testdir, procedure=data_procedure, testname=testpat)
    reader.loadfiles(mode=constants.TRAIN)
    reader.loadfiles(mode=constants.TEST)
    
    # create the dataset objects
    train_dataset = reader.train_dataset
    test_dataset = reader.test_dataset

    # define model
    model_params = {
        'num_classes': 2,
        'imsize': 64,
        'n_colors':4,
    }
    model = iEEGCNN(**model_params) 
    model.buildmodel(output=True)

    num_epochs = 1
    batch_size = 32
    testpatdir = './'
    trainer = CNNTrainer(model=model.net, num_epochs=num_epochs, 
                        batch_size=batch_size,
                        testpatdir=testpatdir)
    trainer.composedatasets(train_dataset, test_dataset)
    trainer.configure()
    # Train the model
    # trainer.train()
    modelname='test'
    trainer.saveoutput(modelname=modelname)
    trainer.savemetricsoutput(modelname=modelname)
    print(model.net)