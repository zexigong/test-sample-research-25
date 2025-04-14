import pytest
import torch
import numpy as np
from torch.utils.data import DataLoader
from pyod.devnet import DevNet, DevNetD, DevNetS, DevNetLinear, SupDataset, deviation_loss, load_model_weight_predict

@pytest.fixture
def dummy_data():
    X_train = np.random.rand(100, 20)
    y_train = np.random.randint(0, 2, 100)
    X_test = np.random.rand(30, 20)
    return X_train, y_train, X_test

@pytest.fixture
def dummy_dataloader(dummy_data):
    X_train, y_train, _ = dummy_data
    dataset = SupDataset(X_train, np.where(y_train == 1)[0], np.where(y_train == 0)[0], rng=np.random.RandomState(42))
    dataloader = DataLoader(dataset, batch_size=10, shuffle=True)
    return dataloader

def test_devnet_init():
    devnet = DevNet()
    assert devnet.network_depth == 2
    assert devnet.batch_size == 512
    assert devnet.epochs == 50

def test_devnet_fit(dummy_data):
    X_train, y_train, _ = dummy_data
    devnet = DevNet()
    devnet.fit(X_train, y_train)
    assert hasattr(devnet, 'decision_scores_')
    assert len(devnet.decision_scores_) == X_train.shape[0]

def test_devnet_decision_function(dummy_data):
    X_train, y_train, X_test = dummy_data
    devnet = DevNet()
    devnet.fit(X_train, y_train)
    scores = devnet.decision_function(X_test)
    assert scores.shape[0] == X_test.shape[0]

def test_devnet_d_forward_pass():
    model = DevNetD(input_shape=20)
    input_tensor = torch.rand((10, 20))
    output = model(input_tensor)
    assert output.shape == (10, 1)

def test_devnet_s_forward_pass():
    model = DevNetS(input_shape=20)
    input_tensor = torch.rand((10, 20))
    output = model(input_tensor)
    assert output.shape == (10, 1)

def test_devnet_linear_forward_pass():
    model = DevNetLinear(input_shape=20)
    input_tensor = torch.rand((10, 20))
    output = model(input_tensor)
    assert output.shape == (10, 1)

def test_deviation_loss():
    y_true = torch.tensor([0, 1, 0, 1], dtype=torch.float32)
    y_pred = torch.tensor([0.1, 0.9, 0.2, 0.8], dtype=torch.float32)
    loss = deviation_loss(y_true, y_pred)
    assert loss.item() >= 0

def test_load_model_weight_predict(dummy_data):
    _, _, X_test = dummy_data
    model = DevNetD(input_shape=20)
    scores = load_model_weight_predict(model, X_test)
    assert scores.shape[0] == X_test.shape[0]