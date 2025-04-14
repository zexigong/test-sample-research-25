import pytest
import numpy as np
from pyod.models.abod import ABOD
from sklearn.utils.testing import assert_allclose, assert_raises

@pytest.fixture
def abod_default():
    return ABOD()

@pytest.fixture
def abod_fast():
    return ABOD(method='fast', n_neighbors=5)

@pytest.fixture
def sample_data():
    X_train = np.array([[1.0, 2.0],
                        [2.0, 3.0],
                        [3.0, 4.0],
                        [4.0, 5.0],
                        [5.0, 6.0]])
    X_test = np.array([[1.5, 2.5],
                       [2.5, 3.5],
                       [3.5, 4.5],
                       [4.5, 5.5]])
    return X_train, X_test

def test_abod_default_fit(abod_default, sample_data):
    X_train, _ = sample_data
    abod_default.fit(X_train)
    assert hasattr(abod_default, 'decision_scores_')
    assert hasattr(abod_default, 'threshold_')
    assert hasattr(abod_default, 'labels_')
    assert len(abod_default.decision_scores_) == X_train.shape[0]

def test_abod_fast_fit(abod_fast, sample_data):
    X_train, _ = sample_data
    abod_fast.fit(X_train)
    assert hasattr(abod_fast, 'decision_scores_')
    assert hasattr(abod_fast, 'threshold_')
    assert hasattr(abod_fast, 'labels_')
    assert len(abod_fast.decision_scores_) == X_train.shape[0]

def test_abod_default_decision_function(abod_default, sample_data):
    X_train, X_test = sample_data
    abod_default.fit(X_train)
    scores = abod_default.decision_function(X_test)
    assert scores.shape[0] == X_test.shape[0]

def test_abod_fast_decision_function(abod_fast, sample_data):
    X_train, X_test = sample_data
    abod_fast.fit(X_train)
    scores = abod_fast.decision_function(X_test)
    assert scores.shape[0] == X_test.shape[0]

def test_abod_invalid_method():
    with assert_raises(ValueError):
        ABOD(method='invalid')

def test_abod_n_neighbors_warning():
    with pytest.warns(UserWarning):
        abod = ABOD(n_neighbors=10)
        X_train = np.array([[1.0, 2.0],
                            [2.0, 3.0],
                            [3.0, 4.0]])
        abod.fit(X_train)

def test_abod_score_consistency(sample_data):
    X_train, X_test = sample_data
    abod_default = ABOD()
    abod_fast = ABOD(method='fast', n_neighbors=5)
    abod_default.fit(X_train)
    abod_fast.fit(X_train)
    scores_default = abod_default.decision_function(X_test)
    scores_fast = abod_fast.decision_function(X_test)
    assert_allclose(scores_default, scores_fast, rtol=1e-1)