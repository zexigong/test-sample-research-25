# -*- coding: utf-8 -*-
"""Test HBOS
"""

import os
import sys

import numpy as np
from numpy.testing import assert_allclose
from numpy.testing import assert_array_less
from sklearn.metrics import roc_auc_score
from sklearn.model_selection import train_test_split
from sklearn.utils import check_random_state

from pyod.models.hbos import HBOS
from pyod.utils.data import generate_data

# temporary solution for relative imports in case pyod is not installed
# if the code is run without installation
try:
    from pyod.models.hbos import HBOS
    from pyod.utils.data import generate_data
except ImportError:
    import sys
    import os

    sys.path.append(
        os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

    from pyod.models.hbos import HBOS
    from pyod.utils.data import generate_data

# Define data file and read X and y
from pyod.utils.data import generate_data

# Test Parameters
n_train = 200
n_test = 100
n_features = 2

contamination = 0.1
tol = 0.5
alpha = 0.1

random_state = np.random.RandomState(42)
X_train, X_test, y_train, y_test = generate_data(
    n_train=n_train,
    n_test=n_test,
    n_features=n_features,
    contamination=contamination,
    random_state=random_state)

hbos = HBOS(contamination=contamination)
hbos.fit(X_train)

# get the prediction on the test data
y_train_pred = hbos.labels_  # binary labels (0: inliers, 1: outliers)
y_train_scores = hbos.decision_scores_  # raw outlier scores
y_test_pred = hbos.predict(X_test)  # outlier labels (0 or 1)
y_test_scores = hbos.decision_function(X_test)  # outlier scores


def test_parameters():
    assert hbos.alpha == alpha
    assert hbos.tol == tol


def test_prediction_labels():
    assert y_train_pred.shape[0] == n_train
    assert y_test_pred.shape[0] == n_test

    # make sure all the predicted labels are either 0 or 1
    assert np.array_equal(np.unique(y_test_pred), [0, 1])


def test_prediction_scores():
    assert y_train_scores.shape[0] == n_train
    assert y_test_scores.shape[0] == n_test

    # check if the scores are all positive
    assert (y_train_scores >= 0).all()
    assert (y_test_scores >= 0).all()


def test_auc():
    assert roc_auc_score(y_test, y_test_scores) >= 0.8


def test_decision_function():
    # decision function must be the same as predicting raw outlier scores
    assert_allclose(hbos.decision_function(X_test), y_test_scores)


def test_prediction_proba():
    y_train_proba = hbos.predict_proba(X_train)
    y_test_proba = hbos.predict_proba(X_test)

    # check proba shape
    assert y_train_proba.shape == (n_train, 2)
    assert y_test_proba.shape == (n_test, 2)

    # check if all probability within the range
    assert (y_train_proba >= 0).all() & (y_train_proba <= 1).all()
    assert (y_test_proba >= 0).all() & (y_test_proba <= 1).all()

    # check if both labels are all zero
    assert (y_train_proba.sum(axis=1) == 1).all()
    assert (y_test_proba.sum(axis=1) == 1).all()


def test_fit_predict_score():
    model = HBOS(contamination=contamination)
    score = model.fit_predict_score(X_test, y_test)
    assert score >= 0.8


def test_train_scores():
    # check the train scores are the same as
    # the decision function on the train set
    assert_allclose(hbos.decision_scores_, hbos.decision_function(X_train))


def test_python_version():
    if (sys.version_info > (3, 0)):
        assert (True)
    else:
        assert (True)