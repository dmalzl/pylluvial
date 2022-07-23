from .utils import *
from .aggregate import aggregate_data
from .fit import *
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon

def get_flow_path(y1, y2, x1, x2, resolution = 50, straight_fraction = 0.2, fit = 'poly'):
    '''
    compute the flow path between x1, y1 and x2, y2 using either
    a polynomial with leading and trailing straight lines or a sigmoidal

    :param y1:                  y coordinate of the first point
    :param y2:                  y coordinate of the second point
    :param x1:                  x coordinate of the first point
    :param x2:                  x coordinate of the second point
    :param resolution:          resolution of the interpolated function
    :param straight_fraction:   fraction of the space between x1 and x2 that should be straight lines for fit = 'poly'
    :param fit:                 string specifying the function to use for computing the flow path

    :return:                    numpy.ndarray, np.ndarray containing x and y coordinates of the fitted function
    '''
    if fit == 'sigmoid':
        xs, ys = sigmoid_fit(
            y1, y2,
            x1, x2,
            resolution
        )

    elif fit == 'poly':
        xs, ys = poly_fit_with_straights(
            y1, y2,
            x1, x2,
            resolution,
            straight_fraction
        )

    return xs, ys

def make_flow_polygon(g1_strat, g2_strat, g1_rh, g2_rh, color, alpha = 0.5):
    '''
    generates a matplotlib.patches.Polygon object for a given alluvial flow

    :param g1_strat:    origin Stratum object
    :param g2_strat:    destination Stratum object
    :param g1_rh:       flow proportion of origin Stratum
    :param g2_rh:       flow proportion of destination Stratum
    :param color:       color of the generated Polygon
    :param alpha:       opacity of the generated Polygon

    :return:            matplotlib.patches.Polygon for flow between origin and destination Stratum
    '''
    y1_bottom, y1_top = g1_strat.get_flow_ycoords(g1_rh)
    y2_bottom, y2_top = g2_strat.get_flow_ycoords(g2_rh)
    x1 = g1_strat.get_right_bound(0.5)
    x2 = g2_strat.get_left_bound(0.5)
    x_bottom, y_bottom = get_flow_path(y1_bottom, y2_bottom, x1, x2)
    x_top, y_top = get_flow_path(y1_top, y2_top, x1, x2)
    x = np.concatenate([x_top, x_bottom[::-1]])
    y = np.concatenate([y_top, y_bottom[::-1]])
    flow_polygon = Polygon(
        np.array([x, y]).T,
        facecolor = color,
        alpha = alpha
    )

    return flow_polygon

def plot_group_strata(group_strata, x, colors, ax, gapsize = 1, height = 100, width = 0.5, alpha = 0.5):
    '''
    plots stratas for a given group

    :param group_strata:    list of relative strata sizes
    :param x:               position of group column on x axis
    :param colors:          iterable containing colors for each of the strata
    :param ax:              matplotlib.Axes object to add the strata patches to
    :param gapsize:         size of gap between each pair of rectangles
    :param height:          height of the group column
    :param width:           width of the plotted rectangles
    :param alpha:           opacity of plotted rectangles

    :return:                None
    '''
    y = 0
    norm = Normalizer(y, height + gapsize * (len(group_strata) - 1))
    # group_strata[::-1] is necessary to comply to top to bottom order of strata
    for c, stratum in zip(colors, group_strata[::-1]):
        stratum.set_height(height, norm)
        stratum.set_width(width)
        stratum.set_xy(x, y)
        ax.add_patch(
            stratum.get_patch(c, alpha)
        )
        y += stratum.height + gapsize

def plot_strata(strata, strat_colors, stratum_width, ax, height, width):
    '''
    plots strata for each group

    :param strata:          list of list of Stratum objects
    :param strat_colors:    list of lists of colors to use for plotting (has to be same shape as strata)
    :param stratum_width:   width of the Stratum rectangles
    :param ax:              matplotlib.Axes object to add the strata patches to
    :param height:          height of the groups
    :param width:           width of the plot

    :return:                None
    '''

    x = stratum_width / 2
    for group_strata, colors in zip(strata, strat_colors):
        plot_group_strata(
            group_strata,
            x,
            colors,
            ax,
            height = height,
            width = stratum_width
        )
        x += width / len(strata)

    ax.set_xlim(0, x - width / len(strata) + 0.25)
    ax.set_ylim(0, height)

def plot_flows(strata, lodes, ax):
    '''
    plot flows between strata

    :param strata:  list of lists of Stratum objects
    :param lodes:   list of lists of numpy.ndarrays holding the Stratum flow proportions (see also get_lodes)
    :param ax:      matplotlib.Axes object to add the flows to

    :return:        None
    '''
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

def alluvial(x, stratum, alluvium, colors, data = None, ax = None, stratum_width = 1, plot_height = 100, plot_width = 150):
    '''
    generate alluvial plot. x, stratum and alluvium are either strings if data is given or iterables of same length
    containing the data to plot in long format (e.g. [0, 0, 1, 1, 2, 2], [0, 1, 0, 1, 0, 1], [0, 1, 0, 1, 0, 1])

    :param x:               string denoting the column to use for grouping of data if data is given else iterable
    :param stratum:         string denoting the column to use for computing stata heights if data is given else iterable
    :param alluvium:        string denoting the column to use for computing flows between strata if data is given else iterable
    :param colors:          list of list of colors to use for plotting strata and flows has to have the same shape as group and strata
    :param data:            pandas.DataFrame containing data in long format
    :param ax:              matplotlib.Axes object to generate the plot in
    :param stratum_width:   width of the stratum rectangles to plot
    :param plot_height:     height of the generated plot
    :param plot_width:      width of the generated plot

    :return:                matplotlib.Axes if ax is given else matplotlib.Figure, matplotlib.Axes
    '''
    return_fig = False
    if not ax:
        fig, ax = plt.subplots()
        return_fig = True

    if not isinstance(data, pd.DataFrame):
        data = to_dataframe(x, alluvium, stratum)
        x = 'x'
        stratum = 'stratum',
        alluvium = 'alluvium'

    strata, lodes = aggregate_data(
        data,
        x,
        alluvium,
        stratum
    )

    plot_strata(
        strata,
        colors,
        stratum_width,
        ax,
        plot_height,
        plot_width,
    )

    plot_flows(
        strata,
        lodes,
        ax
    )

    ax.set_xticks([])
    ax.set_yticks([])
    for pos in ['top', 'bottom', 'left', 'right']:
        ax.spines[pos].set_visible(False)

    return ax if not return_fig else (fig, ax)