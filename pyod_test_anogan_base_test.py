import pytest
import numpy as np
import torch
from pyod.models.anogan import AnoGAN

@pytest.fixture(scope='module')
def sample_data():
    np.random.seed(42)
    X_inliers = np.random.normal(0, 0.5, (200, 5))
    X_outliers = np.random.normal(3, 0.5, (20, 5))
    X = np.vstack([X_inliers, X_outliers])
    y = np.array([0] * 200 + [1] * 20)
    return X, y

@pytest.fixture(scope='module')
def anogan_detector():
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    return AnoGAN(epochs=10, epochs_query=5, device=device)

def test_anogan_fit(sample_data, anogan_detector):
    X, _ = sample_data
    anogan_detector.fit(X)
    assert hasattr(anogan_detector, 'decision_scores_')
    assert hasattr(anogan_detector, 'threshold_')
    assert hasattr(anogan_detector, 'labels_')

def test_anogan_predict(sample_data, anogan_detector):
    X, y = sample_data
    anogan_detector.fit(X)
    predictions = anogan_detector.predict(X)
    assert predictions.shape == y.shape

def test_anogan_predict_proba(sample_data, anogan_detector):
    X, _ = sample_data
    anogan_detector.fit(X)
    probs = anogan_detector.predict_proba(X)
    assert probs.shape[0] == X.shape[0]
    assert probs.shape[1] == 2
    assert np.all(probs >= 0) and np.all(probs <= 1)

def test_anogan_decision_function(sample_data, anogan_detector):
    X, _ = sample_data
    anogan_detector.fit(X)
    scores = anogan_detector.decision_function(X)
    assert scores.shape[0] == X.shape[0]
    assert scores.ndim == 1

def test_anogan_fit_predict(sample_data, anogan_detector):
    X, y = sample_data
    predictions = anogan_detector.fit_predict(X)
    assert predictions.shape == y.shape

def test_anogan_invalid_params():
    with pytest.raises(ValueError):
        AnoGAN(dropout_rate=1.5)
    with pytest.raises(ValueError):
        AnoGAN(contamination=-0.1)