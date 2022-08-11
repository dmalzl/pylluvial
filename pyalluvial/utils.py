import numpy as np
import itertools as it
import pandas as pd
import seaborn as sns
from .stratum import Stratum
from typing import Union, Hashable, Iterable, Optional, Any


class Normalizer:
    def __init__(
        self,
        vmin: float,
        vmax: float
    ):
        self.vmin = vmin
        self.vmax = vmax

    def __call__(
        self,
        val: float,
        scale: float = None
    ) -> float:
        norm = (val - self.vmin) / (self.vmax - self.vmin)
        return norm * scale if scale else norm


def get_color_dict(
    data: pd.DataFrame,
    x: str,
    stratum: str,
    hue: Optional[str],
    sns_palette: str = 'husl'
) -> Union[str, dict[Hashable, dict[Hashable, tuple[float, float, float, float]]]]:
    """
    returns a dict of colors as expected by alluvial

    :param data:            data to plot in wide format
    :param x:               column in data by which to group along x axis
    :param stratum:         column in data by which to group groups along x axis
    :param hue:             column in data indicating the grouping of strata within groups or None
    :param sns_palette:     string indicating the palette to use for colors (see also seaborn)

    :return:                dictionary of colors of the form {group_name: {stratum_name: color}}
    """

    if hue:
        group_sizes = [group.grouping.nunique() * 2 for _, group in groupby(data, x)]

    else:
        group_sizes = [group[stratum].nunique() for _, group in groupby(data, x)]

    palette = sns.color_palette(
        sns_palette,
        max(group_sizes)
    )

    color_dict = {}
    for group_name, strata in groupby(data, x):
        color_dict[group_name] = {}
        for i, (stratum_group_name, stratum_group) in enumerate(groupby(strata, 'grouping')):
            if hue:
                for j, (stratum_name,  _) in enumerate(groupby(stratum_group, stratum)):
                    color_dict[group_name][stratum_name] = palette[2*i + j]

            else:
                color_dict[group_name][stratum_group_name] = palette[i]

    return color_dict


def pairwise(iterable: Iterable) -> list[tuple[Any, Any]]:
    """
    returns successive overlapping pairs taken from the input iterable.
    taken from itertools since this is only available for python>=3.10

    :param iterable:    any iterable container
    :return:            successive overlapping pairs
    """

    a, b = it.tee(iterable)
    next(b, None)
    return list(zip(a, b))


def generate_probabilities(n: int) -> list[float]:
    """
    generates an array of n probabilities with the constraint of sum(probabilities) = 1

    :param n:   number of probabilities in the array
    :return:    list of floats
    """

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


def to_dataframe(
    x: Iterable,
    alluvium: Iterable,
    stratum: Iterable,
    hue: Optional[Iterable] = None
) -> pd.DataFrame:
    """
    converts three iterables of the same length to a pandas.DataFrame
    :param x:
    :param alluvium:
    :param stratum:
    :return:
    """
    keys = ['x', 'alluvium', 'stratum']
    iterables = [x, alluvium, stratum]

    if not isinstance(hue, type(None)):
        keys += ['hue']
        iterables += [hue]

    df = pd.DataFrame(
        {k: v for k, v in zip(keys, iterables)}
    )

    return df


# groupby lambda expression for shorter code
groupby = lambda df, key: df.groupby(key, sort = True)


def reset_strata(strata: list[Stratum]) -> None:
    """
    resets the flow position tracking of all given Stratum objects

    :param strata:  list of Stratum object to reset

    :return:        None
    """
    for stratum in strata:
        stratum.reset_lode_position()


def generate_test_data(
        group_sizes: Union[tuple[int], list[int]] = (3, 5, 4, 6)
) -> pd.DataFrame:
    """
    generates test data for the alluvial plotter

    :param group_sizes:         list or tuple of integers specifying the number of strata per group to generate test data for

    :return: pandas.DataFrame
    """

    nnodes = 1000
    ngroups = len(group_sizes)
    nodenames = list(range(nnodes)) * ngroups
    timepoint = [f't{i}' for i in range(ngroups) for j in range(nnodes)]
    probabilities = [generate_probabilities(i) for i in group_sizes]
    modules, hue = [], []
    for p in probabilities:
        modules.append(
            np.random.choice(range(1, len(p) + 1), size = nnodes, p = p, replace = True)
        )
        phue = np.random.rand()
        hue.append(
            np.random.choice(['s', 'ns'], size = nnodes, p = [phue, 1 - phue])
        )

    modules = np.concatenate(modules)
    hue = np.concatenate(hue)

    df = pd.DataFrame(
        [[a, b, c, d] for a, b, c, d in zip(nodenames, timepoint, modules, hue)],
        columns = [
            'nodename',
            'timepoint',
            'module',
            'signif'
        ]
    )
    return df
