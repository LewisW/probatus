import numpy as np
import pandas as pd
import numbers
from pyrisk.stat_tests import DistributionStatistics, ks, psi, AutoDist


def test_distribution_statistics_psi():
    d1 = np.histogram(np.random.normal(size=1000), 10)[0]
    d2 = np.histogram(np.random.weibull(1, size=1000) - 1, 10)[0]
    myTest = DistributionStatistics('psi', 'SimpleBucketer', bin_count=10)
    assert not myTest.fitted
    res = myTest.fit(d1, d2)
    assert myTest.fitted
    assert isinstance(res, numbers.Number)


def test_distribution_statistics_tuple_output():
    d1 = np.histogram(np.random.normal(size=1000), 10)[0]
    d2 = np.histogram(np.random.weibull(1, size=1000) - 1, 10)[0]
    myTest = DistributionStatistics('ks', 'SimpleBucketer', bin_count=10)
    assert not myTest.fitted
    res = myTest.fit(d1, d2)
    assert myTest.fitted
    assert isinstance(res, tuple)


def test_distribution_statistics_ks_no_binning():
    d1 = np.histogram(np.random.normal(size=1000), 10)[0]
    d2 = np.histogram(np.random.weibull(1, size=1000) - 1, 10)[0]
    myTest = DistributionStatistics('ks', binning_strategy=None)
    assert not myTest.fitted
    res = myTest.fit(d1, d2)
    assert myTest.fitted
    assert isinstance(res, tuple)


def test_distribution_statistics_attributes_psi():
    a = np.random.normal(size=1000)
    b = np.random.normal(size=1000)
    d1 = np.histogram(a, 10)[0]
    d2 = np.histogram(b, 10)[0]
    myTest = DistributionStatistics('psi', binning_strategy=None)
    _ = myTest.fit(d1, d2, verbose=False)
    psi_value = psi(d1, d2, verbose=False)
    assert myTest.statistic == psi_value


def test_distribution_statistics_attributes_ks():
    d1 = np.histogram(np.random.normal(size=1000), 10)[0]
    d2 = np.histogram(np.random.normal(size=1000), 10)[0]
    myTest = DistributionStatistics('ks', binning_strategy=None)
    _ = myTest.fit(d1, d2, verbose=False)
    ks_value, p_value = ks(d1, d2)
    assert myTest.statistic == ks_value


def test_distribution_statistics_autodist_base():
    nr_features = 2
    size = 1000
    np.random.seed(0)
    df1 = pd.DataFrame(np.random.normal(size=(size, nr_features)), columns=[f'feat_{x}' for x in range(nr_features)])
    df2 = pd.DataFrame(np.random.normal(size=(size, nr_features)), columns=[f'feat_{x}' for x in range(nr_features)])
    features = df1.columns
    myAutoDist = AutoDist(statistical_tests='all', binning_strategies='all', bin_count=[10, 20])
    assert not myAutoDist.fitted
    res = myAutoDist.fit(df1, df2, columns=features)
    assert myAutoDist.fitted
    pd.testing.assert_frame_equal(res, myAutoDist.result)
    assert isinstance(res, pd.DataFrame)
    assert res['column'].values.tolist() == features.to_list()
    assert len(myAutoDist.statistical_tests) * len(myAutoDist.binning_strategies) * len(
        myAutoDist.bin_count) * 2 + 1 == res.columns.size

    dist = DistributionStatistics(statistical_test='ks', binning_strategy='simplebucketer', bin_count=10)
    dist.fit(df1['feat_0'], df2['feat_0'])
    assert dist.p_value == res.loc[res['column'] == 'feat_0', 'p_value_KS_simplebucketer_10'][0]
    assert dist.statistic == res.loc[res['column'] == 'feat_0', 'statistic_KS_simplebucketer_10'][0]

    dist = DistributionStatistics(statistical_test='ks', binning_strategy=None, bin_count=10)
    dist.fit(df1['feat_0'], df2['feat_0'])
    assert dist.p_value == res.loc[res['column'] == 'feat_0', 'p_value_KS_no_bucketing_10'][0]
    assert dist.statistic == res.loc[res['column'] == 'feat_0', 'statistic_KS_no_bucketing_10'][0]