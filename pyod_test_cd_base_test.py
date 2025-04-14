import pytest
import numpy as np
from sklearn.linear_model import LinearRegression
from pyod.cd import CD
from sklearn.utils.validation import NotFittedError

def test_cd_initialization():
    detector = CD()
    assert detector.contamination == 0.1
    assert isinstance(detector.model, LinearRegression)

def test_cd_fit():
    X = np.array([[1, 2], [2, 3], [3, 4], [4, 5]])
    detector = CD()
    detector.fit(X)
    assert hasattr(detector, 'decision_scores_')
    assert hasattr(detector, 'threshold_')
    assert hasattr(detector, 'labels_')

def test_cd_fit_invalid_input():
    X = np.array([1, 2, 3, 4])  # Not a 2D array
    detector = CD()
    with pytest.raises(ValueError):
        detector.fit(X)

def test_cd_decision_function():
    X_train = np.array([[1, 2], [2, 3], [3, 4], [4, 5]])
    X_test = np.array([[5, 6], [6, 7], [7, 8]])
    detector = CD()
    detector.fit(X_train)
    scores = detector.decision_function(X_test)
    assert scores.shape[0] == X_test.shape[0]

def test_cd_decision_function_not_fitted():
    X = np.array([[1, 2], [2, 3]])
    detector = CD()
    with pytest.raises(NotFittedError):
        detector.decision_function(X)

def test_cd_predict():
    X_train = np.array([[1, 2], [2, 3], [3, 4], [4, 5]])
    X_test = np.array([[5, 6], [6, 7], [7, 8]])
    detector = CD()
    detector.fit(X_train)
    predictions = detector.predict(X_test)
    assert predictions.shape[0] == X_test.shape[0]
    assert set(predictions).issubset({0, 1})

def test_cd_predict_proba():
    X_train = np.array([[1, 2], [2, 3], [3, 4], [4, 5]])
    X_test = np.array([[5, 6], [6, 7], [7, 8]])
    detector = CD()
    detector.fit(X_train)
    proba = detector.predict_proba(X_test)
    assert proba.shape == (X_test.shape[0], 2)
    assert np.all(proba >= 0) and np.all(proba <= 1)

def test_cd_set_params():
    detector = CD()
    detector.set_params(contamination=0.2)
    assert detector.contamination == 0.2

def test_cd_get_params():
    detector = CD()
    params = detector.get_params()
    assert 'contamination' in params
    assert 'model' in params

def test_cd_fit_predict():
    X = np.array([[1, 2], [2, 3], [3, 4], [4, 5]])
    detector = CD()
    with pytest.warns(DeprecationWarning):
        labels = detector.fit_predict(X)
    assert labels.shape[0] == X.shape[0]
    assert set(labels).issubset({0, 1})

if __name__ == "__main__":
    pytest.main()