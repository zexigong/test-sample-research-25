import pytest
import numpy as np
from pyod.models.gmm import GMM
from sklearn.exceptions import NotFittedError

@pytest.fixture
def data():
    X_inliers = np.random.normal(0, 1, (100, 2))
    X_outliers = np.random.normal(0, 1, (20, 2)) + 5
    X = np.concatenate([X_inliers, X_outliers], axis=0)
    return X

@pytest.fixture
def gmm_detector():
    return GMM(n_components=2, contamination=0.1)

def test_gmm_init():
    detector = GMM()
    assert detector.n_components == 1
    assert detector.covariance_type == "full"
    assert detector.tol == 1e-3
    assert detector.reg_covar == 1e-6
    assert detector.max_iter == 100
    assert detector.n_init == 1
    assert detector.init_params == "kmeans"
    assert detector.contamination == 0.1

def test_fit(gmm_detector, data):
    X = data
    gmm_detector.fit(X)
    assert hasattr(gmm_detector, "decision_scores_")
    assert hasattr(gmm_detector, "detector_")

def test_fit_predict(gmm_detector, data):
    X = data
    gmm_detector.fit(X)
    labels = gmm_detector.predict(X)
    assert labels.shape[0] == X.shape[0]
    assert set(labels).issubset({0, 1})

def test_decision_function(gmm_detector, data):
    X = data
    gmm_detector.fit(X)
    scores = gmm_detector.decision_function(X)
    assert scores.shape[0] == X.shape[0]
    assert np.all(scores >= 0)

def test_predict_without_fit(gmm_detector, data):
    X = data
    with pytest.raises(NotFittedError):
        gmm_detector.predict(X)

def test_attributes(gmm_detector, data):
    X = data
    gmm_detector.fit(X)
    assert gmm_detector.weights_.shape[0] == gmm_detector.n_components
    assert gmm_detector.means_.shape[0] == gmm_detector.n_components
    assert gmm_detector.covariances_.shape[0] == gmm_detector.n_components
    assert gmm_detector.precisions_.shape[0] == gmm_detector.n_components
    assert gmm_detector.precisions_cholesky_.shape[0] == gmm_detector.n_components
    assert isinstance(gmm_detector.converged_, bool)
    assert isinstance(gmm_detector.n_iter_, int)
    assert isinstance(gmm_detector.lower_bound_, float)