import numpy as np


'''
Conclusion:
np.std returns the population standard deviation,
given by the equation

$$
    \sigma = \sqrt{ \frac{ \Sigma (x_i - \bar{x} )^2 } { N } }
$$

(As opposed to the sample standard deviation)
'''


def my_std(data: [float]) -> float:
    mean: float = sum(data) / len(data)

    sum_of_squared_differences: float = sum(
        [pow(item - mean, 2) for item in data])

    out: float = np.sqrt(sum_of_squared_differences / (len(data)))

    return out


for i in range(100):
    random_arr: [float] = np.random.rand(100)
    random_arr = [item * 100 for item in random_arr]

    mine: float = my_std(random_arr)
    theirs: float = np.std(random_arr)

    mine = round(mine, 10)
    theirs = round(theirs, 10)

    if mine != theirs:
        print('Trial', i, '\tManual std:', mine, '\tNP std:', theirs)
    else:
        print('Trial', i, '\tEqual to 10 decimal places')
