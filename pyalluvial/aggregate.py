from .stratum import Stratum
from .utils import pairwise, groupby
import numpy as np
import pandas as pd
from typing import Any


def get_lodes(
    data: pd.DataFrame,
    x: str,
    alluvium: str,
    stratum: str
) -> list[list[np.ndarray]]:
    """
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
    :param hue:         grouping variable on which to split each stratum

    :return:            nested list of numpy.ndarrays
    """

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


def aggregate_data(
    data: pd.DataFrame,
    x: str,
    alluvium: str,
    stratum: str
) -> tuple[list[list[Stratum]], list[list[np.ndarray]], list[Any], list[list[Any]]]:
    """
    computes the strata and lodes for each categorical column in x

    :param data:        pandas.DataFrame containing data in long format (see generate_test_data)
    :param x:           categorical column on which to split the data along the x axis
    :param alluvium:    column from which to compute lode sizes for each stratum
    :param stratum:     column specifying the strata for each column in x

    :return:            list of lists Stratum objects, lode sizes as list of lists of arrays with
                        l[i][j] = lodesizes relative to strata in i and i + 1
                        see also function `get_lodes` for more context
    """

    strata_by_group, group_labels, strata_groupings = [], [], []
    for group_label, group in groupby(data, x):
        group_labels.append(group_label)
        strata, strat_grouping = [], []
        for label, strat in groupby(group, stratum):
            strata.append(
                Stratum(len(strat) / len(group), 0, 0, label)
            )
            strat_grouping.append(
                strat.grouping.unique()
            )
        strata_by_group.append(strata)
        strata_groupings.append(strat_grouping)

    lodes = get_lodes(
        data,
        x,
        alluvium,
        stratum
    )

    return strata_by_group, lodes, group_labels, strata_groupings
