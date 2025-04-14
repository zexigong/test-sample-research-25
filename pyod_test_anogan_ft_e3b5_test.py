import os
import sys

import numpy as np
import torch

from pyod.models.anogan import AnoGAN
from pyod.utils.data import generate_data
from pyod.utils.data import get_outliers_inliers
from sklearn.utils.validation import NotFittedError

# temporary solution for relative imports in case pyod is not installed
# if the script is run without installing pyod
sys.path.append(
    os.path.abspath(os.path.join(os.path.dirname("__file__"), '..')))


class TestAnoGAN:
    def setup_class(self):
        self.n_train = 1000
        self.n_test = 500
        self.contamination = 0.1
        self.epochs = 2
        self.epochs_query = 2
        self.device = 'cuda' if torch.cuda.is_available() else 'cpu'
        self.X_train, self.X_test, self.y_train, self.y_test = generate_data(
            n_train=self.n_train, n_test=self.n_test, n_features=2,
            contamination=self.contamination)

        self.clf = AnoGAN(epochs=self.epochs, epochs_query=self.epochs_query,
                          dropout_rate=0.2, batch_size=32,
                          contamination=self.contamination, device=self.device)
        self.clf.fit(self.X_train)

    def test_prediction_labels(self):
        pred_labels = self.clf.labels_
        assert (self.clf._classes == 2)
        assert (len(pred_labels) == self.n_train)

    def test_prediction_scores(self):
        pred_scores = self.clf.decision_scores_
        assert (pred_scores is not None)
        assert (len(pred_scores) == self.n_train)

    def test_prediction_labels_test(self):
        pred_labels = self.clf.predict(self.X_test)
        assert (len(pred_labels) == self.n_test)

    def test_prediction_scores_test(self):
        pred_scores = self.clf.decision_function(self.X_test)
        assert (pred_scores is not None)
        assert (len(pred_scores) == self.n_test)

    def test_prediction_proba(self):
        pred_proba = self.clf.predict_proba(self.X_test)
        assert (pred_proba is not None)
        assert (len(pred_proba) == self.n_test)
        assert (pred_proba.min() >= 0)
        assert (pred_proba.max() <= 1)

    def test_prediction_proba_train(self):
        pred_proba = self.clf.predict_proba(self.X_train)
        assert (pred_proba is not None)
        assert (len(pred_proba) == self.n_train)
        assert (pred_proba.min() >= 0)
        assert (pred_proba.max() <= 1)

    def test_plot(self):
        self.clf.plot_learning_curves(start_ind=0, window_smoothening=10)

    def test_fit_predict(self):
        try:
            self.clf.fit_predict(self.X_test)
        except NotFittedError as e:
            assert str(e) == (
                "This AnoGAN instance is not fitted yet. Call 'fit' "
                "with appropriate arguments before using this estimator.")