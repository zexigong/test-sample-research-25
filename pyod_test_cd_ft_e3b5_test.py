# -*- coding: utf-8 -*-
"""Cook's distance outlier detection (CD)"""

# Author: D Kulik
# License: BSD 2 clause

import os
import sys

sys.path.append(
    os.path.abspath(os.path.join(os.path.dirname("__file__"), "..", "..")))

import unittest
import numpy as np
from numpy.testing import assert_allclose
from sklearn.utils.testing import assert_equal
from sklearn.utils.testing import assert_raises
from sklearn.utils.testing import assert_warns

from pyod.models.cd import CD

class TestCD(unittest.TestCase):
    def setUp(self):
        self.X_train = np.array(
            [[4.4, 2.0, 1.6, 8.3], [5.0, 2.2, 1.7, 8.9],
             [5.2, 2.7, 3.9, 10.2], [5.4, 3.0, 3.2, 12.9],
             [5.8, 3.4, 2.9, 14.3], [5.6, 3.6, 3.4, 14.1],
             [5.6, 3.9, 3.3, 13.9], [5.8, 3.6, 3.0, 13.2],
             [6.0, 3.3, 3.4, 11.9], [5.8, 2.7, 4.1, 13.3],
             [5.0, 2.0, 1.6, 8.3], [5.0, 2.2, 1.7, 8.9],
             [5.2, 2.7, 3.9, 10.2], [5.4, 3.0, 3.2, 12.9],
             [5.8, 3.4, 2.9, 14.3], [5.6, 3.6, 3.4, 14.1],
             [5.6, 3.9, 3.3, 13.9], [5.8, 3.6, 3.0, 13.2],
             [6.0, 3.3, 3.4, 11.9], [5.8, 2.7, 4.1, 13.3]])
        
        self.X_test = np.array(
            [[5.0, 2.2, 1.7, 8.9], [5.2, 2.7, 3.9, 10.2],
             [5.4, 3.0, 3.2, 12.9], [5.8, 3.4, 2.9, 14.3],
             [5.6, 3.6, 3.4, 14.1], [5.6, 3.9, 3.3, 13.9],
             [5.8, 3.6, 3.0, 13.2], [6.0, 3.3, 3.4, 11.9],
             [5.8, 2.7, 4.1, 13.3], [5.0, 2.0, 1.6, 8.3],
             [5.0, 2.2, 1.7, 8.9], [5.2, 2.7, 3.9, 10.2],
             [5.4, 3.0, 3.2, 12.9], [5.8, 3.4, 2.9, 14.3],
             [5.6, 3.6, 3.4, 14.1], [5.6, 3.9, 3.3, 13.9],
             [5.8, 3.6, 3.0, 13.2], [6.0, 3.3, 3.4, 11.9],
             [5.8, 2.7, 4.1, 13.3], [5.0, 2.0, 1.6, 8.3]])

        self.contamination = 0.25
        self.detector = CD(contamination=self.contamination)
        self.detector.fit(self.X_train)

    def test_parameters(self):
        """Test the parameter settings."""

        assert_raises(ValueError, CD, contamination=0.6)
        assert_raises(ValueError, CD, contamination=-0.1)

    def test_fit(self):
        """Test fit() function"""

        assert_equal(self.detector.decision_scores_.shape[0],
                     self.X_train.shape[0])

        # check threshold
        threshold = np.percentile(self.detector.decision_scores_,
                                  100 * (1 - self.contamination))
        assert_equal(round(self.detector.threshold_, 4), round(threshold, 4))

        # check decision_scores
        assert_equal(self.detector.decision_scores_.shape[0],
                     self.X_train.shape[0])

        # check labels
        assert_equal(self.detector.labels_.shape[0], self.X_train.shape[0])

    def test_predict_score(self):
        """Test predict_score() function"""

        pred_score = self.detector.decision_function(self.X_test)
        assert_equal(pred_score.shape[0], self.X_test.shape[0])

        # check if the outlier scores are the same
        assert_allclose(self.detector.decision_function(self.X_train),
                        self.detector.decision_scores_)

    def test_predict(self):
        """Test predict() function"""

        pred = self.detector.predict(self.X_test)
        assert_equal(pred.shape[0], self.X_test.shape[0])

    def test_predict_proba(self):
        """Test predict_proba() function"""

        pred_proba = self.detector.predict_proba(self.X_test)
        assert_equal(pred_proba.shape[0], self.X_test.shape[0])
        assert_equal(pred_proba.shape[1], 2)
        
        pred = self.detector.predict(self.X_test)
        assert_allclose(pred, pred_proba[:, 1] > 0.5)

    def test_predict_rank(self):
        """Test predict_rank() function"""

        pred_rank = self.detector._predict_rank(self.X_test)
        assert_equal(pred_rank.shape[0], self.X_test.shape[0])
        assert_equal(pred_rank.min(), 0)
        assert_equal(pred_rank.max(), self.X_train.shape[0] - 1)

        pred_rank_normalized = self.detector._predict_rank(self.X_test,
                                                           normalized=True)
        assert_equal(pred_rank_normalized.shape[0], self.X_test.shape[0])
        assert_equal(pred_rank_normalized.min(), 0)
        assert_equal(pred_rank_normalized.max(), 1)

if __name__ == '__main__':
    unittest.main()