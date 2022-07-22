import matplotlib.pyplot as plt
from matplotlib.patches import Polygon
import numpy as np
import pandas as pd
import itertools as it

class Normalizer:
    def __init__(self, vmin, vmax):
        self.vmin = vmin
        self.vmax = vmax

    def __call__(self, val, scale = None):
        norm = (val - self.vmin) / (self.vmax - self.vmin)
        return norm * scale if scale else norm

class Stratum:
    def __init__(self, relative_height, x = 0, y = 0):
        self.x = x
        self.y = y
        self.relative_height = relative_height
        self.lode_position = 0
        self.height = 0
        self.width = 0
        self.color = None

    def __repr__(self):
        return f'Stratum(h = {self.height:.02f}, rh = {self.relative_height:.02f}, y = {self.y:.02f})'

    def set_width(self, width):
        self.width = width

    def set_color(self, color):
        self.color = color

    def reset_lode_position(self):
        self.lode_position = self.height

    def get_left_bound(self, gap):
        return self.x - self.width / 2 - gap

    def get_right_bound(self, gap):
        return self.x + self.width / 2 + gap

    def get_flow_ycoords(self, relative_flow_width):
        if not self.lode_position:
            self.lode_position = self.height

        top = self.lode_position + self.y
        bottom = top - self.height * relative_flow_width
        self.lode_position = bottom

        return top, bottom

    def set_xy(self, x, y):
        self.x = x
        self.y = y

    def set_height(self, scale, norm = None):
        height = self.relative_height * scale
        self.height = norm(height, scale) if norm else height

    def get_patch(self, width, color, alpha):
        if not self.color:
            self.color = color

        top_left = [self.x - width / 2, self.y + self.height]
        top_right = [self.x + width / 2, self.y + self.height]
        bottom_left = [self.x - width / 2, self.y]
        bottom_right = [self.x + width / 2, self.y]
        patch = Polygon(
            [
                top_left, top_right,
                bottom_right, bottom_left
            ],
            color = color,
            alpha = alpha,
            edgecolor = None,
            linewidth = None
        )
        return patch

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

# groupby lambda expression for shorter code
groupby = lambda df, key: df.groupby(key, sort = False)

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

    strata_by_group = []
    for _, group in groupby(data, x):
        strata = [
            Stratum(len(strat) / len(group), 0, 0, ) for _, strat in groupby(group, stratum)
        ]
        strata_by_group.append(strata)

    lodes = get_lodes(
        data,
        x,
        alluvium,
        stratum
    )

    return strata_by_group, lodes

def plot_group_strata(group_strata, x, colors, ax, gapsize = 1, scale = 100, width = 0.5, alpha = 0.5):
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
    norm = Normalizer(y, scale + gapsize * (len(group_strata) - 1))
    # group_strata[::-1] is necessary to comply to top to bottom order of strata
    for c, stratum in zip(colors, group_strata[::-1]):
        stratum.set_height(scale, norm)
        stratum.set_width(width)
        stratum.set_xy(x, y)
        ax.add_patch(
            stratum.get_patch(width, c, alpha)
        )
        y += stratum.height + gapsize

def plot_strata(strata, strat_colors, ax, scale = 100):
    x = 0.25
    for group_strata, colors in zip(strata, strat_colors):
        plot_group_strata(
            group_strata,
            x,
            colors,
            ax,
            scale = scale
        )
        x += scale / 4

    ax.set_xlim(0, x - scale / 4 + 0.25)
    ax.set_ylim(0, scale)

def get_flow_path(y1, y2, x1, x2, resolution = 50):
    # partly taken from https://github.com/vinsburg/alluvial_diagram/blob/master/alluvial.py
    y = np.array([0, 0.15, 0.5, 0.85, 1])
    y = y * (y2 - y1) + y1
    x = np.linspace(x1, x2, len(y))
    z = np.polyfit(x, y, 4)
    f = np.poly1d(z)

    xs = np.linspace(x[0], x[-1], resolution)
    ys = f(xs)

    return xs, ys

def make_flow_polygon(g1_strat, g2_strat, g1_rh, g2_rh, color, alpha = 0.5):
    y1_bottom, y1_top = g1_strat.get_flow_ycoords(g1_rh)
    y2_bottom, y2_top = g2_strat.get_flow_ycoords(g2_rh)
    print(y1_bottom, y1_top, y2_bottom, y2_top)
    x1 = g1_strat.get_right_bound(1)
    x2 = g2_strat.get_left_bound(1)
    x_bottom, y_bottom = get_flow_path(y1_bottom, y2_bottom, x1, x2)
    x_top, y_top = get_flow_path(y1_top, y2_top, x1, x2)
    x = np.concatenate([x_top, x_bottom[::-1]])
    y = np.concatenate([y_top, y_bottom[::-1]])
    flow_polygon = Polygon(
        np.array([x, y]).T,
        color = color,
        alpha = alpha,
        edgecolor = None
    )

    return flow_polygon

def reset_strata(strata):
    for stratum in strata:
        stratum.reset_lode_position()

def plot_flows(strata, lodes, ax):
    for (i, g1_strats), (_, g2_strats) in pairwise(enumerate(strata)):
        for j, g1_strat in enumerate(g1_strats):
            relative_widths = lodes[i][j]
            for k, g2_strat in enumerate(g2_strats):
                flow_polygon = make_flow_polygon(
                    g1_strat,
                    g2_strat,
                    relative_widths[k][0],
                    relative_widths[k][1],
                    g1_strat.color
                )
                ax.add_patch(flow_polygon)

        # reset lode_position for next round
        reset_strata(g2_strats)

if __name__ == '__main__':
    fig, ax = plt.subplots()
    data = generate_test_data()
    strata, lodes = aggregate_data(
        data,
        'timepoint',
        'nodename',
        'module'
    )
    cycler = it.cycle('rgb')
    colors = [[next(cycler) for i in range(len(group_strata))] for group_strata in strata]
    plot_strata(
        strata,
        colors,
        ax,
        scale = 100
    )
    plot_flows(
        strata,
        lodes,
        ax
    )