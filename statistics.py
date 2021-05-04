import numpy as np
import pandas as pd

from data_analysis import get_multi_experiment_data
import matplotlib.pyplot as plt
from scipy import stats


def two_sample_t_test(Y1, sigma1, N1, Y2, sigma2, N2):
    """two sample t test to test if Y1 and Y2 are equal while considerign the 
    sample sizes and standard deviations

    The null hypothesis is Y1=Y1
    source:
    https://www.itl.nist.gov/div898/handbook/eda/section3/eda353.htm
    Args:
        Y1 (float): sample mean 
        sigma1 (float): sample standard deviation 
        N1 (float): sample size
        Y2 (float): sample mean 
        sigma2 (float): sample standard deviation
        N2 (float): sample size
    """

    T = (Y1-Y2)/np.sqrt(sigma1**2/N1+sigma2**2/N2)

    temp = (sigma1**2/N1+sigma2**2/N2)**2
    temp1 = (sigma1**2/N1)**2/(N1-1)
    temp2 = (sigma2**2/N2)**2/(N2-1)

    v = temp/(temp1+temp2)

    print(T)
    print(v)
    t = stats.ttest_ind_from_stats(
        mean1=Y1,
        std1=sigma1,
        nobs1=N1,
        mean2=Y2,
        std2=sigma2,
        nobs2=N2
    )
    print(t)


def two_sample_t_test_main():
    mean1 = 2.54
    std1 = np.sqrt(4.4482)
    n1 = 100
    mean2 = 4.09
    std2 = 4.56
    n2 = 50
    two_sample_t_test(Y1=mean1,
                      sigma1=std1,
                      N1=n1,
                      Y2=mean2,
                      sigma2=std2,
                      N2=n2)


def outlier_remove_main():
    date_exp_num_layer_list = (("20201001", 1, [(0, 8), (9, 17), (18, 26)]),
                               ("20200918", 2, [(0, 8), (9, 17), (18, 25)]),
                               ("20200917", 2, [(0, 8), (9, 17), (18, 26)]),
                               ("20200918", 1, [(0, 8), ]))
    # date_exp_num_layer_list = (("20200917", 2, [(0, 8), (9, 17), (18, 26)]),)

    norm_length = 1500  # mm
    range_percentage = 0.05  # 5% .5
    error_list, pairs, vive = get_multi_experiment_data(
        date_exp_num_layer_list=date_exp_num_layer_list,
        norm_length=norm_length,
        range_percentage=range_percentage
    )
    # David-Heartly Test
    # https://de.wikipedia.org/wiki/David-Hartley-Pearson-Test
    sorted_error = sorted(error_list)

    min = sorted_error[0]
    counter = 0
    updated_list = sorted_error[:]
    # while True:
    #     top_val = updated_list[-1]
    #     mean_updated = np.mean(updated_list)
    #     Res = top_val-min
    #     print(Res)
    #     s = np.sqrt(sum((updated_list-mean_updated)**2)/len(updated_list))
    #     T = Res/s
    #     print(T)
    #     if T < 5.25:
    #         break
    #     counter += 1
    #     updated_list = sorted_error[:-counter]
    # print(counter)
    # print(np.mean(sorted_error[:-counter]))
    # print(np.std(sorted_error[:-counter], ddof=1))
    # David Heartly wirft keine raus
    # Grubbs Test
    # https://en.wikipedia.org/wiki/Grubbs%27s_test
    from outliers import smirnov_grubbs as grubbs
    t = grubbs.max_test_outliers(sorted_error, alpha=0.01)
    print(t)
    ind = grubbs.max_test_indices(sorted_error, alpha=0.01)
    print(ind)
    print(np.mean(sorted_error[:-6]))
    print(np.std(sorted_error[:-6], ddof=1))
    # Grubbs wirft raus (bei alpha=0.01 genau die ich selber rausgeworfen hätte)


def normality_check_main():
    date_exp_num_layer_list = (("20201001", 1, [(0, 8), (9, 17), (18, 26)]),
                               ("20200918", 2, [(0, 8), (9, 17), (18, 25)]),
                               ("20200917", 2, [(0, 8), (9, 17), (18, 26)]),
                               ("20200918", 1, [(0, 8), ]))
    norm_length = 1500  # mm
    range_percentage = 0.05  # 5% .5
    error_list, pairs, vive = get_multi_experiment_data(
        date_exp_num_layer_list=date_exp_num_layer_list,
        norm_length=norm_length,
        range_percentage=range_percentage
    )
    my_data = pd.Series(error_list)
    # my_data.plot(kind='box')
    z = np.abs(stats.zscore(my_data))
    print(z)
    # mydata_outlier = my_data[np.where(z < 2)]
    bubu = np.array(error_list)
    bubu = bubu[np.where(z < 3)]
    my_data_outlier = pd.Series(bubu)
    my_data_outlier.plot(kind="box")
    print(my_data_outlier)
    # my_data = pd.Series([1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 8, 6, 4, 2])
    # my_data.plot(kind='box')
    plt.show()


def two_sample_welch_test_main():
    exp_1 = (("20200917", 2, [(0, 8), (9, 17), (18, 26)]),)
    exp_2 = (("20200918", 2, [(0, 8), (9, 17), (18, 25)]),)
    exp_3 = (("20201001", 1, [(0, 8), (9, 17), (18, 26)]),)

    norm_length = 1500  # mm
    range_percentage = 0.05  # 5% .5
    error_list_1, _, _ = get_multi_experiment_data(
        date_exp_num_layer_list=exp_1,
        norm_length=norm_length,
        range_percentage=range_percentage
    )
    error_list_2, _, _ = get_multi_experiment_data(
        date_exp_num_layer_list=exp_2,
        norm_length=norm_length,
        range_percentage=range_percentage
    )
    from scipy.stats import ttest_ind
    error_list_1 = [i for i in error_list_1 if (i < 30)]
    print(stats.describe(error_list_1))
    print(stats.describe(error_list_2))
    t = stats.ttest_ind(error_list_1, error_list_2, equal_var=False)
    print(t)
    print(stats.normaltest(error_list_1))
    print(stats.normaltest(error_list_2))
    print(stats.shapiro(error_list_2))
    plt.hist(error_list_2)
    plt.show()


if __name__ == "__main__":
    # normality_check_main()
    # two_sample_welch_test_main()
    # two_sample_t_test_main()
    outlier_remove_main()
