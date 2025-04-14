# test_dif.py

import pytest
import numpy as np
from pyod.models.dif import DIF
from sklearn.datasets import make_classification

# Check if torch is available
torch_available = False
try:
    import torch
    torch_available = True
except ImportError:
    pass


@pytest.mark.skipif(not torch_available, reason="Torch is not available")
def test_dif_initialization():
    # Test default initialization
    model = DIF()
    assert model.batch_size == 1000
    assert model.representation_dim == 20
    assert model.hidden_neurons == [500, 100]
    assert model.hidden_activation == 'tanh'
    assert model.skip_connection is False
    assert model.n_ensemble == 50
    assert model.n_estimators == 6
    assert model.max_samples == 256
    assert model.contamination == 0.1
    assert model.random_state is None
    assert model.device is not None


@pytest.mark.skipif(not torch_available, reason="Torch is not available")
def test_dif_fit_predict():
    # Generate a toy dataset
    X, _ = make_classification(n_samples=1000, n_features=20, n_informative=2,
                               n_redundant=10, random_state=42)

    model = DIF()
    model.fit(X)

    # Test decision function
    scores = model.decision_function(X)
    assert scores.shape[0] == X.shape[0]

    # Test predict
    predictions = model.predict(X)
    assert predictions.shape[0] == X.shape[0]
    assert set(predictions).issubset({0, 1})


@pytest.mark.skipif(not torch_available, reason="Torch is not available")
def test_dif_custom_params():
    model = DIF(batch_size=500, representation_dim=10, hidden_neurons=[128, 64],
                hidden_activation='relu', skip_connection=True, n_ensemble=10,
                n_estimators=5, max_samples=128, contamination=0.2, random_state=42)

    assert model.batch_size == 500
    assert model.representation_dim == 10
    assert model.hidden_neurons == [128, 64]
    assert model.hidden_activation == 'relu'
    assert model.skip_connection is True
    assert model.n_ensemble == 10
    assert model.n_estimators == 5
    assert model.max_samples == 128
    assert model.contamination == 0.2
    assert model.random_state == 42


@pytest.mark.skipif(not torch_available, reason="Torch is not available")
def test_dif_prediction_confidence():
    X, _ = make_classification(n_samples=1000, n_features=20, n_informative=2,
                               n_redundant=10, random_state=42)

    model = DIF()
    model.fit(X)

    confidence = model.predict_confidence(X)
    assert confidence.shape[0] == X.shape[0]
    assert np.all((confidence >= 0) & (confidence <= 1))


@pytest.mark.skipif(not torch_available, reason="Torch is not available")
def test_dif_decision_function_exceptions():
    X, _ = make_classification(n_samples=1000, n_features=20, n_informative=2,
                               n_redundant=10, random_state=42)

    model = DIF()

    with pytest.raises(ValueError):
        model.decision_function(X)