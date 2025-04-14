import pytest
import numpy as np
from pyod.models.hbos import HBOS
from sklearn.utils.estimator_checks import check_estimator
from numpy.testing import assert_allclose
from sklearn.utils.validation import check_is_fitted

@pytest.fixture
def data():
    X_train = np.array([[1.0, 2.0], [1.1, 2.1], [1.2, 2.2], [1.3, 2.3], [10.0, 10.0]])
    X_test = np.array([[1.05, 2.05], [0.9, 1.8], [1.5, 2.5]])
    return X_train, X_test

def test_hbos_fit(data):
    X_train, _ = data
    model = HBOS()
    model.fit(X_train)
    check_is_fitted(model, ['hist_', 'bin_edges_'])

def test_hbos_decision_function(data):
    X_train, X_test = data
    model = HBOS()
    model.fit(X_train)
    scores = model.decision_function(X_test)
    assert scores.shape[0] == X_test.shape[0]
    assert np.all(scores >= 0)

def test_hbos_predict(data):
    X_train, X_test = data
    model = HBOS()
    model.fit(X_train)
    predictions = model.predict(X_test)
    assert predictions.shape[0] == X_test.shape[0]
    assert set(predictions).issubset({0, 1})

def test_hbos_threshold(data):
    X_train, _ = data
    model = HBOS(contamination=0.2)
    model.fit(X_train)
    assert 0 <= model.threshold_ <= 1

def test_hbos_auto_n_bins(data):
    X_train, _ = data
    model = HBOS(n_bins='auto')
    model.fit(X_train)
    assert len(model.hist_) == X_train.shape[1]
    assert len(model.bin_edges_) == X_train.shape[1]

def test_hbos_check_estimator():
    check_estimator(HBOS)

def test_hbos_invert_order(data):
    X_train, X_test = data
    model = HBOS()
    model.fit(X_train)
    scores = model.decision_function(X_test)
    inverted_scores = -scores
    assert_allclose(inverted_scores, model.decision_function(X_test, method='multiplication'), atol=1e-5)