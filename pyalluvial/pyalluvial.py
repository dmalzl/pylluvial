from matplotlib.patches import Polygon
import numpy as np
import pandas as pd
import itertools as it

class PlotItemBase:
    def __init__(self):
        # add some generic values for PlotItems
        self.value = 'some generic value'

class Stratum(PlotItemBase):
    def __init__(self):
        super.__init__()

class Flow(PlotItemBase):
    def __init__(self):
        super.__init__()

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

def to_dataframe(x, y, alluvium, stratum):
    df = pd.DataFrame(
        {
            'x': x,
            'y': y,
            'alluvium': alluvium,
            'stratum': stratum
        }
    )

    return df

def get_lodes(data, x, alluvium, stratum):
    '''
    computes lode widths for each flow between strata of successive groups in x
    returns a nested list of numpy arrays of the form l = list(list(array())), where
    l[i][j] gives the flows computed between groups i and i+1 for stratum j as a 2D array
    of shape n x 2, where n gives the number of flows from stratum j in group i to strata in
    group i+1 (e.g. if stratum in i has flows to three strata in i+1 n = 3). The two columns
    of this array denote the width of the lode as a fraction of stratum j in i (first column)
    or of stratum k in i+1 (second column)

    :param data:        pandas.DataFrame
    :param x:           categorical column on which to group data
    :param alluvium:    column on which to compute flows
    :param stratum:     categorical column on which to group x groups

    :return:            nested list of numpy.ndarrays
    '''

    # groupby lambda expression for shorter code
    groupby = lambda df, key: df.groupby(key, sort = False)

    lodes = []
    for (_, g1), (_, g2) in pairwise(groupby(data, x)):
        flows = []
        for _, g1_strat in groupby(g1, stratum):
            strat_flows = []
            for _, g2_strat in groupby(g2, stratum):
                flow = g2_strat[g2_strat[alluvium].isin(g1_strat[alluvium])]
                strat_flows.append(
                    [len(flow) / len(strat) for strat in [g1_strat, g2_strat]]
                )
            flows.append(
                np.array(strat_flows)
            )
        lodes.append(flows)

    return lodes

def aggregate_data(data, x, alluvium, stratum):
    '''
    computes the strata and lodes for each categorical column in x

    :param data:        pandas.DataFrame containing data in long format (see generate_test_data)
    :param x:           categorical column on which to split the data along the x axis
    :param alluvium:    column from which to compute lode sizes for each stratum
    :param stratum:     column specifying the strata for each column in x

    :return:            list of strata sizes relative to group size with l[i] = relative sizes of strata in group i
                        lode sizes as list of list of arrays with l[i][j] = lodesizes relative to strata in i and i + 1
                        see also function `get_lodes` for more context
    '''

    strata_by_group = [
        [len(strat) / len(group) for j, strat in groupby(group, stratum)] for i, group in groupby(data, x)
    ]

    lodes = get_lodes(
        data,
        x,
        alluvium,
        stratum
    )

    return strata_by_group, lodes

def plot_strata(group_strata, x, colors, ax, gapsize = 5, scale = 100, width = 0.5, alpha = 0.5):
    '''
    plots stratas for a given group

    :param group_strata:    list of relative strata sizes
    :param x:               position of group column on x axis
    :param colors:          iterable containing colors for each of the strata
    :param ax:              matplotlib.Axes object to add the strata patches to
    :param gapsize:         size of gap between each pair of rectangles
    :param scale:           scale on which to plot the strata
    :param width:           width of the plotted rectangles
    :param alpha:           opacity of plotted rectangles

    :return:                None
    '''
    y = 0
    for c, stratum in zip(colors, group_strata):
        height = stratum * scale
        patch = Polygon(
            [
                [x - width, y + height], [x + width, y + height],
                [x - width, y], [x + width, y]
            ],
            color = c,
            alpha = alpha
        )
        ax.add_patch(patch)
        y += height + gapsize