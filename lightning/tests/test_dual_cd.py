import numpy as np
import scipy.sparse as sp

from sklearn.metrics.pairwise import linear_kernel
from sklearn.metrics import auc_score
from sklearn.datasets.samples_generator import make_classification

from sklearn.utils.testing import assert_equal
from sklearn.utils.testing import assert_greater
from sklearn.utils.testing import assert_array_almost_equal

from lightning.dual_cd import LinearSVC
from lightning.dual_cd_fast import sparse_dot
from lightning.dataset_fast import get_dataset

bin_dense, bin_target = make_classification(n_samples=200, n_features=100,
                                            n_informative=5,
                                            n_classes=2, random_state=0)
bin_csr = sp.csr_matrix(bin_dense)

mult_dense, mult_target = make_classification(n_samples=300, n_features=100,
                                              n_informative=5,
                                              n_classes=3, random_state=0)
mult_sparse = sp.csr_matrix(mult_dense)


def test_sparse_dot():
    for data in (bin_dense, bin_csr):
        K = linear_kernel(data)
        K2 = np.zeros_like(K)
        ds = get_dataset(data)

        for i in xrange(data.shape[0]):
            for j in xrange(i, data.shape[0]):
                K2[i, j] = sparse_dot(ds, i, j)
                K2[j, i] = K[i, j]

    assert_array_almost_equal(K, K2)


def test_fit_linear_binary():
    for data in (bin_dense, bin_csr):
        for loss in ("l1", "l2"):
            clf = LinearSVC(loss=loss, random_state=0, max_iter=10)
            clf.fit(data, bin_target)
            assert_equal(clf.score(data, bin_target), 1.0)
            y_pred = clf.decision_function(data).ravel()


def test_fit_linear_binary_auc():
    for data in (bin_dense, bin_csr):
        for loss in ("l1", "l2"):
            clf = LinearSVC(loss=loss, criterion="auc", random_state=0,
                            max_iter=25)
            clf.fit(data, bin_target)
            assert_equal(clf.score(data, bin_target), 1.0)


def test_fit_linear_multi():
    for data in (mult_dense, mult_sparse):
        clf = LinearSVC(random_state=0)
        clf.fit(data, mult_target)
        y_pred = clf.predict(data)
        acc = np.mean(y_pred == mult_target)
        assert_greater(acc, 0.85)


def test_warm_start():
    clf = LinearSVC(warm_start=True, loss="l1", random_state=0, max_iter=100)
    for C in (0.1, 0.2):
        clf.C = C

        clf.fit(bin_dense, bin_target)
        acc = clf.score(bin_dense, bin_target)
        assert_greater(acc, 0.99)

