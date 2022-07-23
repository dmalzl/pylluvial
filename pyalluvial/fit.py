import numpy as np

def poly_fit_with_straights(y1, y2, x1, x2, resolution, straight_fraction):
    '''
    fits a 4th grade polynomial between x1, y1 and x2, y2
    with leading and trailing straight lines

    :param y1:                  y coordinate of the first point
    :param y2:                  y coordinate of the second point
    :param x1:                  x coordinate of the first point
    :param x2:                  x coordinate of the second point
    :param resolution:          resolution of the interpolated polynomial
    :param straight_fraction:   fraction of the space between x1 and x2 that should be straight lines

    :return:                    numpy.ndarray, np.ndarray containing x and y coordinates of the fitted function
    '''
    # adapted from https://github.com/vinsburg/alluvial_diagram/blob/master/alluvial.py
    straight_length = (x2 - x1) * straight_fraction
    straight1_x = np.linspace(
        x1,
        x1 + straight_length,
        resolution
    )
    straight1_y = np.repeat(y1, resolution)
    straight2_x = np.linspace(
        x2 - straight_length,
        x2,
        resolution
    )
    straight2_y = np.repeat(y2, resolution)

    y = np.array([0, 0.15, 0.5, 0.85, 1])
    y = y * (y2 - y1) + y1
    x = np.linspace(
        x1 + straight_length,
        x2 - straight_length,
        len(y)
    )
    z = np.polyfit(x, y, 4)
    f = np.poly1d(z)

    xs = np.linspace(x[0], x[-1], resolution)
    ys = f(xs)

    xs = np.concatenate([straight1_x, xs, straight2_x])
    ys = np.concatenate([straight1_y, ys, straight2_y])

    return xs, ys

def sigmoid_fit(y1, y2, x1, x2, resolution):
    '''
    fits a sigmoidal curve between x1, y1 and x2, y2
    with leading and trailing straight lines

    :param y1:                  y coordinate of the first point
    :param y2:                  y coordinate of the second point
    :param x1:                  x coordinate of the first point
    :param x2:                  x coordinate of the second point
    :param resolution:          resolution of the interpolated sigmoidal

    :return:                    numpy.ndarray, np.ndarray containing x and y coordinates of the fitted function
    '''
    sigmoid = lambda x: 1/(1 + np.exp(-x))

    xs = np.linspace(-10, 10, resolution)
    ys = sigmoid(xs)

    xs = np.linspace(x1, x2, resolution)
    ys = ys * (y2 - y1) + y1

    return xs, ys