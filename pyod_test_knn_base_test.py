# test_knn.py

import pytest
import numpy as np
from pyod.models.knn import KNN
from sklearn.utils.validation import NotFittedError


@pytest.fixture
def sample_data():
    X_train = np.array([[1.0, 2.0], [2.0, 1.0], [1.5, 1.5], [10.0, 10.0]])
    X_test = np.array([[1.0, 1.0], [2.0, 2.0]])
    return X_train, X_test


def test_knn_default(sample_data):
    X_train, X_test = sample_data
    clf = KNN()
    clf.fit(X_train)

    assert clf.decision_scores_ is not None
    assert len(clf.decision_scores_) == X_train.shape[0]

    scores = clf.decision_function(X_test)
    assert scores.shape[0] == X_test.shape[0]


def test_knn_predict(sample_data):
    X_train, X_test = sample_data
    clf = KNN()
    clf.fit(X_train)

    labels = clf.predict(X_test)
    assert labels.shape[0] == X_test.shape[0]
    assert set(labels).issubset({0, 1})


def test_knn_methods(sample_data):
    X_train, _ = sample_data

    for method in ['largest', 'mean', 'median']:
        clf = KNN(method=method)
        clf.fit(X_train)
        assert clf.decision_scores_ is not None


def test_knn_not_fitted(sample_data):
    _, X_test = sample_data
    clf = KNN()

    with pytest.raises(NotFittedError):
        clf.decision_function(X_test)


def test_knn_invalid_method():
    with pytest.raises(ValueError):
        KNN(method='invalid_method')


def test_knn_deprecated_algorithm_warns():
    with pytest.warns(FutureWarning):
        KNN(algorithm='kd_tree')


def test_knn_fit_predict(sample_data):
    X_train, X_test = sample_data
    clf = KNN()
    clf.fit(X_train)

    with pytest.deprecated_call():
        labels = clf.fit_predict(X_test)
        assert labels.shape[0] == X_test.shape[0]