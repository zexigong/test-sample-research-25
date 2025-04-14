# -*- coding: utf-8 -*-
"""
Unit test for DevNet
"""
# Author: Sihan Chen <schen976@usc.edu>
# License: BSD 2 clause

import unittest

import numpy as np
from sklearn.metrics import roc_auc_score
from sklearn.model_selection import train_test_split

from pyod.models.devnet import DevNet

class TestDevnet(unittest.TestCase):
    def setUp(self):
        self.X = np.loadtxt('pyod/test_devnet/arrhythmia.txt')
        self.y = np.loadtxt('pyod/test_devnet/arrhythmia_label.txt')
        self.X_train, self.X_test, self.y_train, self.y_test = train_test_split(
            self.X, self.y, test_size=0.25, random_state=42)

    def test_devnet(self):
        devnet = DevNet()
        devnet.fit(self.X_train, self.y_train)
        y_pred = devnet.predict(self.X_test)
        auc = roc_auc_score(self.y_test, y_pred)

        assert auc >= 0.6, f"AUC is lower than expected: {auc}"

if __name__ == "__main__":
    unittest.main()