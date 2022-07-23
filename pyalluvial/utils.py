import numpy as np
import itertools as it
import pandas as pd
import seaborn as sns

class Normalizer:
    def __init__(self, vmin, vmax):
        self.vmin = vmin
        self.vmax = vmax

    def __call__(self, val, scale = None):
        norm = (val - self.vmin) / (self.vmax - self.vmin)
        return norm * scale if scale else norm

def get_color_list(data, x, stratum, sns_palette = 'husl'):
    '''
    returns a list of colors as expected by alluvial

    :param data:    data to plot in wide format

    :return:        list of lists of colors
    '''
    color_list_lengths = [group[stratum].nunique() for _, group in groupby(data, x)]
    palette = sns.color_palette(
        sns_palette,
        max(color_list_lengths)
    )
    return [[palette[i] for i in range(n)] for n in color_list_lengths]

def pairwise(iterable):
    '''
    returns successive overlapping pairs taken from the input iterable.
    taken from itertools since this is only available for python>=3.10

    :param iterable:    any iterable container
    :return:            successive overlapping pairs
    '''

    a, b = it.tee(iterable)
    next(b, None)
    return zip(a, b)

def generate_probabilities(n):
    '''
    generates an array of n probabilities with the constraint of sum(probabilities) = 1
    :param n:   number of probabilities in the array
    :return:    list of floats
    '''

    all_nonzero = False
    while not all_nonzero:
        probabilities = [np.random.randint(0, 51)]
        high = 101 - probabilities[0]
        for i in range(n - 2):
            p = np.random.randint(0, high)
            probabilities.append(p)
            high -= p

        probabilities.append(
            100 - sum(probabilities)
        )

        all_nonzero = all(probabilities)

    return [p / 100 for p in probabilities]

def to_dataframe(x, alluvium, stratum):
    df = pd.DataFrame(
        {
            'x': x,
            'alluvium': alluvium,
            'stratum': stratum
        }
    )

    return df

# groupby lambda expression for shorter code
groupby = lambda df, key: df.groupby(key, sort = False)

def reset_strata(strata):
    '''
    resets the flow position tracking of all given Stratum objects

    :param strata:  list of Stratum object to reset

    :return:        None
    '''
    for stratum in strata:
        stratum.reset_lode_position()

def generate_test_data():
    '''
    generates test data for the alluvial plotter

    :return: pandas.DataFrame
    '''

    nodenames = list(range(100)) * 4
    timepoint = [f't{i}' for i in range(4) for j in range(100)]
    probabilities = [generate_probabilities(i) for i in [3, 5, 4, 6]]
    modules = np.concatenate(
        [np.random.choice(range(1, len(p) + 1), size = 100, p = p, replace = True) for p in probabilities]
    )
    df = pd.DataFrame(
        [[a, b, c] for a, b, c in zip(nodenames, timepoint, modules)],
        columns = [
            'nodename',
            'timepoint',
            'module'
        ]
    )
    return df