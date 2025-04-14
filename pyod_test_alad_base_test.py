# test_alad.py
import pytest
import numpy as np
import torch
from pyod.models.alad import ALAD

@pytest.fixture
def sample_data():
    np.random.seed(42)
    X_inliers = np.random.normal(loc=0, scale=1, size=(100, 2))
    X_outliers = np.random.normal(loc=5, scale=1, size=(10, 2))
    X = np.vstack((X_inliers, X_outliers))
    return X

@pytest.fixture
def alad_detector():
    return ALAD(epochs=10, batch_size=10, contamination=0.1)

def test_fit(sample_data, alad_detector):
    alad_detector.fit(sample_data)
    assert hasattr(alad_detector, 'decision_scores_'), "Model not fitted properly"
    assert hasattr(alad_detector, 'threshold_'), "Model not fitted properly"
    assert hasattr(alad_detector, 'labels_'), "Model not fitted properly"

def test_decision_function(sample_data, alad_detector):
    alad_detector.fit(sample_data)
    scores = alad_detector.decision_function(sample_data)
    assert scores.shape[0] == sample_data.shape[0], "Decision function output shape mismatch"
    assert np.all(scores >= 0), "Scores contain negative values"

def test_predict(sample_data, alad_detector):
    alad_detector.fit(sample_data)
    predictions = alad_detector.predict(sample_data)
    assert predictions.shape[0] == sample_data.shape[0], "Prediction output shape mismatch"
    assert np.all(np.isin(predictions, [0, 1])), "Predictions contain invalid labels"

def test_predict_with_confidence(sample_data, alad_detector):
    alad_detector.fit(sample_data)
    predictions, confidence = alad_detector.predict(sample_data, return_confidence=True)
    assert predictions.shape[0] == sample_data.shape[0], "Prediction output shape mismatch"
    assert confidence.shape[0] == sample_data.shape[0], "Confidence output shape mismatch"
    assert np.all(np.isin(predictions, [0, 1])), "Predictions contain invalid labels"
    assert np.all((confidence >= 0) & (confidence <= 1)), "Confidence values out of bounds"

def test_get_outlier_scores(sample_data, alad_detector):
    alad_detector.fit(sample_data)
    scores = alad_detector.get_outlier_scores(sample_data)
    assert scores.shape[0] == sample_data.shape[0], "Outlier scores output shape mismatch"
    assert np.all(scores >= 0), "Scores contain negative values"

def test_train_more(sample_data, alad_detector):
    alad_detector.fit(sample_data)
    initial_scores = alad_detector.decision_scores_
    alad_detector.train_more(sample_data, epochs=5)
    new_scores = alad_detector.decision_scores_
    assert not np.array_equal(initial_scores, new_scores), "Training more did not change scores"

def test_invalid_device(sample_data):
    with pytest.raises(ValueError):
        ALAD(device='invalid_device')