# -*- coding: utf-8 -*-
"""Unit test for ALAD
"""
# Author: Michiel Bongaerts <michiel.bongaerts@outlook.com>
# License: BSD 2 clause

import os
import sys

import numpy as np
from nose.tools import assert_raises, assert_greater

from pyod.models.alad import ALAD
from pyod.utils.data import generate_data

import torch

# temporary solution for relative imports in case pyod is not installed
# if you have pyod installed, just import normally
sys.path.append(
    os.path.abspath(os.path.join(os.path.dirname("__file__"), '..')))

# generate random data with 2 features
n_train = 100
n_test = 50
n_features = 2

X_train, X_test, y_train, y_test = generate_data(n_train=n_train,
                                                 n_test=n_test,
                                                 n_features=n_features,
                                                 random_state=42)

# train ALAD
contamination = 0.1
latent_dim = 2
recon_loss = True
lambda_recon_loss = 0.1
n_epochs = 10

# initialize a ALAD model
alad = ALAD(contamination=contamination,
            latent_dim=latent_dim,
            epochs=n_epochs,
            add_recon_loss=recon_loss,
            lambda_recon_loss=lambda_recon_loss)

alad.fit(X_train)


def test_train_scores():
    assert alad.decision_scores_ is not None
    assert len(alad.decision_scores_) == X_train.shape[0]


def test_train_labels():
    assert alad.labels_ is not None
    assert len(alad.labels_) == X_train.shape[0]


def test_train_threshold():
    assert alad.threshold_ is not None
    assert isinstance(alad.threshold_, float)


def test_predict_raw():
    assert alad.decision_function(X_test) is not None
    assert len(alad.decision_function(X_test)) == X_test.shape[0]


def test_predict_labels():
    assert alad.predict(X_test) is not None
    assert len(alad.predict(X_test)) == X_test.shape[0]


def test_predict_proba():
    assert alad.predict_proba(X_test) is not None
    assert len(alad.predict_proba(X_test)) == X_test.shape[0]
    assert alad.predict_proba(X_test).max() <= 1
    assert alad.predict_proba(X_test).min() >= 0


def test_plot():
    try:
        alad.plot_learning_curves()
    except:
        pass


def test_fit():
    alad.fit(X_train, y_train)


def test_fit_exception():
    alad.fit(X_train.tolist(), y_train)


def test_predict():
    assert_greater(alad.predict(X_test).sum(), 0)


def test_predict_proba():
    alad.predict_proba(X_test)


def test_predict_proba_linear():
    alad.predict_proba(X_test, method='linear')


def test_predict_proba_unify():
    alad.predict_proba(X_test, method='unify')


def test_predict_proba_default():
    alad.predict_proba(X_test, method='default')


def test_predict_proba_invalid_method():
    with assert_raises(ValueError):
        alad.predict_proba(X_test, method='something')


def test_decision_function():
    alad.decision_function(X_test)


def test_model_clone():
    from sklearn.base import clone
    clone(alad)