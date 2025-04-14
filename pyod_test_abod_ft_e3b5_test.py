# -*- coding: utf-8 -*-
"""Test the ABOD detector
"""
# Author: Yue Zhao <zhaoy@cmu.edu>
# License: BSD 2 clause

import os
import sys
import unittest

import numpy as np
from numpy.testing import assert_allclose
from numpy.testing import assert_equal
from sklearn.utils.testing import assert_raises

from pyod.models.abod import ABOD
from pyod.utils.data import generate_data

# temporary solution for relative imports in case pyod is not installed
# if deep and sklearn is not installed, run: pip install sklearn
sys.path.append(
    os.path.abspath(os.path.join(os.path.dirname("__file__"), '..')))


class TestABOD(unittest.TestCase):
    def setUp(self):
        self.contamination = 0.1
        self.n_train = 100
        self.n_test = 20
        self.n_features = 2
        self.roc_floor = 0.6

        self.X_train, self.X_test, self.y_train, self.y_test = \
            generate_data(n_train=self.n_train,
                          n_test=self.n_test,
                          n_features=self.n_features,
                          contamination=self.contamination,
                          random_state=42)

        self.clf = ABOD(contamination=self.contamination)
        self.clf.fit(self.X_train)

    def test_parameters(self):
        assert_allclose(self.clf.contamination, self.contamination)
        assert_allclose(self.clf.n_neighbors, 5)
        assert_equal(self.clf.method, 'fast')

    def test_fit(self):
        pass

    def test_predict(self):
        pred = self.clf.predict(self.X_test)
        assert_equal(pred.shape, (self.n_test,))

    def test_predict_proba(self):
        pred_proba = self.clf.predict_proba(self.X_test)
        assert_equal(pred_proba.shape, (self.n_test, 2))
        assert_allclose(pred_proba.sum(axis=1), np.ones(self.n_test))

    def test_predict_proba_default_ABOD(self):
        clf = ABOD(contamination=self.contamination, method='default')
        clf.fit(self.X_train)
        pred_proba = clf.predict_proba(self.X_test)
        assert_equal(pred_proba.shape, (self.n_test, 2))
        assert_allclose(pred_proba.sum(axis=1), np.ones(self.n_test))

    def test_label(self):
        pred = self.clf.predict(self.X_test)
        assert_equal(pred.shape, (self.n_test,))

    def test_decision_function(self):
        pred_score = self.clf.decision_function(self.X_test)
        assert_equal(pred_score.shape, (self.n_test,))

    def test_fast_abod(self):
        clf = ABOD(contamination=self.contamination, method='fast')
        clf.fit(self.X_train)

    def test_default_abod(self):
        clf = ABOD(contamination=self.contamination, method='default')
        clf.fit(self.X_train)

    def test_invalid_abod(self):
        with assert_raises(ValueError):
            ABOD(contamination=self.contamination, method='invalid')

    def test_plot(self):
        try:
            import matplotlib  # noqa
            self.clf.fit(self.X_train[:, :2])
            self.clf.plot(self.X_train[:, :2], self.y_train)
            self.clf.fit(self.X_train)
            self.clf.plot(self.X_train, self.y_train)
        except ImportError:
            return