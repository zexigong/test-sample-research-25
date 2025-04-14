# -*- coding: utf-8 -*-
"""Connectivity-Based Outlier Factor (COF) Algorithm

"""
# Author: Yue Zhao <zhaoy@cmu.edu>
# License: BSD 2 clause

import os
import sys

import numpy as np
from numpy.testing import assert_allclose
from numpy.testing import assert_equal
from sklearn.metrics import roc_auc_score

from pyod.models.cof import COF
from pyod.utils.data import generate_data
from pyod.utils.data import get_outliers_inliers

from pyod.utils.example import visualize

# temporary solution for relative imports in case pyod is not installed
# if deep learning is used, add tensorflow to PYTHONPATH
sys.path.append(
    os.path.abspath(os.path.join(os.path.dirname("__file__"), '..')))


class TestCOF:
    def setup_method(self):
        # Generate a random dataset
        self.n_train = 200
        self.n_test = 100
        self.n_features = 2
        self.contamination = 0.1
        self.roc_floor = 0.7
        self.X_train, self.X_test, self.y_train, self.y_test = \
            generate_data(n_train=self.n_train,
                          n_test=self.n_test,
                          n_features=self.n_features,
                          contamination=self.contamination,
                          random_state=42)

        self.clf = COF(contamination=self.contamination)
        self.clf.fit(self.X_train)

    def test_parameters(self):
        assert self.clf.n_neighbors_ == self.clf.n_neighbors

    def test_train_scores(self):
        # Ensure labels have correct shapes
        assert self.clf.decision_scores_.shape[0] == self.n_train

    def test_prediction_labels(self):
        self.y_train_pred = self.clf.labels_
        self.y_test_pred = self.clf.predict(self.X_test)
        assert self.y_train_pred.shape[0] == self.n_train
        assert self.y_test_pred.shape[0] == self.n_test

    def test_prediction_probabilities(self):
        self.y_train_pred_proba = self.clf.predict_proba(self.X_train)
        self.y_test_pred_proba = self.clf.predict_proba(self.X_test)
        assert self.y_train_pred_proba.shape[0] == self.n_train
        assert self.y_train_pred_proba.shape[1] == 2
        assert self.y_test_pred_proba.shape[0] == self.n_test
        assert self.y_test_pred_proba.shape[1] == 2

    def test_prediction_confidence(self):
        self.y_train_confidence = self.clf.predict_confidence(self.X_train)
        self.y_test_confidence = self.clf.predict_confidence(self.X_test)
        assert self.y_train_confidence.shape[0] == self.n_train
        assert self.y_test_confidence.shape[0] == self.n_test

    def test_prediction_with_rejection(self):
        self.y_train_pred_rejection = self.clf.predict_with_rejection(
            self.X_train)
        self.y_test_pred_rejection = self.clf.predict_with_rejection(
            self.X_test)
        assert self.y_train_pred_rejection.shape[0] == self.n_train
        assert self.y_test_pred_rejection.shape[0] == self.n_test

    def test_prediction_with_rejection_return_stats(self):
        self.y_train_pred_rejection_return_stats = self.clf.predict_with_rejection(
            self.X_train, return_stats=True)
        self.y_test_pred_rejection_return_stats = self.clf.predict_with_rejection(
            self.X_test, return_stats=True)
        assert self.y_train_pred_rejection_return_stats[0].shape[0] == self.n_train
        assert self.y_test_pred_rejection_return_stats[0].shape[0] == self.n_test

    def test_decision_function(self):
        self.y_train_scores = self.clf.decision_function(self.X_train)
        self.y_test_scores = self.clf.decision_function(self.X_test)
        assert self.y_train_scores.shape[0] == self.n_train
        assert self.y_test_scores.shape[0] == self.n_test

    def test_auc(self):
        self.y_test_scores = self.clf.decision_function(self.X_test)
        assert roc_auc_score(self.y_test, self.y_test_scores) > self.roc_floor

    def test_decision_function_fast(self):
        self.clf = COF(contamination=self.contamination, method='fast')
        self.clf.fit(self.X_train)
        self.y_train_scores = self.clf.decision_function(self.X_train)
        self.y_test_scores = self.clf.decision_function(self.X_test)
        assert roc_auc_score(self.y_test, self.y_test_scores) > self.roc_floor

    def test_decision_function_memory(self):
        self.clf = COF(contamination=self.contamination, method='memory')
        self.clf.fit(self.X_train)
        self.y_train_scores = self.clf.decision_function(self.X_train)
        self.y_test_scores = self.clf.decision_function(self.X_test)
        assert roc_auc_score(self.y_test, self.y_test_scores) > self.roc_floor

    def test_plot(self):
        visualize(self.clf, self.X_train, self.y_train, self.X_test,
                  self.y_test, "COF")