from keras.callbacks import Callback
import numpy as np
from sklearn.metrics import roc_auc_score 
from sklearn.metrics import confusion_matrix, classification_report

from dnn.keras_models.metrics.classifier import BinaryClassifierMetric

class MetricsCallback(Callback):
    def __init__(self):
        super(MetricsCallback, self).__init__()
        
    def on_train_begin(self, logs={}):
        self.metrics = BinaryClassifierMetric()
        self.aucs = []
        self.roc_metrics = []
        self.fpr = []
        self.tpr = []
        self.thresholds = []
        
    def on_epoch_end(self, epoch, logs={}):
        # access the validatian data
        x = self.validation_data[0]
        y = self.validation_data[1]

        ytrue = np.argmax(y, axis=1)

        # compute loss, and accuracy of model
        inputs = {'input_layer': x}
        loss, acc = self.model.evaluate(inputs, y, verbose=0)
        predicted_probs = self.model.predict(inputs)

        if epoch < 5:
            print(x.shape)
            print(y.shape)
            print(predicted_probs.shape)
            print(y[0:5,:])
            print(predicted_probs[0:5,:])

        predicted_probs_positive = predicted_probs[:,1]
        predicted = np.argmax(predicted_probs, axis=1)
            
        # compute roc_auc scores using the predicted probabilties
        self.metrics.compute_roc(ytrue, predicted_probs_positive)
        # extract the receiver operating curve statistics
        fpr, tpr, thresholds = self.metrics.roc 
        self.fpr.append(fpr)
        self.tpr.append(tpr)
        self.thresholds.append(thresholds)

        # compute the AUC score
        self.aucs.append(roc_auc_score(ytrue, predicted_probs_positive))

        self.metrics.compute_metrics(ytrue, predicted)
        print('Testing loss: {}, acc: {}'.format(loss, acc))
        print('Mean accuracy score: {}'.format(self.metrics.accuracy))
        print('Recall: {}'.format(self.metrics.recall))
        print('Precision: {}'.format(self.metrics.precision))
        print("FPR: {}".format(self.metrics.fp))
        print('\n clasification report:\n',
              classification_report(ytrue, predicted))
        print('\n confusion matrix:\n', confusion_matrix(ytrue, predicted))

    def on_epoch_end_aux(self, epoch, logs={}):
        # access the validatian data
        x = self.validation_data[0]
        aux_x = self.validation_data[0]
        xvec = self.validation_data[1]
        y = self.validation_data[2]

        xvec = self.validation_data[0]
        y = self.validation_data[1]
        ytrue = np.argmax(y, axis=1)

        # compute loss, and accuracy of model
        inputs = {'aux_input_layer': aux_x,
                'input_layer': xvec}
        inputs = {'input_layer': xvec}
        loss, acc = self.model.evaluate(inputs, y, verbose=0)
        predicted_probs = self.model.predict(inputs)

        if epoch < 5:
            print(aux_x.shape)
            print(xvec.shape)
            print(y.shape)
            print(predicted_probs.shape)
            print(y[0:5,:])
            print(predicted_probs[0:5,:])

        predicted_probs_positive = predicted_probs[:,1]
        predicted = np.argmax(predicted_probs, axis=1)
        # compute the predicted classes
        # predicted = self.model.predict_classes({'aux_input_layer': aux_x,
        #                                 'input_layer': xvec})
            
        # compute roc_auc scores using the predicted probabilties
        self.metrics.compute_roc(ytrue, predicted_probs_positive)
        # extract the receiver operating curve statistics
        fpr, tpr, thresholds = self.metrics.roc 
        self.fpr.append(fpr)
        self.tpr.append(tpr)
        self.thresholds.append(thresholds)

        # compute the AUC score
        self.aucs.append(roc_auc_score(ytrue, predicted_probs_positive))

        self.metrics.compute_metrics(ytrue, predicted)
        print('Testing loss: {}, acc: {}'.format(loss, acc))
        print('Mean accuracy score: {}'.format(self.metrics.accuracy))
        print('Recall: {}'.format(self.metrics.recall))
        print('Precision: {}'.format(self.metrics.precision))
        print("FPR: {}".format(self.metrics.fp))
        print('\n clasification report:\n',
              classification_report(ytrue, predicted))
        print('\n confusion matrix:\n', confusion_matrix(ytrue, predicted))
