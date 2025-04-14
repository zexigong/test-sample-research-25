from __future__ import division
from __future__ import print_function

import os
import sys

import numpy as np
from sklearn.utils.testing import assert_equal
from sklearn.utils.testing import assert_raises

from pyod.models.knn import KNN
from pyod.utils.data import generate_data

# temporary solution for relative imports in case pyod is not installed
# if deep learning models are used, add tensorflow and keras to the path
sys.path.append(
    os.path.abspath(os.path.join(os.path.dirname("__file__"), '..')))

# TODO: bring this test back to the main test folder

class TestKNN:

    def setup_method(self):
        self.n_train = 200
        self.n_test = 100
        self.contamination = 0.1
        self.n_neighbors = 5

        self.X_train, self.X_test, self.y_train, self.y_test = \
            generate_data(n_train=self.n_train,
                          n_test=self.n_test,
                          n_features=3,
                          contamination=self.contamination,
                          random_state=42)

        self.clf = KNN(contamination=self.contamination,
                       n_neighbors=self.n_neighbors)
        self.clf.fit(self.X_train)

    def test_parameters(self):
        assert_equal(self.clf.decision_scores_.shape[0], self.n_train)
        assert_equal(self.clf.labels_.shape[0], self.n_train)
        assert_equal(self.clf.threshold_, np.percentile(
            self.clf.decision_scores_, 100 * (1 - self.contamination)))
        assert_equal(self.clf._classes, 2)

    def test_prediction_labels(self):
        pred_labels = self.clf.predict(self.X_test)
        assert_equal(pred_labels.shape[0], self.n_test)
        assert (pred_labels.min() == 0)
        assert (pred_labels.max() == 1)

    def test_prediction_probabilities(self):
        pred_proba = self.clf.predict_proba(self.X_test)
        assert_equal(pred_proba.shape, (self.n_test, 2))
        assert (pred_proba.min() >= 0)
        assert (pred_proba.max() <= 1)

    def test_prediction_proba_all(self):
        pred_proba = self.clf.predict_proba(self.X_test, method='unify')
        assert_equal(pred_proba.shape, (self.n_test, 2))
        assert (pred_proba.min() >= 0)
        assert (pred_proba.max() <= 1)

        assert_raises(ValueError, self.clf.predict_proba, self.X_test,
                      method='something')