# -*- coding: utf-8 -*-
"""Test Gaussian Mixture Model Detector
"""
# Author: Akira Tamamori <tamamori5917@gmail.com>
# License: BSD 2 clause

import os
import sys
import unittest

import numpy as np
from numpy.testing import assert_allclose
from sklearn.utils.testing import assert_array_less

from pyod.models.gmm import GMM

# temporary solution for relative imports in case pyod is not installed
# if it is installed, ignore it
# noinspection PyUnresolvedReferences
try:
    from pyod.utils.data import generate_data
    from pyod.utils.data import get_outliers_inliers
except ImportError:
    import sys
    sys.path.append(
        os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

    from pyod.utils.data import generate_data
    from pyod.utils.data import get_outliers_inliers


class TestGMM(unittest.TestCase):
    def setUp(self):
        self.n_train = 200
        self.n_test = 100
        self.n_features = 2

        # Generate train data
        X, y = generate_data(n_train=self.n_train,
                             n_test=self.n_test,
                             n_features=self.n_features)
        self.X_train, self.X_test = X[:self.n_train, :], X[self.n_train:, :]
        self.y_train, self.y_test = y[:self.n_train], y[self.n_train:]
        self.X_outliers, self.X_inliers = get_outliers_inliers(X, y)

        self.clf = GMM()

    def test_fit(self):
        self.clf.fit(self.X_train)

        # Make sure fit attributes are set
        assert hasattr(self.clf, 'decision_scores_')
        assert hasattr(self.clf, 'labels_')
        assert hasattr(self.clf, 'threshold_')

    def test_predict(self):
        self.clf.fit(self.X_train)

        pred_labels = self.clf.predict(self.X_test)
        assert_allclose(pred_labels, self.y_test)

    def test_predict_proba(self):
        self.clf.fit(self.X_train)

        pred_labels = self.clf.predict(self.X_test)
        pred_proba = self.clf.predict_proba(self.X_test)
        assert_array_less(pred_proba[:, 1], 1)
        assert_array_less(0, pred_proba[:, 1])

    def test_score(self):
        self.clf.fit(self.X_train)

        # test on the inliers
        pred_score = self.clf.decision_function(self.X_inliers)
        assert_array_less(pred_score, self.clf.threshold_)

        # test on the outliers
        pred_score = self.clf.decision_function(self.X_outliers)
        assert_array_less(self.clf.threshold_, pred_score)

    def test_pickle(self):
        import pickle
        self.clf.fit(self.X_train)
        pickled_clf = pickle.dumps(self.clf)
        unpickled_clf = pickle.loads(pickled_clf)
        assert_allclose(unpickled_clf.decision_function(self.X_test),
                        self.clf.decision_function(self.X_test),
                        atol=1e-4)


if __name__ == '__main__':
    unittest.main()