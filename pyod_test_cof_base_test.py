import pytest
import numpy as np
from pyod.models.cof import COF

@pytest.fixture
def data():
    X_train = np.array([[0, 0], [1, 1], [0, 1], [1, 0], [0.5, 0.5]])
    X_test = np.array([[0, 0], [1, 1], [0.1, 0.1]])
    return X_train, X_test

def test_cof_initialization():
    clf = COF(contamination=0.1, n_neighbors=2, method='fast')
    assert clf.contamination == 0.1
    assert clf.n_neighbors == 2
    assert clf.method == 'fast'

    with pytest.raises(TypeError):
        COF(n_neighbors='not an int')

    with pytest.raises(ValueError):
        COF(method='invalid')

def test_fit(data):
    X_train, _ = data
    clf = COF(contamination=0.1, n_neighbors=2)
    clf.fit(X_train)
    assert hasattr(clf, 'decision_scores_')
    assert hasattr(clf, 'threshold_')
    assert hasattr(clf, 'labels_')

def test_decision_function_fast(data):
    X_train, X_test = data
    clf = COF(contamination=0.1, n_neighbors=2, method='fast')
    clf.fit(X_train)
    scores = clf.decision_function(X_test)
    assert scores.shape[0] == X_test.shape[0]
    assert np.all(scores >= 0)

def test_decision_function_memory(data):
    X_train, X_test = data
    clf = COF(contamination=0.1, n_neighbors=2, method='memory')
    clf.fit(X_train)
    scores = clf.decision_function(X_test)
    assert scores.shape[0] == X_test.shape[0]
    assert np.all(scores >= 0)

def test_predict(data):
    X_train, X_test = data
    clf = COF(contamination=0.1, n_neighbors=2)
    clf.fit(X_train)
    predictions = clf.predict(X_test)
    assert predictions.shape[0] == X_test.shape[0]
    assert np.all(np.isin(predictions, [0, 1]))

def test_predict_proba(data):
    X_train, X_test = data
    clf = COF(contamination=0.1, n_neighbors=2)
    clf.fit(X_train)
    probas = clf.predict_proba(X_test)
    assert probas.shape == (X_test.shape[0], 2)
    assert np.allclose(probas.sum(axis=1), 1)

def test_fit_predict(data):
    X_train, _ = data
    clf = COF(contamination=0.1, n_neighbors=2)
    labels = clf.fit_predict(X_train)
    assert labels.shape[0] == X_train.shape[0]
    assert np.all(np.isin(labels, [0, 1]))